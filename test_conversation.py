import requests
import json
import time

# Test the conversation with history
base_url = "http://localhost:8000"

def test_conversation_flow():
    """Test a back-and-forth conversation with the AI agent"""
    
    lead_id = "lead_001"  # John Smith
    
    # Conversation flow
    conversation_flow = [
        "Hi, I'm interested in 3D printers for dental applications. What would you recommend?",
        "That sounds good. What about the accuracy and speed?",
        "What's the difference between the Form 4 and Form 4L?",
        "I'm concerned about the price. Do you have any financing options?",
        "Great! Can you send me a quote for the Form 4 package?"
    ]
    
    print("🤖 Testing Back-and-Forth Conversation with AI Sales Agent")
    print("=" * 60)
    print(f"Customer: {lead_id}")
    print()
    
    for i, message in enumerate(conversation_flow, 1):
        print(f"📝 Message {i}: {message}")
        
        # Send message to AI
        payload = {
            "message": message,
            "lead_id": lead_id
        }
        
        try:
            response = requests.post(f"{base_url}/conversation/chat", json=payload)
            result = response.json()
            
            print(f"🤖 AI Response: {result['ai_response']}")
            print(f"📊 Conversation Length: {result['conversation_length']} messages")
            print("-" * 40)
            
            # Small delay to make it feel more natural
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    # Show conversation history
    print("\n📚 Full Conversation History:")
    print("=" * 60)
    
    try:
        history_response = requests.get(f"{base_url}/conversation/history/{lead_id}")
        history = history_response.json()
        
        for i, msg in enumerate(history['conversation_history'], 1):
            role = "👤 Customer" if msg['role'] == 'user' else "🤖 AI Agent"
            print(f"{i}. {role}: {msg['content']}")
            
    except Exception as e:
        print(f"❌ Error getting history: {e}")

if __name__ == "__main__":
    test_conversation_flow() 