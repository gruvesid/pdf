/**
 * Apex class to call the PDF Generator API
 * Converts HTML tables to PDF files
 */
public class PdfGeneratorCallout {
    
    // API endpoint - update this with your Vercel deployment URL
    private static final String API_ENDPOINT = 'https://your-project-name.vercel.app/api/generate-pdf';
    
    /**
     * Generate PDF from HTML table and save to Salesforce
     * @param htmlTable The HTML table string to convert
     * @param fileName The name for the generated PDF file
     * @param recordId Optional record ID to link the PDF to
     * @return ContentVersion ID of the saved PDF
     */
    public static String generateAndSavePdf(String htmlTable, String fileName, Id recordId) {
        try {
            // Generate PDF
            Blob pdfBlob = generatePdf(htmlTable);
            
            // Save to Salesforce
            String contentVersionId = savePdfToSalesforce(pdfBlob, fileName, recordId);
            
            return contentVersionId;
        } catch (Exception e) {
            System.debug('Error generating and saving PDF: ' + e.getMessage());
            throw new PdfGeneratorException('Failed to generate and save PDF: ' + e.getMessage());
        }
    }
    
    /**
     * Generate PDF from HTML table (returns Blob)
     * @param htmlTable The HTML table string to convert
     * @return Blob containing the PDF data
     */
    public static Blob generatePdf(String htmlTable) {
        try {
            // Create HTTP request
            HttpRequest req = new HttpRequest();
            req.setEndpoint(API_ENDPOINT);
            req.setMethod('POST');
            req.setHeader('Content-Type', 'application/json');
            req.setTimeout(120000); // 120 seconds timeout
            
            // Create JSON body
            Map<String, Object> requestBody = new Map<String, Object>{
                'htmlTable' => htmlTable
            };
            req.setBody(JSON.serialize(requestBody));
            
            // Make callout
            Http http = new Http();
            HttpResponse res = http.send(req);
            
            // Check response
            if (res.getStatusCode() == 200) {
                return res.getBodyAsBlob();
            } else {
                String errorDetails = res.getBody();
                System.debug('API Error: ' + errorDetails);
                throw new PdfGeneratorException('API returned error: ' + res.getStatusCode() + ' - ' + errorDetails);
            }
        } catch (Exception e) {
            System.debug('Error calling PDF Generator API: ' + e.getMessage());
            throw new PdfGeneratorException('Failed to generate PDF: ' + e.getMessage());
        }
    }
    
    /**
     * Save PDF blob to Salesforce as ContentVersion
     * @param pdfBlob The PDF blob data
     * @param fileName The name for the file (without .pdf extension)
     * @param recordId Optional record ID to link the file to
     * @return ContentVersion ID
     */
    public static String savePdfToSalesforce(Blob pdfBlob, String fileName, Id recordId) {
        try {
            // Ensure fileName has .pdf extension
            if (!fileName.endsWithIgnoreCase('.pdf')) {
                fileName += '.pdf';
            }
            
            // Create ContentVersion
            ContentVersion cv = new ContentVersion();
            cv.Title = fileName.removeEnd('.pdf');
            cv.PathOnClient = fileName;
            cv.VersionData = pdfBlob;
            cv.IsMajorVersion = true;
            insert cv;
            
            // Link to record if recordId provided
            if (recordId != null) {
                // Get ContentDocumentId
                cv = [SELECT Id, ContentDocumentId FROM ContentVersion WHERE Id = :cv.Id LIMIT 1];
                
                // Create ContentDocumentLink
                ContentDocumentLink cdl = new ContentDocumentLink();
                cdl.ContentDocumentId = cv.ContentDocumentId;
                cdl.LinkedEntityId = recordId;
                cdl.ShareType = 'V'; // Viewer permission
                cdl.Visibility = 'AllUsers';
                insert cdl;
            }
            
            return cv.Id;
        } catch (Exception e) {
            System.debug('Error saving PDF to Salesforce: ' + e.getMessage());
            throw new PdfGeneratorException('Failed to save PDF: ' + e.getMessage());
        }
    }
    
    /**
     * Future method to generate PDF asynchronously
     * @param htmlTable The HTML table string
     * @param fileName The name for the file
     * @param recordId Optional record ID to link to
     */
    @future(callout=true)
    public static void generatePdfAsync(String htmlTable, String fileName, String recordId) {
        Id recId = String.isNotBlank(recordId) ? Id.valueOf(recordId) : null;
        generateAndSavePdf(htmlTable, fileName, recId);
    }
    
    /**
     * Custom exception class
     */
    public class PdfGeneratorException extends Exception {}
}
