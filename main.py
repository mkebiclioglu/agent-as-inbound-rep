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
]

# Conversation history storage
conversation_history = {}

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
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content
        
        # Store the conversation in history
        conversation_history[conversation.lead_id].append({"role": "user", "content": conversation.message})
        conversation_history[conversation.lead_id].append({"role": "assistant", "content": ai_response})
        
        return {
            "lead_id": conversation.lead_id,
            "customer_message": conversation.message,
            "ai_response": ai_response,
            "conversation_length": len(conversation_history[conversation.lead_id])
        }
        
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/conversation/history/{lead_id}")
def get_conversation_history(lead_id: str):
    """Get conversation history for a specific lead"""
    if lead_id not in conversation_history:
        return {"conversation_history": [], "message": "No conversation history found for this lead"}
    
    return {
        "lead_id": lead_id,
        "conversation_history": conversation_history[lead_id],
        "total_messages": len(conversation_history[lead_id])
    }

@app.delete("/conversation/history/{lead_id}")
def clear_conversation_history(lead_id: str):
    """Clear conversation history for a specific lead"""
    if lead_id in conversation_history:
        del conversation_history[lead_id]
        return {"message": f"Conversation history cleared for lead {lead_id}"}
    else:
        raise HTTPException(status_code=404, detail="No conversation history found for this lead")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 