"""
Test script for the PDF Generator API
"""
import requests
import json

# Test HTML table (your example)
html_table = """<table><tr><td><b>Confidence Score</b></td><td>68</td></tr><tr><td><b>Confidence Level</b></td><td>Medium</td></tr><tr><td><b>Recommended Action</b></td><td>Further Investigation Required</td></tr><tr><td><b>Asset Reference</b></td><td>02iKj00001PJJicIAH</td></tr><tr><td><b>Condition Summary</b></td><td>The asset has registered multiple claim items related to regulator performance, progressing from intermittent issues and fluctuation to complete failure and wiring shorts over a period of approximately two months.</td></tr><tr><td><b>Risk Assessment</b></td><td>The evidence documents a clear progression of a fault related to a component identified as a 'regulator'. The fault escalates from intermittent behavior to degradation and culminates in a complete operational failure and a wiring short. The operational risk is tied to the loss of function of this specific component.</td></tr><tr><td><b>Supporting Evidence</b></td><td><pre>• Claim Item CI-PUNE-002-A described an 'intermittent delay' with the regulator. • Claim Item CI-PUNE-002-B described 'performance fluctuation' with the regulator. • Claim Item CI-PUNE-003-A noted 'degradation under load' of the regulator. • Claim Item CI-PUNE-004-A cited 'regulator motor response failure'. • Claim Item CI-PUNE-005-A documented a 'Complete regulator failure under operation'. • Claim Item CI-PUNE-005-B documented a 'Regulator wiring short detected'. • A Work Order (00000276) has been created with a suggested maintenance date of 2026-02-10.</pre></td></tr></table>"""

def test_health_check(base_url):
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}\n")
        return False

def test_generate_pdf(base_url, html_input, output_filename="test_report.pdf"):
    """Test the PDF generation endpoint"""
    print("Testing PDF generation endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/generate-pdf",
            headers={"Content-Type": "application/json"},
            json={"htmlTable": html_input}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Save the PDF
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ PDF generated successfully! Saved as '{output_filename}'")
            print(f"File size: {len(response.content)} bytes\n")
            return True
        else:
            print(f"❌ Error: {response.json()}\n")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False

def test_error_cases(base_url):
    """Test error handling"""
    print("Testing error handling...")
    
    # Test missing htmlTable field
    print("1. Testing missing htmlTable field...")
    try:
        response = requests.post(
            f"{base_url}/api/generate-pdf",
            headers={"Content-Type": "application/json"},
            json={}
        )
        if response.status_code == 400:
            print(f"✅ Correctly returned 400: {response.json()}")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test empty htmlTable
    print("\n2. Testing empty htmlTable...")
    try:
        response = requests.post(
            f"{base_url}/api/generate-pdf",
            headers={"Content-Type": "application/json"},
            json={"htmlTable": ""}
        )
        if response.status_code == 400:
            print(f"✅ Correctly returned 400: {response.json()}")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

if __name__ == "__main__":
    # Change this to your deployed URL when testing on Vercel
    BASE_URL = "http://localhost:5000"
    
    print(f"Testing API at: {BASE_URL}\n")
    print("=" * 60)
    
    # Run tests
    test_health_check(BASE_URL)
    test_generate_pdf(BASE_URL, html_table)
    test_error_cases(BASE_URL)
    
    print("=" * 60)
    print("\nAll tests completed!")
    print("\nTo test with your deployed Vercel URL:")
    print("1. Update BASE_URL in this script")
    print("2. Run: python test_api.py")
