from openai import OpenAI
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from dotenv import load_dotenv
from app.utils.logger import logger  # Import the logger

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    """
    Generate an embedding for the given text using OpenAI's text-embedding-ada-002 model.
    """
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None

def load_knowledge_base():
    """
    Load the knowledge base from the faqs.json file.
    The file should contain a list of dictionaries with "question" and "answer" keys.
    """
    # Construct the absolute path to faqs.json
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up to the app directory
    kb_path = os.path.join(base_dir, "knowledge_base", "faqs.json")
    logger.debug(f"Loading knowledge base from: {kb_path}")

    # Load the knowledge base from the JSON file
    try:
        with open(kb_path, "r") as f:
            raw_data = json.load(f)
        logger.debug("Successfully loaded knowledge base")
    except FileNotFoundError:
        logger.error(f"Knowledge base file not found at: {kb_path}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in knowledge base file: {kb_path}")
        return []

    # Extract questions and answers from the raw data
    knowledge_base = []
    if isinstance(raw_data, list):
        for item in raw_data:
            if isinstance(item, dict) and "question" in item and "answer" in item:
                knowledge_base.append({"question": item["question"], "answer": item["answer"]})
            elif isinstance(item, dict):
                # If the data is nested, recursively extract Q&A
                extract_qa(item, knowledge_base)
    elif isinstance(raw_data, dict):
        # If the data is a single dictionary, extract Q&A
        extract_qa(raw_data, knowledge_base)

    logger.debug(f"Extracted {len(knowledge_base)} Q&A pairs from knowledge base")
    return knowledge_base

def extract_qa(data, knowledge_base):
    """
    Recursively extract questions and answers from nested dictionaries or lists.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and "question" in value and "answer" in value:
                knowledge_base.append({"question": value["question"], "answer": value["answer"]})
            else:
                extract_qa(value, knowledge_base)  # Recursively search deeper
    elif isinstance(data, list):
        for item in data:
            extract_qa(item, knowledge_base)

def find_most_relevant_answer(query, knowledge_base):
    """
    Find the most relevant answer in the knowledge base for the given query.
    """
    query_embedding = get_embedding(query)
    if query_embedding is None:
        logger.error("Failed to generate embedding for the query")
        return None

    max_similarity = -1
    best_answer = None

    for item in knowledge_base:
        if isinstance(item, dict) and "question" in item and "answer" in item:
            item_embedding = get_embedding(item["question"])
            if item_embedding is None:
                logger.error(f"Failed to generate embedding for question: {item['question']}")
                continue

            similarity = cosine_similarity([query_embedding], [item_embedding])[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                best_answer = item["answer"]

    if best_answer:
        logger.debug(f"Found relevant answer with similarity score: {max_similarity}")
    else:
        logger.debug("No relevant answer found in knowledge base")

    return best_answer if max_similarity > 0.7 else None  # Threshold for relevance