# Vercel Deployment Guide

## ✅ Fixed: No More Cairo Dependency Errors!

The API now uses **ReportLab**, a pure Python library with **zero system dependencies**. This means it will deploy successfully on Vercel without any Cairo/GTK errors.

## Quick Deployment Steps

### 1. Install Vercel CLI (if not already installed)
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy
From the project directory:
```bash
cd "c:\Users\SiddhrajsinhAtodaria\OneDrive - Gruve AI\Desktop\2026\PDFGenerator"
vercel
```

Follow the prompts:
- **Set up and deploy?** Y
- **Which scope?** Choose your account
- **Link to existing project?** N
- **Project name?** pdf-generator (or your choice)
- **Directory?** ./
- **Override settings?** N

### 4. Deploy to Production
```bash
vercel --prod
```

## After Deployment

You'll get URLs like:
- Preview: `https://pdf-generator-xxxxx.vercel.app`
- Production: `https://pdf-generator.vercel.app`

## Update Apex Class

After deployment, update your Apex class with the production URL:

1. Open `PdfGeneratorCallout.cls`
2. Update line 8:
```apex
private static final String API_ENDPOINT = 'https://your-project-name.vercel.app/api/generate-pdf';
```

3. In Salesforce, go to **Setup → Remote Site Settings**
4. Add new remote site:
   - Name: `PDF_Generator_API`
   - URL: `https://your-project-name.vercel.app`
   - Active: ✓

## Test Your Deployment

### Using cURL
```bash
curl -X POST https://your-project-name.vercel.app/api/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{"htmlTable":"<table><tr><td><b>Test</b></td><td>Success</td></tr></table>"}' \
  --output test.pdf
```

### Using Python
```python
import requests

response = requests.post(
    'https://your-project-name.vercel.app/api/generate-pdf',
    json={'htmlTable': '<table><tr><td><b>Test</b></td><td>Success</td></tr></table>'}
)

with open('test.pdf', 'wb') as f:
    f.write(response.content)
```

## Troubleshooting

### Build Fails
- Check `vercel.json` is present
- Verify `requirements.txt` has correct dependencies
- Check logs with `vercel logs`

### Function Timeout
- Vercel free tier has 10s timeout for serverless functions
- Hobby plan has 60s timeout
- If needed, upgrade plan or optimize PDF generation

### CORS Issues
If calling from browser, add CORS support:
```python
# In api/index.py
from flask_cors import CORS
CORS(app)
```

And add to `requirements.txt`:
```
Flask-CORS==4.0.0
```

## What's Deployed

```
Your Vercel Function:
├── Runtime: Python 3.9+
├── Region: Automatic (edge network)
├── Memory: 1024 MB (default)
├── Timeout: 10s (free), 60s (hobby)
└── Dependencies: Flask, ReportLab, html5lib
```

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Get your production URL
3. ✅ Update Apex class with URL
4. ✅ Configure Remote Site Settings in Salesforce
5. ✅ Test from Salesforce

That's it! Your PDF Generator API is live! 🚀
