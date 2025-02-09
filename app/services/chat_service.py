from openai import OpenAI
import os
from dotenv import load_dotenv
from app.services.kb_service import KBService
from app.utils.logger import logger  # Import the logger

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatService:
    def __init__(self):
        self.kb_service = KBService()

    def get_response(self, message):
        logger.info(f"Received user message: {message}")  # Log the incoming message

        try:
            # Check knowledge base first
            kb_answer = self.kb_service.get_answer(message)
            if kb_answer:
                logger.info("Found relevant answer in knowledge base")  # Log KB hit
                return kb_answer

            # Fallback to OpenAI
            logger.info("No relevant answer in knowledge base, querying OpenAI...")  # Log OpenAI fallback
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for Hamzaa, an auto repair shop management software."},
                    {"role": "user", "content": message}
                ]
            )
            bot_response = response.choices[0].message.content
            logger.info(f"Generated bot response: {bot_response}")  # Log the bot response
            return bot_response

        except Exception as e:
            logger.error(f"Error generating response: {e}")  # Log errors
            raise