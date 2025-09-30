from flask import Flask, request, render_template, session, redirect, send_file, url_for, flash,jsonify
import json
import io
import os
import base64
from datetime import datetime
from PIL import Image, ImageChops, ImageStat, ExifTags, ImageDraw, ImageFont
import requests
import folium
from folium.plugins import MarkerCluster, HeatMap, Geocoder
import pandas as pd
import  sqlite3
import hashlib 
import binascii
from pymongo import MongoClient
from bson import ObjectId
from module.genrate_pdf import generate_pdf

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")   # change URI if needed
db = client["forestdb"]
collection = db["scans"]
# Optional: local classifier fallback
try:
    import torch
    import torchvision.transforms as transforms
    from torchvision import models
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False

# ----------------------------
# Flask app setup
# ----------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "Pranav@123"

PLANT_ID_API_KEY ="clpuAjjtZGF8PgKtvomjlPTbn0PORQr3VsO2zGAg7y6d9d60vB"

# ----------------------------
# User registration / login system
# ----------------------------
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    with open('user.json', 'r') as f:
        data = json.load(f)

    data["users"].append({
        "username": username,
        "password": password,
        "email": email
    })

    with open('user.json', 'w') as f:
        json.dump(data, f, indent=4)

    return render_template('login.html', message="Registration successful! Please log in.")

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/news2')
def news2():
    return render_template('news2.html')
@app.route('/setting')
def setting():
    return  render_template('setting.html')
@app.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')

def load_users():
    with open("user.json", "r") as file:
        data = json.load(file)
    return data["users"]

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form.get('username')
    password = request.form.get('password')
    choices  = request.form.get('choices')
    

    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password and user["choices"] == choices:
            print(f"username: {username}, password: {password}")
            return render_template('admin_home.html', name=username)
        elif user["username"] == username and user["password"] == password:
             print(f"username: {username}, password: {password}")
             return render_template('index.html', name=username)

    return render_template('invalid.html')
@app.route('/goverment_schemes')
def goverment_schemes():
    return render_template('goverment_schemes.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/live_map_data')
def live_map_data():
    return render_template('blue_carbon_registry_satellite_map.html')
@app.route('/ai')
def ai_chatbot():
    return render_template("ai.html")

@app.route('/home1')
def home1():
    return render_template('index.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/upload_data')
def upload_data():
    return render_template('upload.html')

# ----------------------------
# JSON save helper
# ----------------------------
def save_to_json(data, filename="image_scan_result.json"):
    try:
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        try:
            with open(filename, "r", encoding="utf-8") as f:
                existing = json.load(f)
                if not isinstance(existing, list):
                    existing = [existing]
        except (FileNotFoundError, json.JSONDecodeError):
            existing = []
        existing.append(data)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[save_to_json] error: {e}")

# ----------------------------
# EXIF helpers
# ----------------------------
def get_exif(image: Image.Image):
    exif = {}
    raw = getattr(image, "_getexif", None)
    if raw is None: return exif
    try:
        info = raw() or {}
        for tag, value in info.items():
            name = ExifTags.TAGS.get(tag, tag)
            exif[name] = value
        if "GPSInfo" in exif:
            gps = {}
            for t, val in exif["GPSInfo"].items():
                subname = ExifTags.GPSTAGS.get(t, t)
                gps[subname] = val
            exif["GPSInfo"] = gps
    except Exception:
        pass
    return exif

def _rational_to_float(r):
    try:
        if isinstance(r, tuple) and len(r) == 2:
            num, den = r
            return float(num)/float(den) if den else 0.0
        return float(r)
    except Exception:
        return 0.0

def gps_to_decimal(gps_coords, ref):
    try:
        d = _rational_to_float(gps_coords[0])
        m = _rational_to_float(gps_coords[1])
        s = _rational_to_float(gps_coords[2])
        dec = d + m/60.0 + s/3600.0
        if ref in ("S","W"): dec = -dec
        return dec
    except Exception:
        return None

def extract_gps_datetime(exif):
    lat = lon = dt = None
    if not exif: return lat, lon, dt
    gps = exif.get("GPSInfo")
    if gps:
        lat_v, lat_ref = gps.get("GPSLatitude"), gps.get("GPSLatitudeRef")
        lon_v, lon_ref = gps.get("GPSLongitude"), gps.get("GPSLongitudeRef")
        if lat_v and lat_ref and lon_v and lon_ref:
            lat, lon = gps_to_decimal(lat_v, lat_ref), gps_to_decimal(lon_v, lon_ref)
    dt = exif.get("DateTimeOriginal") or exif.get("DateTime") or exif.get("DateTimeDigitized")
    return lat, lon, dt

