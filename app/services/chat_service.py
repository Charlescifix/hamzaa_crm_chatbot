from openai import OpenAI
import os
from dotenv import load_dotenv
from app.services.kb_service import KBService
from app.utils.logger import logger

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatService:
    def __init__(self):
        self.kb_service = KBService()

    def get_response(self, message):
        logger.info(f"Received user message: {message}")

        try:
            # Check knowledge base first
            kb_answer = self.kb_service.get_answer(message)
            if kb_answer:
                logger.info("Found relevant answer in knowledge base")
                return kb_answer

            # Fallback to OpenAI
            logger.info("No relevant answer in knowledge base, querying OpenAI...")

            # Updated system prompt
            system_prompt = """
            You are a helpful assistant for Hamzaa, an auto repair shop management software.
            Your role is to assist users with car troubleshooting, automobile-related questions, and Hamzaa's features.
            You must only respond to questions about:
            - Car troubleshooting (e.g., engine problems, brake issues, battery problems).
            - Automobile maintenance (e.g., oil changes, tire rotations).
            - Hamzaa's features (e.g., inventory management, scheduling appointments, invoice generation).
            If a question is outside these topics, politely decline to answer and guide the user to ask automobile-related questions.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},  # Updated system prompt
                    {"role": "user", "content": message}
                ]
            )
            bot_response = response.choices[0].message.content
            logger.info(f"Generated bot response: {bot_response}")
            return bot_response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise