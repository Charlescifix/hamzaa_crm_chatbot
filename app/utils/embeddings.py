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
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding


def load_knowledge_base():
    # Construct the absolute path to faqs.json
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up to the app directory
    kb_path = os.path.join(base_dir, "knowledge_base", "faqs.json")

    with open(kb_path, "r") as f:
        return json.load(f)

    knowledge_base = []

    def extract_qa(data):
        """ Recursively extract questions and answers from nested dictionaries """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) and "Question" in value and "Answer" in value:
                    knowledge_base.append({"question": value["Question"], "answer": value["Answer"]})
                else:
                    extract_qa(value)  # Recursively search deeper
        elif isinstance(data, list):
            for item in data:
                extract_qa(item)

    extract_qa(raw_data)
    return knowledge_base  # Returns a list of Q&A dictionaries



def find_most_relevant_answer(query, knowledge_base):
    query_embedding = get_embedding(query)
    max_similarity = -1
    best_answer = None

    for item in knowledge_base:
        if isinstance(item, dict) and "question" in item and "answer" in item:
            item_embedding = get_embedding(item["question"])
            similarity = cosine_similarity([query_embedding], [item_embedding])[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                best_answer = item["answer"]

    return best_answer if max_similarity > 0.7 else None  # Threshold for relevance