# ----------------------------
# ELA
# ----------------------------
def perform_ela(image: Image.Image, quality=90):
    im = image.convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    recompressed = Image.open(buf).convert("RGB")
    ela_image = ImageChops.difference(im, recompressed)
    extrema = ela_image.getextrema()
    stat = ImageStat.Stat(ela_image.convert("L"))
    mean = stat.mean[0] if stat.mean else 0.0
    max_val = max([e[1] for e in extrema]) if extrema else 0
    ela_score = mean + (max_val * 0.5)
    return ela_image, ela_score

def metadata_checks(exif):
    flags = []
    if not exif: return ["No EXIF metadata present."]
    if "Software" in exif: flags.append(f"Software tag: {exif.get('Software')}")
    if "Make" not in exif or "Model" not in exif: flags.append("Camera Make/Model missing.")
    dto, dt = exif.get("DateTimeOriginal"), exif.get("DateTime")
    if dto and dt and dto != dt: flags.append("DateTimeOriginal != DateTime.")
    if "GPSInfo" in exif and not (exif.get("DateTime") or exif.get("DateTimeOriginal")):
        flags.append("GPS present but no DateTime metadata.")
    return flags

# ----------------------------
# Plant.id API (optional)
# ----------------------------
def identify_with_plantid(image_bytes):
    if not PLANT_ID_API_KEY: raise RuntimeError("No Plant.id API key set.")
    url = "https://api.plant.id/v2/identify"
    headers = {"Content-Type": "application/json"}
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "api_key": PLANT_ID_API_KEY,
        "images": [b64],
        "modifiers": ["similar_images"],
        "plant_language": "en",
        "plant_details": ["common_names","url","name_authority","wiki_description","taxonomy"]
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()

# ----------------------------
# Local classifier
# ----------------------------
model_cache = None
model_transform = None
imagenet_labels = None

def load_local_model_and_labels():
    global model_cache, model_transform, imagenet_labels
    if model_cache or not TORCH_AVAILABLE: return
    model_cache = models.resnet50(weights=models.ResNet50_Weights.DEFAULT) if hasattr(models,"ResNet50_Weights") else models.resnet50(pretrained=True)
    model_cache.eval()
    model_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
    ])
    try:
        here = os.path.dirname(__file__)
        labfile = os.path.join(here,"imagenet_classes.txt")
        if os.path.exists(labfile):
            with open(labfile,"r",encoding="utf-8") as f:
                imagenet_labels = [l.strip() for l in f.readlines()]
    except:
        imagenet_labels = None

