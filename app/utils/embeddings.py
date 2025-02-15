from openai import OpenAI
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    """
    Generate an embedding for the given text using OpenAI's text-embedding-ada-002 model.
    """
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def load_knowledge_base():
    """
    Load the knowledge base from the faqs.json file.
    The file contains nested JSON, so we need to recursively extract questions and answers.
    """
    # Construct the absolute path to faqs.json
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up to the app directory
    kb_path = os.path.join(base_dir, "knowledge_base", "faqs.json")

    # Debug: Print the path to faqs.json
    print(f"Loading knowledge base from: {kb_path}")

    # Load the knowledge base from the JSON file
    try:
        with open(kb_path, "r") as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        return []

    # Debug: Print the raw data
    print(f"Raw knowledge base data: {raw_data}")

    # Extract questions and answers from the raw data
    knowledge_base = []
    extract_qa(raw_data, knowledge_base)

    # Debug: Print the extracted knowledge base
    print(f"Extracted knowledge base: {knowledge_base}")

    return knowledge_base

def extract_qa(data, knowledge_base):
    """
    Recursively extract questions and answers from nested dictionaries or lists.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and "Question" in value and "Answer" in value:
                # Extract Q&A pairs
                knowledge_base.append({"question": value["Question"], "answer": value["Answer"]})
            else:
                # Recursively search deeper
                extract_qa(value, knowledge_base)
    elif isinstance(data, list):
        for item in data:
            extract_qa(item, knowledge_base)

def find_most_relevant_answer(query, knowledge_base):
    """
    Find the most relevant answer in the knowledge base for the given query.
    """
    print(f"Searching for query: {query}")

    query_embedding = get_embedding(query)
    max_similarity = -1
    best_answer = None

    for item in knowledge_base:
        if isinstance(item, dict) and "question" in item and "answer" in item:
            item_embedding = get_embedding(item["question"])
            similarity = cosine_similarity([query_embedding], [item_embedding])[0][0]
            print(f"Question: {item['question']}, Similarity: {similarity}")

            if similarity > max_similarity:
                max_similarity = similarity
                best_answer = item["answer"]

    print(f"Best answer: {best_answer}, Max similarity: {max_similarity}")
    return best_answer if max_similarity > 0.8 else None  # Threshold for relevance