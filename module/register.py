# from flask import Flask, request, render_template, session, redirect, send_file, url_for, flash
# import json
# import io
# import os
# import base64
# from datetime import datetime
# from PIL import Image, ImageChops, ImageStat, ExifTags, ImageDraw, ImageFont
# import requests
# import folium
# from folium.plugins import MarkerCluster, HeatMap, Geocoder
# import pandas as pd

# # Optional: local classifier fallback
# try:
#     import torch
#     import torchvision.transforms as transforms
#     from torchvision import models
#     TORCH_AVAILABLE = True
# except Exception:
#     TORCH_AVAILABLE = False

# # ----------------------------
# # Flask app setup
# # ----------------------------
# app = Flask(__name__)
# app.secret_key = "Pranav@123"

# PLANT_ID_API_KEY = os.environ.get("PLANT_ID_API_KEY", "").strip()

# # ----------------------------
# # User registration / login system
# # ----------------------------
# @app.route('/register', methods=['POST'])
# def register():
#     username = request.form.get('username')
#     password = request.form.get('password')
#     email = request.form.get('email')

#     with open('user.json', 'r') as f:
#         data = json.load(f)

#     data["users"].append({
#         "username": username,
#         "password": password,
#         "email": email
#     })

#     with open('user.json', 'w') as f:
#         json.dump(data, f, indent=4)

#     return render_template('login.html', message="Registration successful! Please log in.")

# @app.route('/')
# def home():
#     return render_template('index2.html')

# @app.route('/login')
# def login():
#     return render_template('login.html')

# def load_users():
#     with open("user.json", "r") as file:
#         data = json.load(file)
#     return data["users"]

# @app.route('/submit', methods=['POST'])
# def submit():
#     username = request.form.get('username')
#     password = request.form.get('password')

#     users = load_users()
#     for user in users:
#         if user["username"] == username and user["password"] == password:
#             print(f"username: {username}, password: {password}")
#             return render_template('index.html', name=username)

#     return "Login failed. Invalid credentials."

# @app.route('/goverment_schemes')
# def goverment_schemes():
#     return render_template('goverment_schemes.html')

# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     return redirect('/')

# @app.route('/live_map_data')
# def live_map_data():
#     return render_template('blue_carbon_registry_satellite_map.html')

# @app.route('/home1')
# def home1():
#     return render_template('index.html')

# @app.route('/calculator')
# def calculator():
#     return render_template('calculator.html')

# @app.route('/upload_data')
# def upload_data():
#     return render_template('upload.html')

# # ----------------------------
# # JSON save helper
# # ----------------------------
# def save_to_json(data, filename="image_scan_result.json"):
#     try:
#         os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
#         try:
#             with open(filename, "r", encoding="utf-8") as f:
#                 existing = json.load(f)
#                 if not isinstance(existing, list):
#                     existing = [existing]
#         except (FileNotFoundError, json.JSONDecodeError):
#             existing = []
#         existing.append(data)
#         with open(filename, "w", encoding="utf-8") as f:
#             json.dump(existing, f, ensure_ascii=False, indent=2)
#     except Exception as e:
#         print(f"[save_to_json] error: {e}")

# # ----------------------------
# # EXIF helpers
# # ----------------------------
# def get_exif(image: Image.Image):
#     exif = {}
#     raw = getattr(image, "_getexif", None)
#     if raw is None: return exif
#     try:
#         info = raw() or {}
#         for tag, value in info.items():
#             name = ExifTags.TAGS.get(tag, tag)
#             exif[name] = value
#         if "GPSInfo" in exif:
#             gps = {}
#             for t, val in exif["GPSInfo"].items():
#                 subname = ExifTags.GPSTAGS.get(t, t)
#                 gps[subname] = val
#             exif["GPSInfo"] = gps
#     except Exception:
#         pass
#     return exif

# def _rational_to_float(r):
#     try:
#         if isinstance(r, tuple) and len(r) == 2:
#             num, den = r
#             return float(num)/float(den) if den else 0.0
#         return float(r)
#     except Exception:
#         return 0.0

