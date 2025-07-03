import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

import logging

logger = logging.getLogger(__name__)

class TwilioVoiceClient:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("Twilio client initialized successfully")
        else:
            self.client = None
            logger.warning("Twilio credentials not found. Voice calls will be disabled.")
    
    def make_call(self, to_number: str, webhook_url: str):
        """Initiate an outbound call"""
        if not self.client:
            raise Exception("Twilio client not configured")
        
        try:
            call = self.client.calls.create(
                url=webhook_url,  # Webhook URL for TwiML instructions
                to=to_number,
                from_=self.phone_number
            )
            logger.info(f"Call initiated: {call.sid}")
            return call.sid
        except Exception as e:
            logger.error(f"Error making call: {e}")
            raise
    
    def create_voice_response(self, message: str, gather_input: bool = True):
        """Create TwiML response for voice call"""
        response = VoiceResponse()
        
        if gather_input:
            # Use Gather to collect speech input
            gather = response.gather(
                input='speech',
                timeout=10,
                speech_timeout='auto',
                action='/voice/process-speech',
                method='POST'
            )
            # Use neural voice for more natural sound with SSML support
            gather.say(message, voice='Google.en-US-Neural2-F', language='en-US')
            
            # If no input is received, repeat the message
            response.say("I didn't catch that. Let me repeat.", voice='Google.en-US-Neural2-F', language='en-US')
            response.redirect('/voice/gather')
        else:
            # Just say the message without gathering input
            response.say(message, voice='Google.en-US-Neural2-F', language='en-US')
            response.hangup()
        
        return str(response)
    
    def create_gather_response(self, message: str):
        """Create a response that gathers speech input"""
        response = VoiceResponse()
        gather = response.gather(
            input='speech',
            timeout=10,
            speech_timeout='auto',
            action='/voice/process-speech',
            method='POST'
        )
        # Use neural voice for more natural sound
        gather.say(message, voice='Google.en-US-Neural2-F', language='en-US')
        
        # If no input is received, end the call
        response.say("Thank you for your time. Goodbye!", voice='Google.en-US-Neural2-F', language='en-US')
        response.hangup()
        
        return str(response)
    
    def create_final_response(self, message: str):
        """Create final response before ending call"""
        response = VoiceResponse()
        response.say(message, voice='Google.en-US-Neural2-F', language='en-US')
        response.hangup()
        return str(response) 