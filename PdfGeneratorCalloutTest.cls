/**
 * Test class for PdfGeneratorCallout
 */
@isTest
private class PdfGeneratorCalloutTest {
    
    @isTest
    static void testGeneratePdfSuccess() {
        // Set up mock response
        Test.setMock(HttpCalloutMock.class, new PdfGeneratorMockSuccess());
        
        Test.startTest();
        String htmlTable = '<table><tr><td><b>Test</b></td><td>Value</td></tr></table>';
        Blob pdfBlob = PdfGeneratorCallout.generatePdf(htmlTable);
        Test.stopTest();
        
        System.assertNotEquals(null, pdfBlob, 'PDF blob should not be null');
        System.assert(pdfBlob.size() > 0, 'PDF blob should have content');
    }
    
    @isTest
    static void testGeneratePdfError() {
        // Set up mock error response
        Test.setMock(HttpCalloutMock.class, new PdfGeneratorMockError());
        
        Test.startTest();
        String htmlTable = '<table><tr><td><b>Test</b></td><td>Value</td></tr></table>';
        Boolean exceptionThrown = false;
        try {
            Blob pdfBlob = PdfGeneratorCallout.generatePdf(htmlTable);
        } catch (PdfGeneratorCallout.PdfGeneratorException e) {
            exceptionThrown = true;
        }
        Test.stopTest();
        
        System.assert(exceptionThrown, 'Exception should be thrown on API error');
    }
    
    @isTest
    static void testGenerateAndSavePdf() {
        // Set up mock response
        Test.setMock(HttpCalloutMock.class, new PdfGeneratorMockSuccess());
        
        // Create test account
        Account acc = new Account(Name = 'Test Account');
        insert acc;
        
        Test.startTest();
        String htmlTable = '<table><tr><td><b>Test</b></td><td>Value</td></tr></table>';
        String cvId = PdfGeneratorCallout.generateAndSavePdf(htmlTable, 'TestReport', acc.Id);
        Test.stopTest();
        
        System.assertNotEquals(null, cvId, 'ContentVersion ID should not be null');
        
        // Verify ContentVersion was created
        ContentVersion cv = [SELECT Id, Title, FileType FROM ContentVersion WHERE Id = :cvId];
        System.assertEquals('TestReport', cv.Title, 'Title should match');
        System.assertEquals('PDF', cv.FileType, 'FileType should be PDF');
        
        // Verify ContentDocumentLink was created
        List<ContentDocumentLink> links = [
            SELECT Id, LinkedEntityId 
            FROM ContentDocumentLink 
            WHERE LinkedEntityId = :acc.Id
        ];
        System.assertEquals(1, links.size(), 'ContentDocumentLink should be created');
    }
    
    @isTest
    static void testSavePdfWithoutRecordId() {
        // Set up mock response
        Test.setMock(HttpCalloutMock.class, new PdfGeneratorMockSuccess());
        
        Test.startTest();
        String htmlTable = '<table><tr><td><b>Test</b></td><td>Value</td></tr></table>';
        String cvId = PdfGeneratorCallout.generateAndSavePdf(htmlTable, 'TestReport', null);
        Test.stopTest();
        
        System.assertNotEquals(null, cvId, 'ContentVersion ID should not be null');
        
        // Verify ContentVersion was created without link
        ContentVersion cv = [SELECT Id, Title FROM ContentVersion WHERE Id = :cvId];
        System.assertEquals('TestReport', cv.Title, 'Title should match');
    }
    
    /**
     * Mock class for successful API response
     */
    private class PdfGeneratorMockSuccess implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/pdf');
            res.setStatusCode(200);
            // Mock PDF content
            res.setBodyAsBlob(Blob.valueOf('Mock PDF Content'));
            return res;
        }
    }
    
    /**
     * Mock class for API error response
     */
    private class PdfGeneratorMockError implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            res.setStatusCode(400);
            res.setBody('{"error": "Missing required field"}');
            return res;
        }
    }
}