def identify_local(image: Image.Image):
    if not TORCH_AVAILABLE: return {"error": "torch not installed"}
    load_local_model_and_labels()
    if model_cache is None: return {"error": "model load failed"}
    inp = model_transform(image.convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        out = model_cache(inp)
        probs = torch.nn.functional.softmax(out[0], dim=0)
        top5 = torch.topk(probs, 5)
    preds = []
    for idx, p in zip(top5.indices.tolist(), top5.values.tolist()):
        label = imagenet_labels[idx] if imagenet_labels and idx < len(imagenet_labels) else f"imagenet_{idx}"
        preds.append({"label": label, "score": float(p)})
    return {"predictions": preds}

# ----------------------------
# PDF Generator
# ----------------------------


@app.route("/generate-report")
def generate_report():
    # Example report (you would pull this from your DB or API)
    report = {
        "filename": "Plant 1",
        "gps": {"latitude": None, "longitude": None},
        "datetime": None,
        "ela_score": 7.67,
        "ela_preview": "iRU5ErkJggg==",  # truncated base64
        "manipulation_flags": ["No EXIF metadata present.", "ELA score: 7.7"],
        "tree_identification": {
            "method": "plant.id",
            "result": {
                "images": [
                    {"file_name": "plant.jpg", "url": "https://plant.id/media/imgs/dffec19dba22449fa417018c76563070.jpg"}
                ],
                "suggestions": [
                    {
                        "plant_name": "Carica papaya",
                        "probability": 0.7949,
                        "similar_images": [],
                        "plant_details": {
                            "common_names": ["papaya", "Pawpaw"],
                            "scientific_name": "Carica papaya",
                            "taxonomy": {"kingdom": "Plantae", "family": "Caricaceae"},
                            "wiki_description": {"value": "Papaya is a tropical fruit..."}
                        }
                    }
                ]
            }
        },
        "scanned_at": "2025-09-06T12:24:51.423150Z",
        "carbon_credit": "Estimated 5 tons CO2"
    }

    pdf_path = generate_pdf(report)
    return send_file(pdf_path, as_attachment=True)

# ----------------------------
# Image upload & scan routes
# ----------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file uploaded", 400
    f = request.files["file"]
    if not f.filename:
        return "Empty filename", 400
    filename_input = request.form.get("filename") or f.filename
    full_name = request.form.get("full_name") or f.full_name

    try:
        img_bytes = f.read()
        image = Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        return f"Could not open image: {e}", 400

    exif = get_exif(image)
    lat, lon, dt = extract_gps_datetime(exif)

    ela_score = ela_b64 = None
    try:
        ela_img, ela_score = perform_ela(image, quality=90)
        buf = io.BytesIO()
        w = 400
        h = int(400*ela_img.height/ela_img.width) if ela_img.width else 400
        ela_img.resize((w,h)).save(buf, format="PNG")
        ela_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception: pass

    manipulation_flags = metadata_checks(exif)
    if ela_score: manipulation_flags.append(f"ELA score: {ela_score:.1f}")

    tree_identification = {"method": None,"result": None,"note": None}
    if PLANT_ID_API_KEY:
        try:
            tree_identification["method"]="plant.id"
            tree_identification["result"]=identify_with_plantid(img_bytes)
        except Exception as e:
            tree_identification["note"]=f"Plant.id failed: {e}"
    if tree_identification["result"] is None:
        tree_identification["method"]="local-imagenet"
        tree_identification["result"]=identify_local(image)

    resp = {
        "full_name": full_name,
        "filename": filename_input,
        "gps":{"latitude":float(lat) if lat else None,"longitude":float(lon) if lon else None},
        "datetime": str(dt) if dt else None,
        "ela_score": float(ela_score) if ela_score else None,
        "ela_preview": ela_b64,
        "manipulation_flags": manipulation_flags,
        "tree_identification": tree_identification,
        "scanned_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "carbon_credit": "Estimated 5 tons CO2"
    }
    save_to_json(resp)
    collection.insert_one(resp)
    pdf_path = generate_pdf(resp)

    return render_template("report.html", pdf_file=pdf_path)

# ----------------------------
# Folium map generation
# ----------------------------
def generate_map():
    projects = [
        {"project": "Mangrove Restoration - Gujarat", "lat": 21.6417, "lon": 72.2097, "carbon_tons": 1200, "year": 2021, "status": "Verified"},
        {"project": "Seagrass Plantation - Tamil Nadu", "lat": 10.78, "lon": 79.13, "carbon_tons": 850, "year": 2022, "status": "Pending"},
        {"project": "Saltmarsh Revival - Sundarbans", "lat": 22.0, "lon": 88.0, "carbon_tons": 2500, "year": 2019, "status": "Verified"},
        {"project": "Community Plantation - Kerala", "lat": 9.9312, "lon": 76.2673, "carbon_tons": 600, "year": 2023, "status": "Ongoing"},
        {"project": "Mangrove Belt - Maharashtra", "lat": 18.97, "lon": 72.82, "carbon_tons": 1500, "year": 2020, "status": "Verified"},
        {"project": "Community Plantation - Aurangabad Satara Parisar", "lat": 19.8773, "lon": 75.3391, "carbon_tons": 900, "year": 2023, "status": "Ongoing"},
    ]
    df = pd.DataFrame(projects)

    m = folium.Map(
        location=[20.5937, 78.9629],
        zoom_start=5,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community"
    )

    marker_cluster = MarkerCluster(name="Registry Projects").add_to(m)

    for _, row in df.iterrows():
        popup_html = f"""
        <div style="font-size:14px;">
            <b>{row['project']}</b><br>
            <b>Carbon Stored:</b> {row['carbon_tons']} tons<br>
            <b>Year:</b> {row['year']}<br>
            <b>Status:</b> {row['status']}<br>
        </div>
        """
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=7 + (row["carbon_tons"]/1000),
            popup=folium.Popup(popup_html, max_width=300),
            color="darkgreen" if row["status"] == "Verified" else "orange",
            fill=True,
            fill_color="blue",
            fill_opacity=0.7
        ).add_to(marker_cluster)

    heat_data = [[row["lat"], row["lon"], row["carbon_tons"]] for _, row in df.iterrows()]
    HeatMap(heat_data, name="Carbon Storage Heatmap", radius=30, blur=15, max_zoom=10).add_to(m)

    folium.TileLayer("CartoDB positron", name="Light Mode").add_to(m)
    folium.TileLayer("CartoDB dark_matter", name="Dark Mode").add_to(m)
    Geocoder(collapsed=False, add_marker=True).add_to(m)
    folium.LayerControl().add_to(m)

    os.makedirs("templates", exist_ok=True)
    m.save("templates/blue_carbon_registry_satellite_map.html")
    print("✅ Satellite map created: open blue_carbon_registry_satellite_map.html")

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize tables
with db() as con:
    con.executescript("""
    CREATE TABLE IF NOT EXISTS projects(
        project_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        owner TEXT NOT NULL,
        metadata_cid TEXT,
        status TEXT NOT NULL DEFAULT 'Proposed'
    );
    CREATE TABLE IF NOT EXISTS monitoring_events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT NOT NULL,
        ts TEXT NOT NULL,
        plot_id TEXT,
        species TEXT,
        survival_rate REAL,
        dbh_cm REAL,
        height_m REAL,
        lat REAL,
        lon REAL,
        raw_cid TEXT,
        sha256 TEXT
    );
    CREATE TABLE IF NOT EXISTS verifications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT NOT NULL,
        vintage_year INTEGER NOT NULL,
        package_cid TEXT,
        package_sha256 TEXT,
        tco2e REAL,
        accepted INTEGER,
        ts TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS credits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT NOT NULL,
        vintage_year INTEGER NOT NULL,
        method TEXT NOT NULL,
        amount INTEGER NOT NULL,
        beneficiary TEXT,
        retired INTEGER DEFAULT 0
    );
    """)
    con.commit()


