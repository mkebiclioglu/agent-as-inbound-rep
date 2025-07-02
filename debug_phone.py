import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Debugging Phone Configuration")
print("=" * 40)

# Check customer phone
customer_phone = os.getenv("CUSTOMER_PHONE_NUMBER")
print(f"📱 Customer Phone: {customer_phone}")

# Check Twilio phone
twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
print(f"📞 Twilio Phone: {twilio_phone}")

# Check Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

print(f"🔑 Account SID: {account_sid[:10]}..." if account_sid else "❌ Not set")
print(f"🔑 Auth Token: {auth_token[:10]}..." if auth_token else "❌ Not set")

# Check webhook URL
webhook_url = os.getenv("WEBHOOK_BASE_URL")
print(f"🌐 Webhook URL: {webhook_url}")

print("\n📋 Recommendations:")
if not customer_phone or customer_phone == "+1234567890":
    print("❌ Update CUSTOMER_PHONE_NUMBER with your real phone number")
if not twilio_phone or twilio_phone == "+1234567890":
    print("❌ Update TWILIO_PHONE_NUMBER with your Twilio phone number")
if not account_sid:
    print("❌ Add your TWILIO_ACCOUNT_SID")
if not auth_token:
    print("❌ Add your TWILIO_AUTH_TOKEN")
if not webhook_url or "your-ngrok-url" in webhook_url:
    print("❌ Update WEBHOOK_BASE_URL with your actual ngrok URL") 