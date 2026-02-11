from flask import Flask, request, send_file, jsonify
from io import BytesIO
from xhtml2pdf import pisa
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Custom CSS for better PDF formatting
PDF_STYLES = """
    @page {
        size: A4;
        margin: 2cm;
    }
    
    body {
        font-family: Arial, Helvetica, sans-serif;
        font-size: 11pt;
        line-height: 1.4;
        color: #333;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background-color: white;
    }
    
    td {
        padding: 12px 15px;
        border: 1px solid #ddd;
        vertical-align: top;
    }
    
    td:first-child {
        background-color: #f8f9fa;
        font-weight: bold;
        width: 30%;
        color: #2c3e50;
    }
    
    td:last-child {
        width: 70%;
    }
    
    b {
        color: #2c3e50;
    }
    
    pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
        line-height: 1.5;
        margin: 0;
    }
"""

def create_html_document(html_table):
    """Wrap the HTML table in a complete HTML document with styling"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Asset Report</title>
        <style>
            {PDF_STYLES}
        </style>
    </head>
    <body>
        {html_table}
    </body>
    </html>
    """

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
        
        # Create complete HTML document
        full_html = create_html_document(html_table)
        
        # Generate PDF
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(
            src=full_html,
            dest=pdf_buffer,
            encoding='UTF-8'
        )
        
        if pisa_status.err:
            return jsonify({
                "error": "Failed to generate PDF",
                "details": "PDF generation encountered errors"
            }), 500
        
        pdf_buffer.seek(0)
        
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

# Vercel requires the app to be exported
def handler(request):
    """Vercel serverless function handler"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    # For local development
    app.run(debug=True, port=5000)
