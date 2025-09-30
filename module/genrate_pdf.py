import os
import io
import base64
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def download_image(url, save_path):
    """Download image from URL and save locally."""
    try:
        response = requests.get(url, stream=True, timeout=5)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return save_path
    except Exception:
        return None
    return None


def generate_pdf(report):
    pdf_path = "static/scan_report.pdf"
    os.makedirs("static", exist_ok=True)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    header_style = ParagraphStyle(
        "Header",
        parent=styles["Heading2"],
        spaceAfter=10,
        textColor=colors.HexColor("#2C5F2D")  # dark green
    )
    normal_bold = ParagraphStyle(
        "NormalBold",
        parent=styles["Normal"],
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )

    # Title
    story.append(Paragraph("🌿 Blue Carbon Image Scan Report", styles["Title"]))
    story.append(Spacer(1, 20))

    # Report metadata
    story.append(Paragraph("<b>Report Metadata</b>", header_style))
    metadata = [
        ["Full Name:", report.get("full_name", "N/A")],
        ["Project Name:", report.get("filename", "N/A")],
        ["Scanned At:", report.get("scanned_at", "N/A")],
        ["GPS:", f"{report.get('gps', {}).get('latitude')} , {report.get('gps', {}).get('longitude')}"],
        ["DateTime:", report.get("datetime", "N/A")],
        ["ELA Score:", str(report.get("ela_score", "N/A"))],
        ["Carbon Credit:", report.get("carbon_credit", "N/A")],
        ["Tree Identification Method:", report.get("tree_identification", {}).get("method", "N/A")]
    ]
    table = Table(metadata, hAlign="LEFT", colWidths=[160, 350])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # Manipulation Flags
    if "manipulation_flags" in report:
        story.append(Paragraph("<b>Image Analysis Flags</b>", header_style))
        for flag in report["manipulation_flags"]:
            story.append(Paragraph(f"• {flag}", styles["Normal"]))
        story.append(Spacer(1, 20))

    # Tree Identification Results
    result = report.get("tree_identification", {}).get("result", {})
    if result:
        story.append(Paragraph("<b>🌱 Tree Identification</b>", styles["Heading1"]))
        story.append(Spacer(1, 10))

        # Best match suggestion
        suggestions = result.get("suggestions", [])
        if suggestions:
            top = suggestions[0]
            story.append(Paragraph(
                f"<b>Best Match:</b> {top['plant_name']} ({top['probability']*100:.1f}% confidence)",
                normal_bold
            ))

            # Plant details
            details = top.get("plant_details", {})
            if details:
                if details.get("common_names"):
                    story.append(Paragraph(f"<b>Common Names:</b> {', '.join(details['common_names'])}", styles["Normal"]))
                if details.get("scientific_name"):
                    story.append(Paragraph(f"<b>Scientific Name:</b> {details['scientific_name']}", styles["Normal"]))
                if details.get("taxonomy"):
                    taxo = details["taxonomy"]
                    story.append(Paragraph("<b>Taxonomy:</b>", normal_bold))
                    for k, v in taxo.items():
                        story.append(Paragraph(f"• {k}: {v}", styles["Normal"]))
                if details.get("wiki_description"):
                    story.append(Spacer(1, 10))
                    story.append(Paragraph("<b>Description:</b>", normal_bold))
                    story.append(Paragraph(details["wiki_description"].get("value", ""), styles["Normal"]))

            story.append(Spacer(1, 15))

            # Similar images
            sim_images = top.get("similar_images", [])
            if sim_images:
                story.append(Paragraph("<b>Similar Images</b>", header_style))
                img_row = []
                for sim in sim_images[:3]:
                    img_path = f"static/{sim['id']}.jpg"
                    if download_image(sim["url_small"], img_path):
                        img_row.append(Image(img_path, width=180, height=180))
                if img_row:
                    sim_table = Table([img_row], hAlign="LEFT")
                    story.append(sim_table)
                story.append(Spacer(1, 15))

    # Original uploaded image
    images = result.get("images", [])
    if images:
        story.append(Paragraph("<b>Uploaded Image</b>", header_style))
        img_url = images[0].get("url")
        if img_url:
            img_path = "static/uploaded.jpg"
            if download_image(img_url, img_path):
                story.append(Image(img_path, width=250, height=250))
                story.append(Spacer(1, 20))

    # Signature area
    story.append(Spacer(1, 40))
    story.append(Paragraph("<b>Authorized Signature:</b>", normal_bold))
    story.append(Spacer(1, 50))
    story.append(Paragraph("__________________________", styles["Normal"]))
    story.append(Paragraph("Blue Carbon Authority", styles["Normal"]))

    # Build PDF (single page, good design)
    doc.build(story)
    return pdf_path
