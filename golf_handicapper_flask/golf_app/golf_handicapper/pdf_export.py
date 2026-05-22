"""ReportLab replacement for the Rails ScorecardPdf Prawn class."""
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


def generate_scorecard_pdf(user):
    if not AVAILABLE:
        raise RuntimeError('reportlab is not installed – run: pip install reportlab')

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=inch, rightMargin=inch,
                            topMargin=inch, bottomMargin=inch)

    styles = getSampleStyleSheet()
    green  = colors.HexColor('#2d6a4f')
    h1     = ParagraphStyle('h1', parent=styles['Heading1'],
                            textColor=green, fontSize=20, spaceAfter=4)
    sub    = ParagraphStyle('sub', parent=styles['Normal'],
                            textColor=colors.HexColor('#5a7a68'), fontSize=11, spaceAfter=14)

    story = [
        Paragraph('The Golf Handicapper', h1),
        Paragraph(f'Scorecard for <b>{user.name}</b>', sub),
        Paragraph(f'Handicap Index: <b>{user.handicap}</b>', sub),
        Spacer(1, 0.1 * inch),
    ]

    rounds = user.rounds.all()
    if rounds:
        data = [['Course', 'Date', 'Score', 'Rating', 'Slope', 'Differential']]
        for r in rounds:
            data.append([r.course, r.game_date, str(r.score),
                         str(r.rating), str(r.slope), str(r.differential())])

        t = Table(data, colWidths=[2.1*inch, 1.1*inch, 0.7*inch, 0.75*inch, 0.7*inch, 1.05*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1,  0), green),
            ('TEXTCOLOR',    (0, 0), (-1,  0), colors.white),
            ('FONTNAME',     (0, 0), (-1,  0), 'Helvetica-Bold'),
            ('FONTSIZE',     (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS',(0, 1),(-1,-1), [colors.white, colors.HexColor('#f3f9f5')]),
            ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor('#c8ddd0')),
            ('TOPPADDING',   (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
        ]))
        story.append(t)
    else:
        story.append(Paragraph('No rounds recorded yet.', styles['Normal']))

    doc.build(story)
    return buf.getvalue()
