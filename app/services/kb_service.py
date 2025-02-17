from app.utils.embeddings import load_knowledge_base, find_most_relevant_answer

class KBService:
    def __init__(self):
        self.knowledge_base = load_knowledge_base()

    def get_answer(self, query):
        return find_most_relevant_answer(query, self.knowledge_base)