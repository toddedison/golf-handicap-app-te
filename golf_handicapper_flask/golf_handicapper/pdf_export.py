"""
Generates a scorecard PDF for a user.
Requires: pip install reportlab
"""
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_scorecard_pdf(user):
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab is not installed. Run: pip install reportlab")

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=inch, rightMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    green = colors.HexColor('#2d6a4f')

    title_style = ParagraphStyle('title', parent=styles['Heading1'],
                                 textColor=green, fontSize=22, spaceAfter=4)
    sub_style = ParagraphStyle('sub', parent=styles['Normal'],
                               textColor=colors.HexColor('#5a7a68'), fontSize=11, spaceAfter=16)

    story = [
        Paragraph(f"Golf Scorecard — {user.name}", title_style),
        Paragraph(f"Handicap Index: <b>{user.handicap}</b>", sub_style),
        Spacer(1, 0.15 * inch),
    ]

    rounds = user.rounds.all()
    if rounds:
        data = [['Course', 'Date', 'Score', 'Rating', 'Slope', 'Differential']]
        for r in rounds:
            diff = round((r.score - r.rating) * 113 / r.slope, 1)
            data.append([r.course, r.game_date, str(r.score),
                         str(r.rating), str(r.slope), str(diff)])

        t = Table(data, colWidths=[2.2*inch, 1.1*inch, 0.7*inch, 0.75*inch, 0.7*inch, 1*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f9f5')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c8ddd0')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No rounds recorded.", styles['Normal']))

    doc.build(story)
    return buf.getvalue()
