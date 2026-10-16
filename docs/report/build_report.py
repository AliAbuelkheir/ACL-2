"""Build submission/report.pdf from the figures of the executed notebook.

Run from the repo root:  python docs/report/build_report.py
The text is in report_content.py (team info at the top). Needs reportlab.
"""
import base64
import io
import json
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle, ListFlowable, ListItem)

HERE = os.path.dirname(os.path.abspath(__file__))
nb_path = os.path.join(HERE, '..', '..', 'submission', 'f1-podium-prediction.ipynb')
out_path = os.path.join(HERE, '..', '..', 'submission', 'report.pdf')
with open(nb_path, encoding='utf-8') as f:
    cells = json.load(f)['cells']

PAGE_W = A4[0] - 4 * cm

ss = getSampleStyleSheet()
ACCENT = colors.HexColor('#1f3a5f')
H1 = ParagraphStyle('H1', parent=ss['Heading1'], fontSize=15, textColor=ACCENT, spaceBefore=10, spaceAfter=6)
H2 = ParagraphStyle('H2', parent=ss['Heading2'], fontSize=12, textColor=ACCENT, spaceBefore=8, spaceAfter=4)
BODY = ParagraphStyle('Body', parent=ss['BodyText'], fontSize=9.5, leading=13, spaceAfter=4)
SMALL = ParagraphStyle('Small', parent=BODY, fontSize=8.5, leading=11)
CAP = ParagraphStyle('Cap', parent=BODY, fontSize=8, leading=10, textColor=colors.HexColor('#555555'),
                     alignment=TA_CENTER, spaceAfter=8)
CELL = ParagraphStyle('Cell', parent=BODY, fontSize=8, leading=10, spaceAfter=0)
TITLE = ParagraphStyle('Title', parent=ss['Title'], fontSize=20, textColor=ACCENT)

story = []
fig_no = [0]


def h1(t):
    story.append(Paragraph(t, H1))


def h2(t):
    story.append(Paragraph(t, H2))


def p(t, style=BODY):
    story.append(Paragraph(t, style))


def bullets(items):
    story.append(ListFlowable([ListItem(Paragraph(i, BODY), leftIndent=10) for i in items],
                              bulletType='bullet', start='•', leftIndent=12, bulletFontSize=8))


def table(rows, widths=None, header=True, spans=()):
    data = [[Paragraph(str(c), CELL) for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#b0b0b0')),
             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
             ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3)]
    for a, z in spans:
        style += [('SPAN', a, z), ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e3e9f2'))]
    if header:
        style += [('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3e9f2'))]
    t.setStyle(TableStyle(style))
    story.append(KeepTogether([t, Spacer(1, 6)]))   # never split a table over two pages


def find_png(snippet, k=0):
    hits = [c for c in cells if c['cell_type'] == 'code' and snippet in ''.join(c['source'])]
    assert len(hits) == 1, (snippet, len(hits))
    pngs = [o['data']['image/png'] for o in hits[0].get('outputs', []) if 'data' in o and 'image/png' in o['data']]
    assert len(pngs) > k, ('no image for', snippet)
    return base64.b64decode(pngs[k])


def fig(snippet, caption, width=1.0, k=0):
    raw = find_png(snippet, k)
    w, h = ImageReader(io.BytesIO(raw)).getSize()
    tw = PAGE_W * width
    th = tw * h / w
    if th > 11 * cm:   # keep tall plots from taking a whole page
        th = 11 * cm
        tw = th * w / h
    fig_no[0] += 1
    story.append(KeepTogether([Image(io.BytesIO(raw), width=tw, height=th),
                               Paragraph(f'Figure {fig_no[0]}. {caption}', CAP)]))


def page_num(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f'F1 Podium Prediction - Milestone 1   |   page {doc.page}')
    canvas.restoreState()


exec(open(os.path.join(HERE, 'report_content.py'), encoding='utf-8').read())   # the report text lives in its own file

doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                        bottomMargin=1.8 * cm, title='F1 Podium Prediction - Milestone 1 Report',
                        author='ACL-2 team')
doc.build(story, onFirstPage=page_num, onLaterPages=page_num)
print('figures:', fig_no[0])
