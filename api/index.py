from flask import Flask, request, send_file, jsonify
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from html.parser import HTMLParser
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class HTMLTableParser(HTMLParser):
    """Parse HTML table into structured data"""
    def __init__(self):
        super().__init__()
        self.table_data = []
        self.current_row = []
        self.current_cell = []
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.is_bold = False
        self.in_pre = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr':
            self.in_row = True
            self.current_row = []
        elif tag == 'td':
            self.in_cell = True
            self.current_cell = []
        elif tag == 'b':
            self.is_bold = True
        elif tag == 'pre':
            self.in_pre = True
            
    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        elif tag == 'tr':
            self.in_row = False
            if self.current_row:
                self.table_data.append(self.current_row)
        elif tag == 'td':
            self.in_cell = False
            cell_text = ''.join(self.current_cell).strip()
            self.current_row.append({
                'text': cell_text,
                'is_bold': self.is_bold
            })
            self.is_bold = False
        elif tag == 'b':
            self.is_bold = False
        elif tag == 'pre':
            self.in_pre = False
            
    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)

def create_pdf_from_table(html_table):
    """Create PDF from HTML table using ReportLab"""
    # Parse HTML table
    parser = HTMLTableParser()
    parser.feed(html_table)
    
    if not parser.table_data:
        raise ValueError("No table data found in HTML")
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        spaceAfter=6
    )
    
    # Convert parsed data to ReportLab table format
    pdf_table_data = []
    for row in parser.table_data:
        pdf_row = []
        for cell in row:
            if cell['is_bold']:
                # Use header style for bold cells
                para = Paragraph(cell['text'], header_style)
            else:
                # Use normal style
                para = Paragraph(cell['text'], normal_style)
            pdf_row.append(para)
        pdf_table_data.append(pdf_row)
    
    # Create table
    table = Table(pdf_table_data, colWidths=[6*cm, 11*cm])
    
    # Apply table style
    table.setStyle(TableStyle([
        # Background for first column (headers)
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd')),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        
        # Vertical alignment
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    # Build PDF
    elements = [table]
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "PDF Generator API is running",
        "endpoints": {
            "/api/generate-pdf": "POST - Generate PDF from HTML table"
        }
    }), 200

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from HTML table
    
    Request body:
    {
        "htmlTable": "<table>...</table>"
    }
    
    Returns: PDF file as blob
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'htmlTable' not in data:
            return jsonify({
                "error": "Missing required field 'htmlTable' in request body"
            }), 400
        
        html_table = data['htmlTable']
        
        if not html_table or not html_table.strip():
            return jsonify({
                "error": "htmlTable cannot be empty"
            }), 400
        
        # Generate PDF
        pdf_buffer = create_pdf_from_table(html_table)
        
        # Return PDF as blob
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='report.pdf'
        )
    
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        return jsonify({
            "error": "Failed to generate PDF",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    # For local development
    app.run(debug=True, port=5000)
