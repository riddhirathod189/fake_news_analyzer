from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import textwrap

def generate_pdf(report_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a365d'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2d3748'),
        fontName='Helvetica'
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#1a365d'),
        fontName='Helvetica-Bold'
    )
    
    content_style = ParagraphStyle(
        'ContentText',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Build story
    story = []
    
    # Header with logo and title
    story.append(Paragraph("TruthLens", title_style))
    story.append(Paragraph("AI-Powered News Verification & Analysis Report", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Report metadata
    current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"<b>Report Generated:</b> {current_date}", content_style))
    story.append(Spacer(1, 30))
    
    # Classification Result (Most Important)
    classification = report_data.get('Classification', 'Unknown')
    confidence = report_data.get('Confidence', 0)
    
    if classification.lower() == 'real':
        classification_color = colors.HexColor('#38a169')
        classification_text = "VERIFIED AUTHENTIC NEWS"
        classification_desc = "Our AI analysis indicates this content is likely legitimate journalism."
    else:
        classification_color = colors.HexColor('#e53e3e')
        classification_text = "POTENTIAL MISINFORMATION DETECTED"
        classification_desc = "This content exhibits patterns commonly found in fake news."
    
    # Classification banner
    classification_style = ParagraphStyle(
        'Classification',
        parent=styles['Normal'],
        fontSize=16,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=colors.white,
        backColor=classification_color,
        borderPadding=15,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph(classification_text, classification_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(classification_desc, content_style))
    story.append(Spacer(1, 30))
    
    # Analysis Summary Table
    story.append(Paragraph("Analysis Summary", section_style))
    
    # Create summary data
    summary_data = [
        ['Metric', 'Value', 'Description'],
        ['Classification', classification.title(), 'AI prediction result'],
        ['Confidence Level', f"{float(confidence):.1f}%", 'Algorithm certainty'],
        ['Readability Score', f"{float(report_data.get('Readability (Flesch Score)', 0)):.1f}", 'Reading difficulty level'],
        ['Sentiment', report_data.get('Sentiment', 'Unknown').title(), 'Overall emotional tone']
    ]
    
    # Create table
    summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Article Summary
    summary_text = report_data.get('Summary', 'No summary available.')
    story.append(Paragraph("AI-Generated Summary", section_style))
    
    # Wrap long summary text
    wrapped_summary = textwrap.fill(summary_text, width=80)
    story.append(Paragraph(wrapped_summary, content_style))
    story.append(Spacer(1, 30))
    
    # Original Article (if available and not too long)
    original_article = report_data.get('Original Article', '')
    if original_article and len(original_article) > 50:
        story.append(Paragraph("Original Article Content", section_style))
        
        # Limit article length for PDF
        if len(original_article) > 2000:
            article_preview = original_article[:2000] + "... [Content truncated for PDF report]"
        else:
            article_preview = original_article
        
        # Wrap the article text
        wrapped_article = textwrap.fill(article_preview, width=80)
        story.append(Paragraph(wrapped_article, content_style))
        story.append(Spacer(1, 30))
    
    story.append(Spacer(1, 40))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4a5568'),
        fontName='Helvetica'
    )
    
    story.append(Paragraph("━" * 60, footer_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("TruthLens - Combating Misinformation with AI Technology", footer_style))
    story.append(Paragraph("This report was generated using advanced machine learning and natural language processing.", footer_style))
    story.append(Paragraph(f"© 2024 TruthLens. Report ID: TL-{datetime.now().strftime('%Y%m%d%H%M%S')}", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def add_page_number(canvas, doc):
    """Add page numbers to the PDF"""
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.drawRightString(letter[0] - 72, 30, text)