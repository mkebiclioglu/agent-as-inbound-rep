import requests
import json

# Test the API endpoints
base_url = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{base_url}/")
        print("✅ Health check:", response.json())
        return True
    except Exception as e:
        print("❌ Health check failed:", e)
        return False

def test_get_leads():
    """Test getting leads"""
    try:
        response = requests.get(f"{base_url}/leads")
        leads = response.json()
        print("✅ Got leads:", len(leads["leads"]), "leads found")
        for lead in leads["leads"]:
            print(f"   - {lead['name']} ({lead['company']})")
        return leads["leads"][0]["id"] if leads["leads"] else None
    except Exception as e:
        print("❌ Get leads failed:", e)
        return None

def test_conversation(lead_id):
    """Test the AI conversation"""
    try:
        # Test message
        test_message = "Hi, I'm interested in 3D printers to print drone parts. What would you recomend?"
        
        payload = {
            "message": test_message,
            "lead_id": lead_id
        }
        
        print(f"🤖 Testing AI conversation with: '{test_message}'")
        response = requests.post(f"{base_url}/conversation/chat", json=payload)
        result = response.json()
        
        print("✅ AI Response:")
        print(f"   Customer: {result['customer_message']}")
        print(f"   AI Agent: {result['ai_response']}")
        return True
    except Exception as e:
        print("❌ Conversation test failed:", e)
        return False

if __name__ == "__main__":
    print("🧪 Testing AI Sales Agent API...")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Server might not be running. Make sure to run 'python main.py' first.")
        exit(1)
    
    print()
    
    # Test leads
    lead_id = test_get_leads()
    if not lead_id:
        print("❌ No leads available for testing.")
        exit(1)
    
    print()
    
    # Test conversation
    test_conversation(lead_id)
    
    print()
    print("🎉 API testing complete!")
    print("You can now visit http://localhost:8000/docs for the interactive API documentation.") 