# ---------- MongoDB connection ----------
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client["bluecarbon"]

projects_col = mongo_db["projects"]
events_col = mongo_db["monitoring_events"]
verifications_col = mongo_db["verifications"]
credits_col = mongo_db["credits"]
scans_col = mongo_db["scans"]   # for review UI

# ---------- Utility placeholders ----------
def bytes32_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def compute_metrics(area_ha: float, canopy_cover: float) -> float:
    FACTOR = 50.0
    return round(area_ha * canopy_cover * FACTOR, 3)

def generate_map():
    print("Map generated (placeholder)")

# ---------- Pages ----------
@app.route("/admin")
def admin():
    projects = list(projects_col.find().sort("_id", -1))
    issued = sum(c.get("amount", 0) for c in credits_col.find({"retired": 0}))
    retired = sum(c.get("amount", 0) for c in credits_col.find({"retired": 1}))
    return render_template("admin.html", projects=projects, issued=issued, retired=retired)

@app.route("/projects/new")
def new_project():
    return render_template("project_new.html")

@app.route("/projects/create", methods=["POST"])
def create_project():
    name = request.form["name"]
    owner = request.form["owner"]
    metadata_cid = request.form.get("metadata_cid", "")
    project_id = bytes32_hex(owner + name + str(datetime.utcnow().year))
    projects_col.insert_one({
        "project_id": project_id,
        "name": name,
        "owner": owner,
        "metadata_cid": metadata_cid,
        "status": "Proposed"
    })
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/projects/<project_id>")
def project_detail(project_id):
    pr = projects_col.find_one({"project_id": project_id})
    if not pr:
        return "Not Found", 404
    ev = list(events_col.find({"project_id": project_id}).sort("_id", -1))
    vers = list(verifications_col.find({"project_id": project_id}).sort("_id", -1))
    creds = list(credits_col.find({"project_id": project_id}).sort("_id", -1))
    return render_template("project_detail.html", p=pr, events=ev, verifications=vers, credits=creds)

