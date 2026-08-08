from __future__ import annotations

from pathlib import Path
from io import BytesIO

import qrcode
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Alkhansae_CV 2026.pdf"
PHOTO = ROOT / "WhatsApp Image 2025-06-07 à 12.37.23_bd4a3f26.jpg"
SITE_URL = "https://alkhansae-cv-medecine-travail.hicham1535.chatgpt.site/cv-dr-alkhansae"


def register(name: str, candidates: list[Path]) -> str:
    for p in candidates:
        if p.exists():
            pdfmetrics.registerFont(TTFont(name, str(p)))
            return name
    return "Helvetica"


FONT = register("CvBody", [Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")])
FONT_BOLD = register("CvBold", [Path(r"C:\Windows\Fonts\arialbd.ttf"), Path(r"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")])


def P(text: str, size: float = 9.6, leading: float | None = None, bold: bool = False, color=colors.HexColor("#24313d"), align=TA_LEFT):
    return Paragraph(
        text,
        ParagraphStyle(
            name="tmp",
            fontName=FONT_BOLD if bold else FONT,
            fontSize=size,
            leading=leading or size * 1.35,
            textColor=color,
            alignment=align,
            spaceBefore=0,
            spaceAfter=0,
        ),
    )


def qr_reader(data: str) -> ImageReader:
    qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1d2733", back_color="white").convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def rounded_box(width, title, content, accent="#9a7a4f"):
    tbl = Table([[P(f"<b>{title}</b>", 10.4, bold=True, color=colors.HexColor(accent)), ""]], colWidths=[width - 20, 0])
    tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.white), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#e6ddd0")), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    body = [tbl, Spacer(1, 2 * mm)] + content
    return body


def main():
    doc = BaseDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f1")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])

    story = []

    # Header
    photo = Image(str(PHOTO), width=34 * mm, height=41 * mm) if PHOTO.exists() else Spacer(34 * mm, 41 * mm)
    left = [
        P("Docteur Al Khansae Nafizy", 20, 22, bold=True, color=colors.HexColor("#18222d")),
        Spacer(1, 2 * mm),
        P("Médecin généraliste et médecin de travail diplômée de l’Université de Reims", 10.6, 14, color=colors.HexColor("#5b6672")),
        Spacer(1, 3 * mm),
        P(
            "Profil clinique fondé sur la rigueur, le sens de l’écoute, l’adaptation aux contextes variés et une solide expérience de terrain.",
            9.4,
            13,
        ),
    ]
    contact = Table(
        [
            [P("<b>Adresse</b><br/>Maroc, Salé, Hay Essalam, block 11, secteur 11, Imm 728, Appt 2", 8.8, 11.5)],
            [P("<b>Téléphone</b><br/>0677.72.22.44", 8.8, 11.5)],
            [P("<b>Email</b><br/>alkhansaenafizy@gmail.com", 8.8, 11.5)],
        ],
        colWidths=[62 * mm],
    )
    contact.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7f3ed")), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#e6ddd0")), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))

    header = Table([[photo, left, contact]], colWidths=[38 * mm, 76 * mm, 62 * mm])
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    story += [header, Spacer(1, 6 * mm)]

    # Experience
    exp_content = [
        P("<b>2022</b> - Ouverture de cabinet de médecine générale à Zitoune, Meknès.", 9.3, 12.6),
        Spacer(1, 1.8 * mm),
        P("<b>2020 - 2021</b> - Médecin remplaçante dans plusieurs cabinets à Meknès et dans les régions voisines.", 9.3, 12.6),
        P("Interventions dans plusieurs cabinets médicaux à El Hajeb, Ouisslane et Boufekrane, avec adaptation rapide aux environnements de travail et aux besoins des patients.", 9.2, 12.2),
        Spacer(1, 1.8 * mm),
        P("<b>2018 - 2020</b> - Ouverture de cabinet de médecine générale à Laayayda, Salé.", 9.3, 12.6),
        P("Construction d’une pratique de proximité, avec une approche structurée, empathique et orientée résultats.", 9.2, 12.2),
        Spacer(1, 1.8 * mm),
        P("<b>2014 - 2015</b> - Médecin remplaçante dans plusieurs cabinets médicaux à Salé, Tabriket et El Karia.", 9.2, 12.2),
        P("- Médecin remplaçante à Laâyoune, en cabinet de médecine générale et d’urgences.", 9.2, 12.2),
        P("- Concours de résidanat en spécialité médicale.", 9.2, 12.2),
        Spacer(1, 1.8 * mm),
        P("<b>2015</b> - Médecin formatrice.", 9.2, 12.2),
        P("Animation d’un programme d’éducation à la santé et formation des cadres du centre, dans le cadre d’un partenariat institutionnel.", 9.2, 12.2),
    ]
    story += rounded_box(doc.width, "Expérience professionnelle", exp_content)
    story += [Spacer(1, 4 * mm)]

    # Academic and skills split
    left_block = [
        P("<b>2024 - 2026</b> - Diplôme universitaire de médecine de travail et d’ergonomie, Université de Reims.", 9.2, 12.2),
        Spacer(1, 1.4 * mm),
        P("<b>2007 - 2015</b> - Doctorat en Médecine, Faculté de Médecine et de Pharmacie de Rabat.", 9.2, 12.2),
        P("Mention « Très Honorable » avec « Félicitations du Jury ».", 9.2, 12.2),
        Spacer(1, 1.4 * mm),
        P("<b>Juin 2007</b> - Baccalauréat, option sciences expérimentales.", 9.2, 12.2),
        P("Mention « Très Bien ».", 9.2, 12.2),
    ]
    right_block = [
        P("Français : bilingue", 9.2, 12.2),
        P("Anglais : bon niveau", 9.2, 12.2),
        P("Loisirs : sport, lecture, voyage", 9.2, 12.2),
        Spacer(1, 2 * mm),
        P(
            "Une pratique médicale sobre, fiable et humaine, avec un sens du contact qui sécurise les patients.",
            9.2,
            12.2,
        ),
    ]
    left_tbl = Table([[rounded_box(84 * mm, "Cursus académique", left_block)]], colWidths=[84 * mm])
    right_tbl = Table([[rounded_box(84 * mm, "Langues et points forts", right_block)]], colWidths=[84 * mm])
    for t in (left_tbl, right_tbl):
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    story.append(Table([[left_tbl, right_tbl]], colWidths=[86 * mm, 86 * mm], style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)])))

    story.append(Spacer(1, 5 * mm))

    stage_block = [
        P("Novembre 2013 - Janvier 2014 : Médecin interne, Centre de Santé SIDI FATEH RABAT, service de pédiatrie.", 9.1, 12.0),
        P("Février 2014 - Avril 2014 : Médecin interne, CHP MOULAY YOUSSEF RABAT, chirurgie générale.", 9.1, 12.0),
        P("Mai 2014 - Juillet 2014 : Médecin interne, CHP MOULAY YOUSSEF RABAT, gynécologie.", 9.1, 12.0),
        P("Juillet 2014 - Septembre 2014 : Médecin interne, CHP MOULAY YOUSSEF RABAT, cardiologie.", 9.1, 12.0),
        P("Années 2012 - 2013, 2011 - 2012, 2010 - 2011, 2009 - 2010, 2008 - 2009 : stages hospitaliers et formation clinique.", 9.1, 12.0),
    ]
    story += rounded_box(doc.width, "Stages hospitaliers universitaires", stage_block)

    story.append(Spacer(1, 4 * mm))

    contact_band = Table(
        [
            [
                P(
                    "<b>Un profil sérieux, humain et prêt à rejoindre une structure exigeante.</b><br/>"
                    "Cette présentation sert de support de partage rapide du CV. Le document est téléchargeable immédiatement.",
                    9.2,
                    12.6,
                    color=colors.HexColor("#f7f2eb"),
                ),
                Table(
                    [
                        [P("Télécharger le CV", 9.2, 11.5, bold=True, color=colors.white, align=TA_CENTER)],
                        [P("Alkhansae 2026.pdf", 7.8, 10.2, color=colors.HexColor("#eadcc7"), align=TA_CENTER)],
                    ],
                    colWidths=[48 * mm],
                    style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#b8915e")), ("BOX", (0, 0), (-1, -1), 0, colors.HexColor("#b8915e")), ("ROUNDED", (0, 0), (-1, -1), 12), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]),
                ),
                Table(
                    [
                        [P("Téléphone", 7.8, 10.2, color=colors.HexColor("#d8c5aa"), align=TA_CENTER)],
                        [P("0677.72.22.44", 9.5, 12.0, bold=True, color=colors.white, align=TA_CENTER)],
                        [P("alkhansaenafizy@gmail.com", 8.4, 11.0, color=colors.white, align=TA_CENTER)],
                    ],
                    colWidths=[52 * mm],
                    style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1d2733")), ("BOX", (0, 0), (-1, -1), 0, colors.HexColor("#1d2733")), ("ROUNDED", (0, 0), (-1, -1), 12), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]),
                ),
            ]
        ],
        colWidths=[90 * mm, 50 * mm, 50 * mm],
    )
    contact_band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1d2733")), ("BOX", (0, 0), (-1, -1), 0, colors.HexColor("#1d2733")), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.append(contact_band)

    doc.build(story)


def on_page(canvas, doc):
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#f4efe8"))
    canvas.rect(0, 0, w, h, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#1d2733"))
    canvas.setLineWidth(1.2)
    canvas.roundRect(9 * mm, 9 * mm, w - 18 * mm, h - 18 * mm, 16, stroke=1, fill=0)
    canvas.setStrokeColor(colors.HexColor("#e4dbcf"))
    canvas.line(14 * mm, h - 18 * mm, w - 14 * mm, h - 18 * mm)
    canvas.setFillColor(colors.HexColor("#5b6672"))
    canvas.setFont(FONT, 7.6)
    canvas.drawString(14 * mm, 12 * mm, "Document de présentation personnelle")
    canvas.setFillColor(colors.HexColor("#9a7a4f"))
    canvas.drawRightString(w - 14 * mm, 12 * mm, SITE_URL.replace("https://", ""))
    q = qr_reader(SITE_URL)
    canvas.drawImage(q, w - 28 * mm, 18 * mm, 14 * mm, 14 * mm, mask="auto")
    canvas.restoreState()


if __name__ == "__main__":
    main()
