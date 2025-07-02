import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

def test_twilio_verification():
    """Test if the phone number is properly verified"""
    
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    customer_phone = os.getenv("CUSTOMER_PHONE_NUMBER")
    
    if not all([account_sid, auth_token, customer_phone]):
        print("❌ Missing Twilio credentials or phone number")
        return
    
    try:
        client = Client(account_sid, auth_token)
        
        # Try to get account info to test credentials
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Twilio credentials valid")
        print(f"📊 Account status: {account.status}")
        
        # Try to make a test call (this will fail if number not verified, but we'll see the error)
        print(f"📞 Testing call to: {customer_phone}")
        
        # This will likely fail, but we'll get a more specific error
        call = client.calls.create(
            url="http://demo.twilio.com/docs/voice.xml",  # Simple test TwiML
            to=customer_phone,
            from_=os.getenv("TWILIO_PHONE_NUMBER")
        )
        
        print(f"✅ Call initiated: {call.sid}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        if "unverified" in str(e).lower():
            print("\n🔧 Solution: Re-verify your phone number in Twilio Console")
            print("1. Go to https://console.twilio.com/")
            print("2. Navigate to Phone Numbers → Verified Caller IDs")
            print("3. Add your number +16175106633 again")
            print("4. Complete the verification process")
        elif "trial" in str(e).lower():
            print("\n🔧 Solution: Upgrade to a paid Twilio account or verify your number")

if __name__ == "__main__":
    test_twilio_verification() 