@app.route("/projects/<project_id>/status", methods=["POST"])
def set_status(project_id):
    status = request.form["status"]
    projects_col.update_one({"project_id": project_id}, {"$set": {"status": status}})
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/projects/<project_id>/monitoring/upload", methods=["POST"])
def upload_monitoring(project_id):
    ts = request.form["ts"]
    plot_id = request.form.get("plot_id", "")
    species = request.form.get("species", "")
    survival_rate = float(request.form.get("survival_rate", 0.0))
    dbh_cm = float(request.form.get("dbh_cm", 0.0))
    height_m = float(request.form.get("height_m", 0.0))
    lat = float(request.form.get("lat", 0.0))
    lon = float(request.form.get("lon", 0.0))
    file = request.files.get("file")

    raw_cid = ""
    sha_hex = ""
    if file:
        content = file.read()
        sha_hex = hashlib.sha256(content).hexdigest()
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(data_dir, exist_ok=True)
        path = os.path.join(data_dir, f"upload_{sha_hex[:8]}_{file.filename}")
        with open(path, "wb") as f:
            f.write(content)
        raw_cid = f"local://{os.path.basename(path)}"

    events_col.insert_one({
        "project_id": project_id,
        "ts": ts,
        "plot_id": plot_id,
        "species": species,
        "survival_rate": survival_rate,
        "dbh_cm": dbh_cm,
        "height_m": height_m,
        "lat": lat,
        "lon": lon,
        "raw_cid": raw_cid,
        "sha256": sha_hex
    })
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/projects/<project_id>/verify", methods=["POST"])
def verify_project(project_id):
    monitoringStart = request.form["monitoringStart"]
    monitoringEnd = request.form["monitoringEnd"]
    area_ha = float(request.form.get("area_ha", 1.0))
    canopy_cover = float(request.form.get("canopy_cover", 0.5))
    methodology = request.form.get("methodology", "Mangrove-IND-001")

    tco2e = compute_metrics(area_ha, canopy_cover)
    manifest = {
        "projectId": project_id,
        "monitoringStart": monitoringStart,
        "monitoringEnd": monitoringEnd,
        "area_ha": area_ha,
        "canopy_cover": canopy_cover,
        "methodology": methodology,
        "carbon_tCO2e": tco2e
    }
    data = json.dumps(manifest, separators=(",", ":")).encode()
    sha = hashlib.sha256(data).hexdigest()
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, f"manifest_{sha[:8]}.json")
    with open(path, "wb") as f:
        f.write(data)
    cid = f"local://{os.path.basename(path)}"

    verifications_col.insert_one({
        "project_id": project_id,
        "vintage_year": int(monitoringEnd[:4]),
        "package_cid": cid,
        "package_sha256": sha,
        "tco2e": tco2e,
        "accepted": 1,
        "ts": datetime.utcnow().isoformat()
    })
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/projects/<project_id>/issue", methods=["POST"])
def issue_credits(project_id):
    vintage_year = int(request.form["vintage_year"])
    method = request.form["method"]
    amount = int(request.form["amount"])
    credits_col.insert_one({
        "project_id": project_id,
        "vintage_year": vintage_year,
        "method": method,
        "amount": amount,
        "beneficiary": "",
        "retired": 0
    })
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/credits/<string:credit_id>/retire", methods=["POST"])
def retire_credit(credit_id):
    beneficiary = request.form.get("beneficiary", "")
    purpose = request.form.get("purpose", "")
    credits_col.update_one(
        {"_id": ObjectId(credit_id)},
        {"$set": {"retired": 1, "beneficiary": beneficiary or purpose}}
    )
    credit = credits_col.find_one({"_id": ObjectId(credit_id)})
    pr = credit.get("project_id", "") if credit else ""
    return redirect(url_for("project_detail", project_id=pr))


# ---------- Simple JSON APIs ----------
@app.route("/api/projects")
def api_projects():
    projects = list(projects_col.find().sort("_id", -1))
    for p in projects:
        p["_id"] = str(p["_id"])
    return jsonify({"projects": projects})

@app.route("/api/projects/<project_id>")
def api_project(project_id):
    p = projects_col.find_one({"project_id": project_id})
    ev = list(events_col.find({"project_id": project_id}))
    ver = list(verifications_col.find({"project_id": project_id}))
    cr = list(credits_col.find({"project_id": project_id}))
    for col in [ev, ver, cr]:
        for item in col:
            item["_id"] = str(item["_id"])
    if p:
        p["_id"] = str(p["_id"])
    return jsonify({
        "project": p,
        "events": ev,
        "verifications": ver,
        "credits": cr
    })
    
    
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)
db = client["forestdb"]
col = db["scans"]

# ---- Minimal 1x1 placeholder PNG (base64) if no image available ----
PLACEHOLDER_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMA"
    "ASsJTYQAAAAASUVORK5CYII="
)

def first_or_none(arr, key=None):
    if isinstance(arr, list) and arr:
        return arr[0] if key is None else (arr[0].get(key) if isinstance(arr[0], dict) else None)
    return None

