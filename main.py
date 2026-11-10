import os
import secrets
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Form
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from openai import OpenAI
from twilio.request_validator import RequestValidator
from twilio_client import TwilioVoiceClient

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI Sales Agent", description="AI-powered inbound sales representative")

# Configure OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
if not openai_client:
    print("Warning: OPENAI_API_KEY not found in environment variables!")
    print("Please create a .env file with your OpenAI API key.")
    print("You can copy env.example to .env and add your key.")

MAX_MESSAGE_LENGTH = 4000
MAX_HISTORY_MESSAGES = 50


def require_api_access(request: Request, x_api_key: Optional[str] = Header(None)):
    """Protect the API: these endpoints place calls, spend OpenAI credits and return lead data.

    With API_KEY set, callers must send it as X-API-Key. Without it, only direct
    requests from this machine are served (not ones arriving through ngrok or a proxy).
    """
    api_key = os.getenv("API_KEY")
    if api_key:
        if not x_api_key or not secrets.compare_digest(x_api_key.encode(), api_key.encode()):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
        return
    client_host = request.client.host if request.client else ""
    forwarded = any(h in request.headers for h in ("x-forwarded-for", "x-forwarded-host", "forwarded"))
    if client_host not in ("127.0.0.1", "::1") or forwarded:
        raise HTTPException(status_code=403, detail="Set API_KEY to use this endpoint remotely")