# def gps_to_decimal(gps_coords, ref):
#     try:
#         d = _rational_to_float(gps_coords[0])
#         m = _rational_to_float(gps_coords[1])
#         s = _rational_to_float(gps_coords[2])
#         dec = d + m/60.0 + s/3600.0
#         if ref in ("S","W"): dec = -dec
#         return dec
#     except Exception:
#         return None

# def extract_gps_datetime(exif):
#     lat = lon = dt = None
#     if not exif: return lat, lon, dt
#     gps = exif.get("GPSInfo")
#     if gps:
#         lat_v, lat_ref = gps.get("GPSLatitude"), gps.get("GPSLatitudeRef")
#         lon_v, lon_ref = gps.get("GPSLongitude"), gps.get("GPSLongitudeRef")
#         if lat_v and lat_ref and lon_v and lon_ref:
#             lat, lon = gps_to_decimal(lat_v, lat_ref), gps_to_decimal(lon_v, lon_ref)
#     dt = exif.get("DateTimeOriginal") or exif.get("DateTime") or exif.get("DateTimeDigitized")
#     return lat, lon, dt

# # ----------------------------
# # ELA
# # ----------------------------
# def perform_ela(image: Image.Image, quality=90):
#     im = image.convert("RGB")
#     buf = io.BytesIO()
#     im.save(buf, format="JPEG", quality=quality)
#     buf.seek(0)
#     recompressed = Image.open(buf).convert("RGB")
#     ela_image = ImageChops.difference(im, recompressed)
#     extrema = ela_image.getextrema()
#     stat = ImageStat.Stat(ela_image.convert("L"))
#     mean = stat.mean[0] if stat.mean else 0.0
#     max_val = max([e[1] for e in extrema]) if extrema else 0
#     ela_score = mean + (max_val * 0.5)
#     return ela_image, ela_score

# def metadata_checks(exif):
#     flags = []
#     if not exif: return ["No EXIF metadata present."]
#     if "Software" in exif: flags.append(f"Software tag: {exif.get('Software')}")
#     if "Make" not in exif or "Model" not in exif: flags.append("Camera Make/Model missing.")
#     dto, dt = exif.get("DateTimeOriginal"), exif.get("DateTime")
#     if dto and dt and dto != dt: flags.append("DateTimeOriginal != DateTime.")
#     if "GPSInfo" in exif and not (exif.get("DateTime") or exif.get("DateTimeOriginal")):
#         flags.append("GPS present but no DateTime metadata.")
#     return flags

# # ----------------------------
# # Plant.id API (optional)
# # ----------------------------
# def identify_with_plantid(image_bytes):
#     if not PLANT_ID_API_KEY: raise RuntimeError("No Plant.id API key set.")
#     url = "https://api.plant.id/v2/identify"
#     headers = {"Content-Type": "application/json"}
#     b64 = base64.b64encode(image_bytes).decode("utf-8")
#     payload = {
#         "api_key": PLANT_ID_API_KEY,
#         "images": [b64],
#         "modifiers": ["similar_images"],
#         "plant_language": "en",
#         "plant_details": ["common_names","url","name_authority","wiki_description","taxonomy"]
#     }
#     resp = requests.post(url, json=payload, headers=headers, timeout=30)
#     resp.raise_for_status()
#     return resp.json()

# # ----------------------------
# # Local classifier
# # ----------------------------
# model_cache = None
# model_transform = None
# imagenet_labels = None

# def load_local_model_and_labels():
#     global model_cache, model_transform, imagenet_labels
#     if model_cache or not TORCH_AVAILABLE: return
#     model_cache = models.resnet50(weights=models.ResNet50_Weights.DEFAULT) if hasattr(models,"ResNet50_Weights") else models.resnet50(pretrained=True)
#     model_cache.eval()
#     model_transform = transforms.Compose([
#         transforms.Resize(256),
#         transforms.CenterCrop(224),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
#     ])
#     try:
#         here = os.path.dirname(__file__)
#         labfile = os.path.join(here,"imagenet_classes.txt")
#         if os.path.exists(labfile):
#             with open(labfile,"r",encoding="utf-8") as f:
#                 imagenet_labels = [l.strip() for l in f.readlines()]
#     except:
#         imagenet_labels = None

