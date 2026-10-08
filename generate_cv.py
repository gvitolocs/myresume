#!/usr/bin/env python3
"""Generate a one-page CV from resume.json using ReportLab.

    python generate_cv.py
    python generate_cv.py --language en --output-dir output/pdf

The PDFs use searchable text and clickable contact/project links. ReportLab's
bundled fonts require no OS-specific font files or browser/LaTeX installation.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
INK = colors.HexColor("#17212C")
MUTED = colors.HexColor("#526170")
ACCENT = colors.HexColor("#176B75")
RULE = colors.HexColor("#C9D6DB")
MARGIN = 35
WIDTH = A4[0] - 2 * MARGIN - 12  # Platypus frame has 6 pt padding per side.
FONT_DIR = Path(reportlab.__file__).resolve().parent / "fonts"
pdfmetrics.registerFont(TTFont("CVSans", str(FONT_DIR / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("CVSans-Bold", str(FONT_DIR / "VeraBd.ttf")))
pdfmetrics.registerFontFamily("CVSans", normal="CVSans", bold="CVSans-Bold")


class OnePageCanvas(canvas.Canvas):
    """Fail before publishing an overflowing CV instead of shrinking its text."""

    def showPage(self):
        if self.getPageNumber() > 1:
            raise ValueError(
                "CV exceeds one A4 page. Shorten resume.json or adjust the layout."
            )
        super().showPage()


def styles():
    defaults = dict(fontName="CVSans", textColor=INK)
    def style(name, **kwargs):
        return ParagraphStyle(name, **{**defaults, **kwargs})
    return {
        "name": style("name", fontName="CVSans-Bold", fontSize=25, leading=29),
        "headline": style("headline", fontSize=9.1, leading=12.2, textColor=ACCENT),
        "contact": style("contact", fontSize=9, leading=12, textColor=MUTED),
        "body": style("body", fontSize=9.7, leading=12.6),
        "section": style("section", fontName="CVSans-Bold", fontSize=9.5, leading=12, textColor=ACCENT, spaceBefore=9, spaceAfter=4),
        "role": style("role", fontName="CVSans-Bold", fontSize=10.1, leading=12.2),
        "date": style("date", fontSize=8.7, leading=12.2, alignment=TA_RIGHT, textColor=MUTED),
        "org": style("org", fontSize=9.1, leading=11.6, textColor=MUTED),
        "bullet": style("bullet", fontSize=9.7, leading=12.6, leftIndent=9, firstLineIndent=0, bulletIndent=0, bulletFontName="CVSans", bulletFontSize=9.7, spaceBefore=2.2),
        "small": style("small", fontSize=9.1, leading=11.8),
    }


def link(label, url):
    return f'<a href="{escape(url, {chr(34): "&quot;"})}" color="#176B75">{escape(label)}</a>'


def row(title, period, style):
    table = Table(
        [[Paragraph(escape(title), style["role"]), Paragraph(escape(period), style["date"])]],
        colWidths=[WIDTH - 128, 128],
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


def make_story(contact, cv):
    s = styles()
    story = [
        Paragraph(escape(contact["name"]), s["name"]),
        Spacer(1, 3),
        Paragraph(escape(cv["headline"]), s["headline"]),
        Spacer(1, 3),
        Paragraph(
            f'{escape(contact["location"])} &nbsp; | &nbsp; {escape(contact["phone"])}'
            f' &nbsp; | &nbsp; {link(contact["email"], "mailto:" + contact["email"])}',
            s["contact"],
        ),
        Paragraph(" &nbsp; | &nbsp; ".join(link(item["label"], item["url"]) for item in contact["links"]), s["contact"]),
        Spacer(1, 9),
        HRFlowable(width="100%", thickness=0.7, color=RULE),
        Spacer(1, 8),
        Paragraph(cv["profile"], s["body"]),
        Paragraph(cv["skills_title"], s["section"]),
    ]
    for skill in cv["skills"]:
        story.append(Paragraph(f'<b>{escape(skill["label"])}:</b> {escape(skill["text"])}', s["small"]))
    story.append(Paragraph(cv["experience_title"], s["section"]))
    for i, job in enumerate(cv["experience"]):
        if i:
            story.append(Spacer(1, 6))
        story.append(KeepTogether([
            row(job["title"], job["period"], s),
            Paragraph(escape(job["organization"]), s["org"]),
            Paragraph(job["bullets"][0], s["bullet"], bulletText="•"),
        ]))
        for bullet in job["bullets"][1:]:
            story.append(Paragraph(bullet, s["bullet"], bulletText="•"))
    story.append(Paragraph(cv["education_title"], s["section"]))
    for i, item in enumerate(cv["education"]):
        if i:
            story.append(Spacer(1, 4))
        story.append(KeepTogether([
            row(item["title"], item["period"], s),
            Paragraph(escape(item["organization"]) + " · " + escape(item["detail"]), s["small"]),
        ]))
    story.append(Paragraph(cv["additional_title"], s["section"]))
    for text in cv["additional"]:
        story.append(Paragraph(text, s["small"]))
    return story


def generate(data, language, output_dir):
    cv = data["languages"][language]
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / cv["filename"]
    with tempfile.TemporaryDirectory(prefix="cv-generator-") as scratch:
        draft = Path(scratch) / target.name
        doc = SimpleDocTemplate(
            str(draft), pagesize=A4,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=31, bottomMargin=30,
            title=f'{data["contact"]["name"]} - CV ({language.upper()})',
            author=data["contact"]["name"],
            subject=cv["headline"],
            pageCompression=1,
        )
        doc.build(make_story(data["contact"], cv), canvasmaker=OnePageCanvas)
        target.write_bytes(draft.read_bytes())
    print(f"Generated {target}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "resume.json")
    parser.add_argument("--language", choices=("en", "da", "all"), default="all")
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    languages = ("en", "da") if args.language == "all" else (args.language,)
    for language in languages:
        generate(data, language, args.output_dir)


if __name__ == "__main__":
    main()