async def require_twilio_signature(request: Request):
    """Only accept voice webhooks that carry a valid Twilio signature."""
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    webhook_base_url = os.getenv("WEBHOOK_BASE_URL")
    if not auth_token or not webhook_base_url:
        raise HTTPException(status_code=403, detail="Twilio webhook validation is not configured")
    url = webhook_base_url.rstrip("/") + request.url.path
    if request.url.query:
        url += "?" + request.url.query
    form = await request.form()
    params = {key: value for key, value in form.items() if isinstance(value, str)}
    signature = request.headers.get("X-Twilio-Signature", "")
    if not RequestValidator(auth_token).validate(url, params, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")


api_access = [Depends(require_api_access)]
twilio_webhook = [Depends(require_twilio_signature)]

# Pydantic models
class Lead(BaseModel):
    name: str
    email: str
    phone: str
    company: str
    inquiry: str

class ConversationMessage(BaseModel):
    message: str = Field(max_length=MAX_MESSAGE_LENGTH)
    lead_id: str



# Mock data for MVP
customer_phone = os.getenv("CUSTOMER_PHONE_NUMBER", "+1-555-0123")  # Default fallback
mock_leads = [
    {
        "id": "lead_001",
        "name": "John Smith",
        "email": "john.smith@techcompany.com",
        "phone": customer_phone,
        "company": "TechCorp Industries",
        "inquiry": "Interested in industrial 3D printers for prototyping. Need high precision and large build volume."
    }
]

# Conversation history storage
conversation_history = {}

# Initialize Twilio client
twilio_client = TwilioVoiceClient()

# Simple product knowledge base
product_knowledge = {
    "desktop printer": {
        "name": "Form 4 Complete Package",
        "price": 5849,
        "description": "High-speed desktop SLA printer with ±35 micron accuracy, ideal for prototyping and dental applications. Includes Form Wash, Form Cure, resin tank, build platform, and 1-year Pro Service Plan."
    },
    "benchtop printer": {
        "name": "Form 4L Complete Package",
        "price": 20399,
        "description": "Large-format SLA printer with 345×145×295 mm build volume and ±25 micron accuracy. Suited for production-size prototypes. Includes Form Wash L, Form Cure L, resin pumping system, and 1-year Pro Service Plan."
    },
    "sls printer": {
        "name": "Fuse 1+ 30W Complete Package",
        "price": 54241,
        "description": "Industrial SLS 3D printer for durable nylon parts with no support structures. Includes Fuse 1+ 30W printer, Fuse Sift powder recovery station, Fuse Blast cleaning station, and post-processing tools."
    }
}

@app.get("/")
def read_root():
    return {"message": "AI Sales Agent is running!"}

@app.get("/leads", dependencies=api_access)
def get_leads():
    """Get all available leads"""
    return {"leads": mock_leads}

@app.get("/leads/{lead_id}", dependencies=api_access)
def get_lead(lead_id: str):
    """Get a specific lead by ID"""
    for lead in mock_leads:
        if lead["id"] == lead_id:
            return lead
    raise HTTPException(status_code=404, detail="Lead not found")

@app.post("/conversation/chat", dependencies=api_access)
def chat_with_lead(conversation: ConversationMessage):
    """Generate AI response for customer conversation"""
    try:
        # Find the lead
        lead = None
        for l in mock_leads:
            if l["id"] == conversation.lead_id:
                lead = l
                break
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Initialize conversation history for this lead if it doesn't exist
        if conversation.lead_id not in conversation_history:
            conversation_history[conversation.lead_id] = []
        
        # Create system prompt
        system_prompt = f"""You are an expert inbound sales representative for Formlabs, a leading 3D printer manufacturer.

Customer Information:
- Name: {lead['name']}
- Company: {lead['company']}
- Inquiry: {lead['inquiry']}

Available Products:
{product_knowledge}

Your role is to:
1. Understand customer needs through discovery questions
2. Provide relevant product recommendations based on customer painpoints and needs
3. Handle objections professionally
4. Be conversational and helpful
5. Remember previous parts of the conversation

Respond naturally as if you're having a real phone conversation. 
So your answers don't need to be too long and keep it conversational.
Try to guide the conversation to the next step in the sales process which is either:
1. Sending a quote based on the conversation
2. Scheduling a follow up call with the customer at a later date
"""

        # Build messages array with conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 10 messages to keep context manageable)
        for msg in conversation_history[conversation.lead_id][-10:]:
            messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": conversation.message})
        
        # Generate response using OpenAI
        if not openai_client:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content
        
        # Store the conversation in history
        conversation_history[conversation.lead_id].append({"role": "user", "content": conversation.message})
        conversation_history[conversation.lead_id].append({"role": "assistant", "content": ai_response})
        del conversation_history[conversation.lead_id][:-MAX_HISTORY_MESSAGES]
        
        return {
            "lead_id": conversation.lead_id,
            "customer_message": conversation.message,
            "ai_response": ai_response,
            "conversation_length": len(conversation_history[conversation.lead_id])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating response")

@app.get("/conversation/history/{lead_id}", dependencies=api_access)
def get_conversation_history(lead_id: str):
    """Get conversation history for a specific lead"""
    if lead_id not in conversation_history:
        return {"conversation_history": [], "message": "No conversation history found for this lead"}
    
    return {
        "lead_id": lead_id,
        "conversation_history": conversation_history[lead_id],
        "total_messages": len(conversation_history[lead_id])
    }

@app.delete("/conversation/history/{lead_id}", dependencies=api_access)
def clear_conversation_history(lead_id: str):
    """Clear conversation history for a specific lead"""
    if lead_id in conversation_history:
        del conversation_history[lead_id]
        return {"message": f"Conversation history cleared for lead {lead_id}"}
    else:
        raise HTTPException(status_code=404, detail="No conversation history found for this lead")

@app.get("/customer/phone/{lead_id}", dependencies=api_access)
def get_customer_phone(lead_id: str):
    """Get customer phone number for call initiation"""
    for lead in mock_leads:
        if lead["id"] == lead_id:
            return {
                "lead_id": lead_id,
                "customer_name": lead["name"],
                "phone_number": lead["phone"],
                "company": lead["company"]
            }
    raise HTTPException(status_code=404, detail="Lead not found")

@app.post("/voice/initiate-call/{lead_id}", dependencies=api_access)
def initiate_call(lead_id: str):
    """Initiate a voice call to the customer"""
    try:
        # Get customer info
        customer_info = get_customer_phone(lead_id)
        
        # Create webhook URL for this call
        webhook_base_url = os.getenv("WEBHOOK_BASE_URL")
        if not webhook_base_url:
            raise HTTPException(status_code=500, detail="WEBHOOK_BASE_URL not configured. Please set it in your .env file.")
        
        webhook_url = f"{webhook_base_url.rstrip('/')}/voice/gather?lead_id={lead_id}"
        
        # Make the call
        call_sid = twilio_client.make_call(
            to_number=customer_info["phone_number"],
            webhook_url=webhook_url
        )
        
        return {
            "message": "Call initiated successfully",
            "call_sid": call_sid,
            "customer_name": customer_info["customer_name"],
            "phone_number": customer_info["phone_number"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error initiating call: {str(e)}")
        raise HTTPException(status_code=500, detail="Error initiating call")

@app.post("/voice/gather", dependencies=twilio_webhook)
async def gather_speech(request: Request, lead_id: str = Form(None)):
    """Initial greeting and speech gathering"""
    try:
        print(f"🔍 Gather endpoint called with lead_id: {lead_id}")
        print(f"🔍 Query params: {request.query_params}")
        
        # If lead_id is not in form data, try to get it from query parameters
        if not lead_id:
            lead_id = request.query_params.get("lead_id")
            print(f"🔍 Got lead_id from query params: {lead_id}")
        
        if not lead_id:
            # Default to lead_001 if no lead_id provided
            lead_id = "lead_001"
            print(f"🔍 Using default lead_id: {lead_id}")
        
        # Get customer info
        customer_info = get_customer_phone(lead_id)
        print(f"🔍 Customer info: {customer_info}")
        
        # Create greeting message with SSML for natural speech
        greeting = f"""<speak>
            Hello {customer_info['customer_name']}, this is Sarah from Formlabs. 
            <break time="0.5s"/>
            I noticed you showed interest in our 3D printers. 
            <break time="0.3s"/>
            I'd love to learn more about your needs and see how we can help you achieve your goals. 
            <break time="0.5s"/>
            What specific applications are you looking to use 3D printing for?
        </speak>"""
        
        # Create TwiML response
        twiml_response = twilio_client.create_gather_response(greeting)
        print(f"🔍 TwiML response created successfully")
        
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        print(f"❌ Error in gather endpoint: {str(e)}")
        # Return a simple error response instead of raising HTTPException
        error_response = twilio_client.create_final_response("I apologize for the technical difficulties. Please call us back later. Thank you!")
        return Response(content=error_response, media_type="application/xml")

@app.post("/voice/process-speech", dependencies=twilio_webhook)
async def process_speech(
    request: Request,
    lead_id: str = Form(None),
    SpeechResult: str = Form(None)
):
    """Process speech input and generate AI response"""
    # If lead_id is not in form data, try to get it from query parameters
    if not lead_id:
        lead_id = request.query_params.get("lead_id")
    
    if not lead_id:
        # Default to lead_001 if no lead_id provided
        lead_id = "lead_001"
    
    try:
        print(f"🔍 Process speech called with lead_id: {lead_id}, SpeechResult: {SpeechResult}")
        
        if not SpeechResult:
            # No speech detected, ask to repeat
            print("🔍 No speech detected, asking to repeat")
            twiml_response = twilio_client.create_gather_response("I didn't catch that. Could you please repeat your question?")
            return Response(content=twiml_response, media_type="application/xml")
        
        # Generate AI response
        print(f"🔍 Generating AI response for: {SpeechResult}")
        conversation = ConversationMessage(message=SpeechResult, lead_id=lead_id)
        chat_result = chat_with_lead(conversation)
        
        # Create voice response
        print(f"🔍 AI response: {chat_result['ai_response']}")
        twiml_response = twilio_client.create_gather_response(chat_result["ai_response"])
        
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        print(f"❌ Error in process_speech endpoint: {str(e)}")
        # Error handling - end call gracefully
        twiml_response = twilio_client.create_final_response("I apologize for the technical difficulties. Please call us back later. Thank you!")
        return Response(content=twiml_response, media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    # ngrok forwards to localhost, so there is no need to listen on every interface
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=8000) 