# def identify_local(image: Image.Image):
#     if not TORCH_AVAILABLE: return {"error": "torch not installed"}
#     load_local_model_and_labels()
#     if model_cache is None: return {"error": "model load failed"}
#     inp = model_transform(image.convert("RGB")).unsqueeze(0)
#     with torch.no_grad():
#         out = model_cache(inp)
#         probs = torch.nn.functional.softmax(out[0], dim=0)
#         top5 = torch.topk(probs, 5)
#     preds = []
#     for idx, p in zip(top5.indices.tolist(), top5.values.tolist()):
#         label = imagenet_labels[idx] if imagenet_labels and idx < len(imagenet_labels) else f"imagenet_{idx}"
#         preds.append({"label": label, "score": float(p)})
#     return {"predictions": preds}

# # ----------------------------
# # PDF Generator
# # ----------------------------
# def generate_pdf(report):
#     pdf_img = Image.new("RGB", (595,842), color="white")
#     draw = ImageDraw.Draw(pdf_img)
#     try:
#         font_title = ImageFont.truetype("arial.ttf", 20)
#         font_normal = ImageFont.truetype("arial.ttf", 14)
#     except:
#         font_title = ImageFont.load_default()
#         font_normal = ImageFont.load_default()

#     y = 30
#     draw.text((50,y), "Blue Carbon Image Scan Report", fill="black", font=font_title)
#     y+=30
#     draw.text((50,y), f"File: {report['filename']}", fill="black", font=font_normal); y+=20
#     draw.text((50,y), f"Scanned at: {report['scanned_at']}", fill="black", font=font_normal); y+=20
#     draw.text((50,y), f"GPS: {report.get('gps')}", fill="black", font=font_normal); y+=20
#     draw.text((50,y), f"DateTime: {report.get('datetime')}", fill="black", font=font_normal); y+=20
#     draw.text((50,y), f"ELA Score: {report.get('ela_score')}", fill="black", font=font_normal); y+=20
#     draw.text((50,y), f"Tree Method: {report['tree_identification'].get('method')}", fill="black", font=font_normal); y+=20

#     if report.get("ela_preview"):
#         ela_bytes = io.BytesIO(base64.b64decode(report["ela_preview"]))
#         ela_img = Image.open(ela_bytes)
#         ela_img.thumbnail((200,200))
#         pdf_img.paste(ela_img, (50, y))
#         y+=220

#     pdf_path = "static/scan_report.pdf"
#     os.makedirs("static", exist_ok=True)
#     pdf_img.save(pdf_path, "PDF")
#     return pdf_path

# # ----------------------------
# # Image upload & scan routes
# # ----------------------------
# @app.route("/upload", methods=["POST"])
# def upload():
#     if "file" not in request.files:
#         return "No file uploaded", 400
#     f = request.files["file"]
#     if not f.filename:
#         return "Empty filename", 400
#     filename_input = request.form.get("filename") or f.filename

#     try:
#         img_bytes = f.read()
#         image = Image.open(io.BytesIO(img_bytes))
#     except Exception as e:
#         return f"Could not open image: {e}", 400

#     exif = get_exif(image)
#     lat, lon, dt = extract_gps_datetime(exif)

#     ela_score = ela_b64 = None
#     try:
#         ela_img, ela_score = perform_ela(image, quality=90)
#         buf = io.BytesIO()
#         w = 400
#         h = int(400*ela_img.height/ela_img.width) if ela_img.width else 400
#         ela_img.resize((w,h)).save(buf, format="PNG")
#         ela_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
#     except Exception: pass

#     manipulation_flags = metadata_checks(exif)
#     if ela_score: manipulation_flags.append(f"ELA score: {ela_score:.1f}")

#     tree_identification = {"method": None,"result": None,"note": None}
#     if PLANT_ID_API_KEY:
#         try:
#             tree_identification["method"]="plant.id"
#             tree_identification["result"]=identify_with_plantid(img_bytes)
#         except Exception as e:
#             tree_identification["note"]=f"Plant.id failed: {e}"
#     if tree_identification["result"] is None:
#         tree_identification["method"]="local-imagenet"
#         tree_identification["result"]=identify_local(image)

