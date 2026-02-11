# Apex Integration Guide

## Setup

### 1. Deploy API to Vercel
First, deploy your API to Vercel:
```bash
vercel --prod
```

Note your deployment URL (e.g., `https://your-project-name.vercel.app`)

### 2. Configure Remote Site Setting in Salesforce
1. Go to **Setup** → **Security** → **Remote Site Settings**
2. Click **New Remote Site**
3. Enter:
   - **Remote Site Name**: `PDF_Generator_API`
   - **Remote Site URL**: `https://your-project-name.vercel.app`
   - Check **Active**
4. Click **Save**

### 3. Update API Endpoint in Apex Class
In `PdfGeneratorCallout.cls`, update line 8:
```apex
private static final String API_ENDPOINT = 'https://your-actual-vercel-url.vercel.app/api/generate-pdf';
```

### 4. Deploy Apex Classes
Deploy both files to your Salesforce org:
- `PdfGeneratorCallout.cls`
- `PdfGeneratorCalloutTest.cls`

## Usage Examples

### Example 1: Generate PDF and Save to Account

```apex
// Your HTML table
String htmlTable = '<table><tr><td><b>Confidence Score</b></td><td>68</td></tr>' +
    '<tr><td><b>Confidence Level</b></td><td>Medium</td></tr>' +
    '<tr><td><b>Recommended Action</b></td><td>Further Investigation Required</td></tr>' +
    '<tr><td><b>Asset Reference</b></td><td>02iKj00001PJJicIAH</td></tr></table>';

// Generate PDF and attach to Account
Id accountId = '001XXXXXXXXXXXXXXX';
String contentVersionId = PdfGeneratorCallout.generateAndSavePdf(
    htmlTable,
    'Asset_Report',
    accountId
);

System.debug('PDF saved with ID: ' + contentVersionId);
```

### Example 2: Generate PDF Blob Only (No Save)

```apex
String htmlTable = '<table><tr><td><b>Field</b></td><td>Value</td></tr></table>';

// Just get the PDF blob
Blob pdfBlob = PdfGeneratorCallout.generatePdf(htmlTable);

// Now you can do whatever you want with the blob
// e.g., send as email attachment, custom storage, etc.
```

### Example 3: Asynchronous PDF Generation

```apex
// For use in triggers or when you need async processing
String htmlTable = '<table><tr><td><b>Test</b></td><td>Data</td></tr></table>';
Id recordId = '001XXXXXXXXXXXXXXX';

// Generate PDF asynchronously
PdfGeneratorCallout.generatePdfAsync(
    htmlTable,
    'Async_Report',
    recordId
);
```

### Example 4: Generate PDF from Dynamic Data

```apex
// Build HTML table from Salesforce data
List<Account> accounts = [SELECT Name, Industry, AnnualRevenue FROM Account LIMIT 10];

String htmlTable = '<table>';
htmlTable += '<tr><td><b>Account Name</b></td><td><b>Industry</b></td><td><b>Revenue</b></td></tr>';

for (Account acc : accounts) {
    htmlTable += '<tr>';
    htmlTable += '<td>' + acc.Name + '</td>';
    htmlTable += '<td>' + (acc.Industry != null ? acc.Industry : 'N/A') + '</td>';
    htmlTable += '<td>' + (acc.AnnualRevenue != null ? String.valueOf(acc.AnnualRevenue) : 'N/A') + '</td>';
    htmlTable += '</tr>';
}

htmlTable += '</table>';

// Generate PDF
String cvId = PdfGeneratorCallout.generateAndSavePdf(
    htmlTable,
    'Accounts_Report',
    null  // Not linked to specific record
);
```

### Example 5: Send PDF via Email

```apex
String htmlTable = '<table><tr><td><b>Report Title</b></td><td>Monthly Summary</td></tr></table>';

// Generate PDF
Blob pdfBlob = PdfGeneratorCallout.generatePdf(htmlTable);

// Send email with PDF attachment
Messaging.SingleEmailMessage email = new Messaging.SingleEmailMessage();
email.setToAddresses(new String[] { 'user@example.com' });
email.setSubject('Your PDF Report');
email.setPlainTextBody('Please find attached your PDF report.');

// Attach PDF
Messaging.EmailFileAttachment attachment = new Messaging.EmailFileAttachment();
attachment.setFileName('report.pdf');
attachment.setBody(pdfBlob);
email.setFileAttachments(new Messaging.EmailFileAttachment[] { attachment });

Messaging.sendEmail(new Messaging.SingleEmailMessage[] { email });
```

### Example 6: Use in Flow/Process Builder

Create an Invocable Method wrapper:

```apex
public class PdfGeneratorInvocable {
    
    @InvocableMethod(label='Generate PDF Report' description='Generate PDF from HTML table')
    public static List<Result> generatePdf(List<Request> requests) {
        List<Result> results = new List<Result>();
        
        for (Request req : requests) {
            Result result = new Result();
            try {
                String cvId = PdfGeneratorCallout.generateAndSavePdf(
                    req.htmlTable,
                    req.fileName,
                    req.recordId
                );
                result.contentVersionId = cvId;
                result.success = true;
            } catch (Exception e) {
                result.errorMessage = e.getMessage();
                result.success = false;
            }
            results.add(result);
        }
        
        return results;
    }
    
    public class Request {
        @InvocableVariable(required=true label='HTML Table')
        public String htmlTable;
        
        @InvocableVariable(required=true label='File Name')
        public String fileName;
        
        @InvocableVariable(label='Record ID')
        public Id recordId;
    }
    
    public class Result {
        @InvocableVariable
        public String contentVersionId;
        
        @InvocableVariable
        public Boolean success;
        
        @InvocableVariable
        public String errorMessage;
    }
}
```

## Error Handling

The class includes comprehensive error handling:

```apex
try {
    String cvId = PdfGeneratorCallout.generateAndSavePdf(htmlTable, 'Report', recordId);
    System.debug('Success: ' + cvId);
} catch (PdfGeneratorCallout.PdfGeneratorException e) {
    System.debug('Error: ' + e.getMessage());
    // Handle error appropriately
}
```

## Governor Limits

- **HTTP Callout Timeout**: 120 seconds
- **Max Callouts per Transaction**: 100
- Use `@future(callout=true)` for async execution if needed
- For bulk operations, consider using Queueable with Continuation

## Best Practices

1. **Always set Remote Site Settings** before making callouts
2. **Use try-catch blocks** for robust error handling
3. **For bulk operations**, use asynchronous methods
4. **Test with mock callouts** before deploying
5. **Monitor API limits** on Vercel (free tier has limits)

## Testing

Run the test class to verify functionality:
```apex
// Execute in Developer Console
Test.startTest();
// Your test code or run PdfGeneratorCalloutTest
Test.stopTest();
```

The test class uses mock HTTP callouts, so it doesn't require actual API access.
