import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def test_openai_connection():
    """Test if OpenAI API key is working"""
    try:
        print("🔑 Testing OpenAI API key...")
        print(f"API Key (first 10 chars): {os.getenv('OPENAI_API_KEY')[:10]}...")
        
        # Simple test request
        response = openai.ChatCompletion.create(
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