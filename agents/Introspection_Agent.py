from mistralai import Mistral
from dotenv import load_dotenv
import os
import sqlite3
import json

class IntrospectionAgent:
    def __init__(self, db_path="memory.db"):
        
        load_dotenv()
        
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("ERROR: MISTRAL_API_KEY not found in .env file")
         
        self.model = "phi-mini-3"
        self.client = Mistral(api_key=api_key)

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                answer TEXT,
                feedback TEXT,
                reflection TEXT,
                score INTEGER
            )
        """)
        
        conn.commit()
        conn.close()

    def generate_reflection(self, query, answer, feedback):
        prompt = f"""
        You are the Introspection Agent.

        USER QUERY: {query}
        SYSTEM ANSWER: {answer}
        USER FEEDBACK: {feedback}

        Produce a self-reflection that explains:
        - Whether the answer was good or bad
        - What could be improved next time
        - Assign an improvement score from 1 to 10

        Return ONLY JSON in this EXACT format:
        {{
            "reflection": "text here",
            "score": number
        }}
        """

        response = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message["content"]

    def save_reflection(self, query, answer, feedback, reflection_json):
        data = json.loads(reflection_json)
        reflection = data["reflection"]
        score = data["score"]

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO reflections (query, answer, feedback, reflection, score)
            VALUES (?, ?, ?, ?, ?)
        """, (query, answer, feedback, reflection, score))

        conn.commit()
        conn.close()

        return reflection, score

    def run(self, query, answer, feedback):
        reflection_json = self.generate_reflection(query, answer, feedback)

        reflection, score = self.save_reflection(query, answer, feedback, reflection_json)

        return {
            "reflection": reflection,
            "score": score
        }
