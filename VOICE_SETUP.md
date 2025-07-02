# Voice Call Setup Guide

## 🎯 Goal
Receive an actual phone call from the AI agent and have a real conversation with it.

## 📋 Prerequisites

### 1. Twilio Account Setup
1. Sign up for a free Twilio account at https://www.twilio.com
2. Get your Account SID and Auth Token from the Twilio Console
3. Purchase a phone number (or use trial credits for testing)
4. **IMPORTANT**: Verify your phone number in Twilio Console (Phone Numbers → Verified Caller IDs)

### 2. Environment Configuration
Update your `.env` file with your credentials:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
COMPANY_NAME=TechPrint Solutions
COMPANY_EMAIL=sales@techprintsolutions.com

# Phone Configuration
CUSTOMER_PHONE_NUMBER=+1234567890  # Your actual phone number

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_actual_account_sid
TWILIO_AUTH_TOKEN=your_actual_auth_token
TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio phone number

# Webhook Configuration
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io  # Your ngrok URL
```

### 3. Ngrok Setup (for webhooks)
1. Install ngrok: `brew install ngrok/ngrok/ngrok` (or download from ngrok.com)
2. Start ngrok to expose your local server:
   ```bash
   ngrok http 8000
   ```
3. Copy the HTTPS ngrok URL (e.g., `https://abc123def456.ngrok.io`)
4. Update `WEBHOOK_BASE_URL` in your `.env` file (not in the code)

## 🚀 Testing the Voice Integration

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Ngrok (in one terminal)
```bash
ngrok http 8000
# Keep this terminal open - don't close it!
```

### Step 3: Start the Server (in another terminal)
```bash
source venv/bin/activate
python main.py
```

### Step 4: Test the Call
```bash
python test_voice_call.py
```

### Step 5: Debug if needed
```bash
python debug_phone.py  # Check configuration
python test_twilio_verification.py  # Test Twilio setup
```

## 📞 How It Works

1. **Call Initiation**: The AI agent calls your phone number
2. **Greeting**: "Hello John, this is Sarah from Formlabs..."
3. **Speech Recognition**: Your voice is converted to text
4. **AI Processing**: GPT-4o-mini generates a response
5. **Text-to-Speech**: AI response is spoken back to you
6. **Conversation Loop**: Continues until you hang up

## 🔧 Troubleshooting

### Common Issues:
1. **"Twilio client not configured"** - Check your .env file
2. **"Webhook URL not accessible"** - Make sure ngrok is running
3. **"Call failed"** - Verify your phone number format (+1XXXXXXXXXX)
4. **"Number is unverified"** - Re-verify your phone number in Twilio Console
5. **"No speech detected"** - Speak clearly and wait for the beep
6. **Import errors** - Run `pip install -r requirements.txt`

### Testing Tips:
- Use a quiet environment for better speech recognition
- Speak clearly and at a normal pace
- Wait for the AI to finish speaking before responding
- Test with simple questions first
- Keep ngrok terminal open while testing

### Debug Commands:
```bash
python debug_phone.py  # Check all configuration
python test_twilio_verification.py  # Test Twilio setup
python test_api.py  # Test basic API functionality
```

## 🎉 Expected Experience

You should receive a call that sounds like:
- "Hello John, this is Sarah from Formlabs. I noticed you showed interest in our 3D printers..."
- The AI will ask about your needs
- You can respond naturally
- The AI will remember the conversation and provide relevant recommendations
- The call continues until you hang up or the AI suggests next steps

## 📁 Project Structure

```
agent-as-inbound-rep/
├── main.py                    # Main FastAPI application
├── twilio_client.py           # Twilio voice integration
├── test_voice_call.py         # Voice call testing
├── test_conversation.py       # Conversation testing
├── debug_phone.py             # Configuration debugging
├── test_twilio_verification.py # Twilio setup testing
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
├── env.example               # Environment template
└── VOICE_SETUP.md            # This guide
```

## 📝 Next Steps

After successful voice testing:
1. Add call recording and transcription
2. Implement call analytics
3. Add more sophisticated conversation flows
4. Integrate with CRM for lead tracking
5. Add quote generation based on conversations 