def get_image(doc):
    """
    Choose image priority:
      1) tree_identification.result.images[0].url
      2) ela_preview (base64)
      3) placeholder
    Returns (is_url, value)
    """
    url = (
        doc.get("tree_identification", {})\
           .get("result", {})\
           .get("images", [{}])
    )
    url = first_or_none(url, "url")
    if url:
        return True, url
    if doc.get("ela_preview"):
        return False, doc["ela_preview"]
    return False, PLACEHOLDER_B64

def get_time(doc):
    # Prefer scanned_at -> plant meta_data.datetime -> top-level datetime
    if doc.get("scanned_at"):
        return doc["scanned_at"]
    meta_dt = (
        doc.get("tree_identification", {})
           .get("result", {})
           .get("meta_data", {})
           .get("datetime")
    )
    if meta_dt:
        return meta_dt
    return doc.get("datetime")

def get_coords(doc):
    # Prefer top-level gps -> plant meta_data lat/lon
    gps = doc.get("gps") or {}
    lat = gps.get("latitude")
    lon = gps.get("longitude")
    if lat is not None and lon is not None:
        return lat, lon
    meta = (
        doc.get("tree_identification", {})
           .get("result", {})
           .get("meta_data", {})
    )
    mlat = meta.get("latitude")
    mlon = meta.get("longitude")
    if mlat is not None and mlon is not None:
        return mlat, mlon
    return None, None

def get_plant_details(doc):
    result = doc.get("tree_identification", {}).get("result", {})
    suggestion = first_or_none(result.get("suggestions") or [])
    details = (suggestion or {}).get("plant_details", {}) if isinstance(suggestion, dict) else {}
    sci = details.get("scientific_name")
    common = details.get("common_names") or []
    tax = details.get("taxonomy") or {}
    wiki = (details.get("wiki_description") or {}).get("value")
    url = details.get("url")
    return {
        "scientific_name": sci,
        "common_names": common,
        "taxonomy": tax,
        "wiki": wiki,
        "url": url
    }

def normalize_doc(doc):
    """Normalize & enrich fields for template use (vertical-only data)."""
    doc["_id"] = str(doc["_id"])
    # minimal display fields
    doc["display_name"] = doc.get("filename") or "Unnamed"
    doc["display_time"] = get_time(doc) or "—"
    lat, lon = get_coords(doc)
    doc["display_lat"] = lat
    doc["display_lon"] = lon
    is_url, img = get_image(doc)
    doc["image_is_url"] = is_url
    doc["image_value"] = img
    plant = get_plant_details(doc)
    doc["plant"] = plant
    # status fields for actions
    doc.setdefault("status", "pending")
    doc.setdefault("accepted_at", None)
    return doc

@app.route("/review")
def index():
    docs = list(col.find({"status": {"$ne": "rejected"}}).sort([("_id", -1)]))
    data = [normalize_doc(d) for d in docs]
    return render_template("review.html", data=data, placeholder=PLACEHOLDER_B64)

@app.route("/action", methods=["POST"])
def action():
    payload = request.get_json(force=True)
    _id = payload.get("id")
    act = payload.get("action")

    if not _id or act not in ("accept", "reject"):
        return jsonify(ok=False, error="Invalid payload"), 400

    try:
        oid = ObjectId(_id)
    except Exception:
        return jsonify(ok=False, error="Invalid id"), 400

    if act == "reject":
        res = col.delete_one({"_id": oid})
        if res.deleted_count:
            return jsonify(ok=True)
        return jsonify(ok=False, error="Not found"), 404

    accepted_at = datetime.utcnow().isoformat() + "Z"
    res = col.update_one(
        {"_id": oid},
        {"$set": {"status": "accepted", "accepted_at": accepted_at}}
    )
    if res.matched_count:
        return jsonify(ok=True, accepted_at=accepted_at)
    return jsonify(ok=False, error="Not found"), 404

# ---------- Contact ----------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        full_name = request.form.get("fullName")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        return redirect(url_for("thankyou", name=full_name, subject=subject, message=message))
    return render_template("contact.html")

@app.route("/thankyou")
def thankyou():
    name = request.args.get("name", "Guest")
    subject = request.args.get("subject", "")
    message = request.args.get("message", "")
    return render_template("thankyou.html", name=name, subject=subject, message=message)

if __name__ == "__main__":
    generate_map()
app.run(debug=True, port=5000)