#     resp = {
#         "filename": filename_input,
#         "gps":{"latitude":float(lat) if lat else None,"longitude":float(lon) if lon else None},
#         "datetime": str(dt) if dt else None,
#         "ela_score": float(ela_score) if ela_score else None,
#         "ela_preview": ela_b64,
#         "manipulation_flags": manipulation_flags,
#         "tree_identification": tree_identification,
#         "scanned_at": datetime.utcnow().isoformat()+"Z",
#         "carbon_credit": "Estimated 5 tons CO2"
#     }

#     save_to_json(resp)
#     pdf_path = generate_pdf(resp)

#     return render_template("report.html", pdf_file=pdf_path)

# # ----------------------------
# # Folium map generation
# # ----------------------------
# def generate_map():
#     projects = [
#         {"project": "Mangrove Restoration - Gujarat", "lat": 21.6417, "lon": 72.2097, "carbon_tons": 1200, "year": 2021, "status": "Verified"},
#         {"project": "Seagrass Plantation - Tamil Nadu", "lat": 10.78, "lon": 79.13, "carbon_tons": 850, "year": 2022, "status": "Pending"},
#         {"project": "Saltmarsh Revival - Sundarbans", "lat": 22.0, "lon": 88.0, "carbon_tons": 2500, "year": 2019, "status": "Verified"},
#         {"project": "Community Plantation - Kerala", "lat": 9.9312, "lon": 76.2673, "carbon_tons": 600, "year": 2023, "status": "Ongoing"},
#         {"project": "Mangrove Belt - Maharashtra", "lat": 18.97, "lon": 72.82, "carbon_tons": 1500, "year": 2020, "status": "Verified"},
#         {"project": "Community Plantation - Aurangabad Satara Parisar", "lat": 19.8773, "lon": 75.3391, "carbon_tons": 900, "year": 2023, "status": "Ongoing"},
#     ]
#     df = pd.DataFrame(projects)

#     m = folium.Map(
#         location=[20.5937, 78.9629],
#         zoom_start=5,
#         tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
#         attr="Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community"
#     )

#     marker_cluster = MarkerCluster(name="Registry Projects").add_to(m)

#     for _, row in df.iterrows():
#         popup_html = f"""
#         <div style="font-size:14px;">
#             <b>{row['project']}</b><br>
#             <b>Carbon Stored:</b> {row['carbon_tons']} tons<br>
#             <b>Year:</b> {row['year']}<br>
#             <b>Status:</b> {row['status']}<br>
#         </div>
#         """
#         folium.CircleMarker(
#             location=[row["lat"], row["lon"]],
#             radius=7 + (row["carbon_tons"]/1000),
#             popup=folium.Popup(popup_html, max_width=300),
#             color="darkgreen" if row["status"] == "Verified" else "orange",
#             fill=True,
#             fill_color="blue",
#             fill_opacity=0.7
#         ).add_to(marker_cluster)

#     heat_data = [[row["lat"], row["lon"], row["carbon_tons"]] for _, row in df.iterrows()]
#     HeatMap(heat_data, name="Carbon Storage Heatmap", radius=30, blur=15, max_zoom=10).add_to(m)

#     folium.TileLayer("CartoDB positron", name="Light Mode").add_to(m)
#     folium.TileLayer("CartoDB dark_matter", name="Dark Mode").add_to(m)
#     Geocoder(collapsed=False, add_marker=True).add_to(m)
#     folium.LayerControl().add_to(m)

#     os.makedirs("templates", exist_ok=True)
#     m.save("templates/blue_carbon_registry_satellite_map.html")
#     print("✅ Satellite map created: open blue_carbon_registry_satellite_map.html")

# # ----------------------------
# # Run app
# # ----------------------------
# if __name__ == "__main__":
#     generate_map()   # build map on startup
# #     app.run(debug=True, port=5000)
# from flask import Flask, request, jsonify, render_template, redirect, url_for
# from datetime import datetime

# app = Flask(__name__)


# ----------------------------
# In-memory projects store
# ----------------------------
# Each project: {id, filename, gps, datetime, ela_score, ela_preview, manipulation_flags,
#                tree_identification, scanned_at, carbon_credit, status}
