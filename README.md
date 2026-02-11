# PDF Generator API

A Python API built with Flask that converts HTML tables to PDF files. Deployable to Vercel as a serverless function.

## Features

- ✅ Convert HTML tables to professionally formatted PDFs
- ✅ RESTful API endpoint
- ✅ Custom styling for better readability
- ✅ Deployable to Vercel
- ✅ Error handling and validation

## Local Development

### Prerequisites

- Python 3.9 or higher
- pip

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Run Locally

```bash
python api/index.py
```

The API will be available at `http://localhost:5000`

## API Usage

### Health Check

**GET** `/`

Response:
```json
{
  "status": "healthy",
  "message": "PDF Generator API is running"
}
```

### Generate PDF

**POST** `/api/generate-pdf`

**Request Body:**
```json
{
  "htmlTable": "<table><tr><td><b>Field</b></td><td>Value</td></tr></table>"
}
```

**Response:**
- Content-Type: `application/pdf`
- Returns PDF file as blob

### Example Request (JavaScript/Fetch)

```javascript
const htmlTable = `<table><tr><td><b>Confidence Score</b></td><td>68</td></tr><tr><td><b>Confidence Level</b></td><td>Medium</td></tr></table>`;

fetch('http://localhost:5000/api/generate-pdf', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ htmlTable })
})
  .then(response => response.blob())
  .then(blob => {
    // Download the PDF
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'report.pdf';
    a.click();
  });
```

### Example Request (Python)

```python
import requests

html_table = """<table><tr><td><b>Confidence Score</b></td><td>68</td></tr></table>"""

response = requests.post(
    'http://localhost:5000/api/generate-pdf',
    json={'htmlTable': html_table}
)

if response.status_code == 200:
    with open('report.pdf', 'wb') as f:
        f.write(response.content)
    print("PDF generated successfully!")
else:
    print(f"Error: {response.json()}")
```

### Example Request (cURL)

```bash
curl -X POST http://localhost:5000/api/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{"htmlTable":"<table><tr><td><b>Test</b></td><td>Value</td></tr></table>"}' \
  --output report.pdf
```

## Deploy to Vercel

### Prerequisites

- [Vercel CLI](https://vercel.com/download) installed
- Vercel account

### Deployment Steps

1. Install Vercel CLI (if not already installed):
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Follow the prompts to deploy your application

5. For production deployment:
```bash
vercel --prod
```

### After Deployment

Your API will be available at: `https://your-project-name.vercel.app`

Use the same endpoints:
- `GET https://your-project-name.vercel.app/`
- `POST https://your-project-name.vercel.app/api/generate-pdf`

## Project Structure

```
PDFGenerator/
├── api/
│   └── index.py          # Main Flask application
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## PDF Styling

The generated PDFs include:
- A4 page size with 2cm margins
- Professional table formatting
- Distinct styling for headers (first column)
- Proper spacing and borders
- Support for preformatted text in cells
- Responsive font sizing

## Error Handling

The API includes comprehensive error handling:
- Missing `htmlTable` field → 400 Bad Request
- Empty HTML content → 400 Bad Request
- PDF generation errors → 500 Internal Server Error

All errors return JSON with error details:
```json
{
  "error": "Error message",
  "details": "Detailed error information"
}
```

## Troubleshooting

### Local Development Issues

If you encounter issues with WeasyPrint:

**Windows:**
- Install GTK3: Download from [GTK for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer)

**macOS:**
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Linux:**
```bash
sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

## License

MIT
"# pdf" 
