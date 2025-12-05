from mistralai import Mistral
from dotenv import load_dotenv
import os
import sqlite3
import json


class IntrospectionAgent:
    def __init__(self, db_path="memory.db"):

        load_dotenv()

        api_key = os.getenv("MISTRALAI_API_KEY") or os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("ERROR: MISTRALAI_API_KEY not found in environment")

        self.model = "mistral-medium-latest"
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

    def generate_reflection(
        self,
        query,
        rag_output=None,
        web_output=None,
        reasoning_output=None,
        feedback=None,
        answer=None,
    ):
        answer_text = answer or rag_output or ""
        web_text = ""
        if isinstance(web_output, dict):
            web_text = web_output.get("summary") or web_output.get("results") or ""
        elif web_output:
            web_text = str(web_output)

        reasoning_text = reasoning_output or ""
        feedback_text = feedback or ""

        prompt = f"""
        You are the Introspection Agent.

        USER QUERY: {query}
        SYSTEM ANSWER: {answer_text}
        WEB EVIDENCE: {web_text}
        INTERNAL REASONING: {reasoning_text}
        USER FEEDBACK: {feedback_text}

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

        message = response.choices[0].message
        return message["content"] if isinstance(message, dict) else message.content

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
        reflection_json = self.generate_reflection(query, answer=answer, feedback=feedback)

        reflection, score = self.save_reflection(query, answer, feedback, reflection_json)

        return {
            "reflection": reflection,
            "score": score
        }
