import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test if OpenAI API key is working"""
    try:
        print("🔑 Testing OpenAI API key...")
        print("API Key: set" if os.getenv("OPENAI_API_KEY") else "API Key: NOT set")
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'Hello, API is working!'"}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI API is working!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_connection() 