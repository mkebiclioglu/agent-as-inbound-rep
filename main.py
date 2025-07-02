import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import openai

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI Sales Agent", description="AI-powered inbound sales representative")

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables!")
    print("Please create a .env file with your OpenAI API key.")
    print("You can copy env.example to .env and add your key.")

# Pydantic models
class Lead(BaseModel):
    name: str
    email: str
    phone: str
    company: str
    inquiry: str

class ConversationMessage(BaseModel):
    message: str
    lead_id: str



# Mock data for MVP
mock_leads = [
    {
        "id": "lead_001",
        "name": "John Smith",
        "email": "john.smith@techcompany.com",
        "phone": "+1-555-0123",
        "company": "TechCorp Industries",
        "inquiry": "Interested in industrial 3D printers for prototyping. Need high precision and large build volume."
    },
    {
        "id": "lead_002", 
        "name": "Sarah Johnson",
        "email": "sarah.j@startup.com",
        "phone": "+1-555-0456",
        "company": "Innovation Startup",
        "inquiry": "Looking for affordable desktop 3D printers for educational purposes. Need 5-10 units."
    }
]

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

@app.get("/leads")
def get_leads():
    """Get all available leads"""
    return {"leads": mock_leads}

@app.get("/leads/{lead_id}")
def get_lead(lead_id: str):
    """Get a specific lead by ID"""
    for lead in mock_leads:
        if lead["id"] == lead_id:
            return lead
    raise HTTPException(status_code=404, detail="Lead not found")

@app.post("/conversation/chat")
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
2. Provide relevant product recommendations
3. Handle objections professionally
4. Be conversational and helpful

Respond naturally as if you're having a real phone conversation."""

        # Generate response using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": conversation.message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content
        
        return {
            "lead_id": conversation.lead_id,
            "customer_message": conversation.message,
            "ai_response": ai_response
        }
        
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 