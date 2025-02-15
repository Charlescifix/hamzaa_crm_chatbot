import logging
import os
from logging.handlers import RotatingFileHandler
from app.config import Config


# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Set up logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("logs/hamzaa_chatbot.log", maxBytes=1024 * 1024 * 5, backupCount=5),  # 5 MB per file
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)