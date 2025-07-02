import requests
import json

# Test voice call functionality
base_url = "http://localhost:8000"

def test_voice_call():
    """Test initiating a voice call"""
    
    lead_id = "lead_001"  # John Smith
    
    print("📞 Testing Voice Call Initiation")
    print("=" * 50)
    print(f"Customer: {lead_id}")
    print()
    
    try:
        # First, get customer phone info
        print("📋 Getting customer phone information...")
        phone_response = requests.get(f"{base_url}/customer/phone/{lead_id}")
        phone_info = phone_response.json()
        
        print(f"✅ Customer: {phone_info['customer_name']}")
        print(f"📱 Phone: {phone_info['phone_number']}")
        print(f"🏢 Company: {phone_info['company']}")
        print()
        
        # Initiate the call
        print("📞 Initiating voice call...")
        call_response = requests.post(f"{base_url}/voice/initiate-call/{lead_id}")
        call_result = call_response.json()
        
        print(f"✅ Call initiated successfully!")
        print(f"📞 Call SID: {call_result['call_sid']}")
        print(f"👤 Customer: {call_result['customer_name']}")
        print(f"📱 Phone: {call_result['phone_number']}")
        print()
        print("🎉 You should receive a call on your phone shortly!")
        print("📝 Note: Make sure your Twilio credentials are configured and ngrok is running.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("🔧 Troubleshooting:")
        print("1. Make sure your Twilio credentials are in .env file")
        print("2. Ensure ngrok is running and webhook URL is updated")
        print("3. Check that your phone number is correct in .env")

if __name__ == "__main__":
    test_voice_call() 