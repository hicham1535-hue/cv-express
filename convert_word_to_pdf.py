from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from PIL import Image as PILImage
import qrcode
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


ROOT = Path(__file__).resolve().parent
DOCX = ROOT / "Alkhansae_CV 2026.docx"
OUT = ROOT / "Alkhansae_CV 2026.pdf"
EXTRACT = ROOT / "_word_extract"
SITE_URL = "https://alkhansae-cv-medecine-travail.hicham1535.chatgpt.site"

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def register_font(name: str, candidates: list[Path]) -> str:
    for path in candidates:
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))
            return name
    return "Helvetica"


FONT = register_font(
    "CvSans",
    [
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path(r"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ],
)
FONT_BOLD = register_font(
    "CvSans-Bold",
    [
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
        Path(r"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ],
)


@dataclass
class Section:
    title: str
    lines: list[str]


def extract_docx():
    EXTRACT.mkdir(exist_ok=True)
    with ZipFile(DOCX) as z:
        # extract media
        media_dir = EXTRACT / "media"
        media_dir.mkdir(exist_ok=True)
        images = []
        for name in z.namelist():
            if name.startswith("word/media/"):
                out = media_dir / Path(name).name
                out.write_bytes(z.read(name))
                images.append(out)

        # parse document paragraphs in order
        root = ET.fromstring(z.read("word/document.xml"))
        paragraphs = []
        for node in root.iter():
            if node.tag.endswith("}p"):
                text = "".join(t.text or "" for t in node.findall(".//w:t", NS)).strip()
                if text:
                    paragraphs.append(text)
        return paragraphs, images


def classify_content(paragraphs: list[str]) -> tuple[list[str], list[Section], list[Section], list[str]]:
    header = paragraphs[:4]

    def take_section(title: str, stop_titles: set[str]) -> Section:
        nonlocal idx
        lines: list[str] = []
        while idx < len(paragraphs):
            item = paragraphs[idx]
            if item in stop_titles and item != title:
                break
            if item == title:
                idx += 1
                continue
            lines.append(item)
            idx += 1
        return Section(title, lines)

    idx = 4
    acad = []
    exp = []
    misc = []

    while idx < len(paragraphs):
        item = paragraphs[idx]
        if item == "Cursus Académique" or item == "Cursus AcadémiqueCursus Académique":
            idx += 1
            acad = [take_section("Cursus Académique", {"Expériences Professionnelles", "Langues et Loisirs"})]
        elif item == "Expériences Professionnelles":
            idx += 1
            exp = [take_section("Expériences Professionnelles", {"STAGES HOSPITALIERS UNIVERSITAIRES :", "Langues et Loisirs"})]
        elif item == "STAGES HOSPITALIERS UNIVERSITAIRES :":
            idx += 1
            misc = [take_section("STAGES HOSPITALIERS UNIVERSITAIRES :", {"Langues et Loisirs"})]
        elif item == "Langues et Loisirs":
            idx += 1
            lang_lines = paragraphs[idx:]
            misc.append(Section("Langues et Loisirs", lang_lines))
            break
        else:
            idx += 1

    return header, acad, exp, misc


def style(name: str, size: int, color=colors.HexColor("#1c2733"), bold=False, center=False, leading=None):
    return ParagraphStyle(
        name=name,
        fontName=FONT_BOLD if bold else FONT,
        fontSize=size,
        leading=leading or int(size * 1.35),
        textColor=color,
        alignment=TA_CENTER if center else 0,
        spaceAfter=0,
        spaceBefore=0,
    )


def bullets(lines: list[str]) -> list[Paragraph]:
    out: list[Paragraph] = []
    for line in lines:
        if not line.strip():
            continue
        out.append(Paragraph(f"• {line}", style("body", 10.2, colors.HexColor("#31414f"), leading=13)))
    return out


def card(title: str, lines: list[str], width: float) -> Table:
    flow = [Paragraph(title, style("section", 11, colors.HexColor("#9a7a4f"), bold=True))]
    flow.append(Spacer(1, 2 * mm))
    for p in bullets(lines):
        flow.append(p)
        flow.append(Spacer(1, 1.2 * mm))
    tbl = Table([[flow]], colWidths=[width])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#e4dbcf")),
                ("ROUNDRECT", (0, 0), (-1, -1), 10, colors.white),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return tbl


def main():
    paragraphs, images = extract_docx()
    header, acad, exp, misc = classify_content(paragraphs)
    photo = images[1] if len(images) > 1 else None

    doc = BaseDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=14 * mm,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="F1")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=draw_page)])

    story = []
    story.append(Spacer(1, 1 * mm))

    # Header block
    header_tbl_data = []
    text_block = [
        Paragraph(header[0], style("name", 20, colors.HexColor("#18222d"), bold=True)),
        Spacer(1, 1.2 * mm),
        Paragraph("Médecin généraliste | Médecin de travail diplômée de l’Université de Reims", style("sub", 10.2, colors.HexColor("#5a6673"))),
        Spacer(1, 2 * mm),
        Paragraph("Profil clinique fondé sur la rigueur, le sens de l’écoute, l’adaptation aux contextes variés et une solide expérience de terrain.", style("body", 9.8, colors.HexColor("#33404d"), leading=13)),
    ]
    contact_lines = header[1:4]
    contact_tbl = Table(
        [[Paragraph(f"<b>Adresse</b><br/>{contact_lines[0]}", style("contact", 9.2, colors.HexColor("#33404d"), leading=12))],
         [Paragraph(f"<b>Téléphone</b><br/>{contact_lines[1]}", style("contact", 9.2, colors.HexColor("#33404d"), leading=12))],
         [Paragraph(f"<b>Email</b><br/>{contact_lines[2]}", style("contact", 9.2, colors.HexColor("#33404d"), leading=12))]],
        colWidths=[62 * mm],
    )
    contact_tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f6f1ea")),
                                     ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#e4dbcf")),
                                     ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e4dbcf")),
                                     ("LEFTPADDING", (0, 0), (-1, -1), 8),
                                     ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                                     ("TOPPADDING", (0, 0), (-1, -1), 6),
                                     ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))

    if photo and photo.exists():
        img = PILImage.open(photo)
        story_photo = Image(str(photo), width=34 * mm, height=41 * mm)
    else:
        story_photo = Spacer(34 * mm, 41 * mm)

    header_tbl = Table(
        [[
            [story_photo],
            text_block,
            contact_tbl,
        ]],
        colWidths=[38 * mm, 74 * mm, 62 * mm],
    )
    header_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 6 * mm))

    # Two-column cards
    acad_text = acad[0].lines if acad else []
    exp_text = exp[0].lines if exp else []
    left_card = card("Cursus académique", acad_text, 84 * mm)
    right_card = card("Expériences professionnelles", exp_text, 84 * mm)
    story.append(Table([[left_card, right_card]], colWidths=[86 * mm, 86 * mm], style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)])))
    story.append(Spacer(1, 5 * mm))

    # Hospital stages and languages
    stage_lines = []
    lang_lines = []
    for sec in misc:
        if sec.title.startswith("STAGES"):
            stage_lines = sec.lines
        elif sec.title == "Langues et Loisirs":
            lang_lines = sec.lines
    story.append(card("Stages hospitaliers universitaires", stage_lines, 170 * mm))
    story.append(Spacer(1, 4 * mm))
    story.append(card("Langues et loisirs", lang_lines, 170 * mm))

    doc.build(story)


def draw_page(canvas, doc):
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#f4efe8"))
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#1d2733"))
    canvas.roundRect(10 * mm, 10 * mm, w - 20 * mm, h - 20 * mm, 18, fill=0, stroke=1)
    canvas.setStrokeColor(colors.HexColor("#e3d8ca"))
    canvas.line(16 * mm, h - 18 * mm, w - 16 * mm, h - 18 * mm)
    canvas.setFillColor(colors.HexColor("#9a7a4f"))
    canvas.setFont(FONT_BOLD, 8.5)
    canvas.drawRightString(w - 16 * mm, 13 * mm, SITE_URL.replace("https://", ""))
    canvas.setFillColor(colors.HexColor("#5b6672"))
    canvas.setFont(FONT, 7.5)
    canvas.drawString(16 * mm, 13 * mm, "Document de présentation personnelle")
    qr = qrcode.QRCode(version=2, box_size=3, border=2)
    qr.add_data(SITE_URL)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#1d2733", back_color="white").convert("RGB")
    qr_reader = ImageReader(qr_img)
    canvas.drawImage(qr_reader, w - 31 * mm, 12 * mm, 16 * mm, 16 * mm, mask="auto")
    canvas.restoreState()


if __name__ == "__main__":
    main()
