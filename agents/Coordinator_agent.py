import os
import sqlite3
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_classic.schema import HumanMessage

from .InHouseSearch_agent import IHouseRAGAgent
from .WebScraper_agent import WebSearchAgent
from .Summarizer_agent import SummarizerAgent
from .Introspection_Agent import IntrospectionAgent

DB_PATH = Path(__file__).resolve().parent / "aqualens.db"


class CoordinatorAgent:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("MISTRALAI_API_KEY") or os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRALAI_API_KEY is required for CoordinatorAgent")

        os.environ.setdefault("MISTRAL_API_KEY", api_key)

        self.client = ChatMistralAI(
            mistral_api_key=api_key,
            model_name="mistral-medium-latest",
            temperature=0
        )

        self.rag = IHouseRAGAgent()
        self.web = WebSearchAgent()
        self.sum = SummarizerAgent()
        self.introspector = IntrospectionAgent()

        # Track last interaction for feedback loop
        self.last_query = None
        self.last_rag = None
        self.last_web = None
        self.last_reasoning = None

        self._init_db()

    def _extract_content(self, resp):
        """Normalize content extraction from Mistral responses."""
        if hasattr(resp, "content"):
            return resp.content
        if isinstance(resp, (list, tuple)) and resp:
            first = resp[0]
            if hasattr(first, "content"):
                return first.content
        return str(resp)

    # ------------------ DATABASE INIT ------------------
    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reflection TEXT,
            created_at TEXT
        )
        """)
        conn.commit()
        conn.close()

    # ------------------ GET RECENT REFLECTIONS ------------------
    def _load_reflections(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT reflection FROM reflections ORDER BY id DESC LIMIT 3")
        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]

    # ------------------ INTENT ANALYSIS ------------------
    def _analyze_intent(self, query):
        reflections = self._load_reflections()
        ref_prompt = "\n".join(reflections)

        prompt = f"""
You are the Intent Analyzer.

Past reflections to guide you:
{ref_prompt}

User Query: {query}

Decide what tasks are needed. Always respond as JSON like:
{{
    "intent": "...",
    "tasks": ["RAG", "WEB"]
}}
"""

        # Call Mistral chat; handle both list and single message return types
        try:
            resp = self.client.invoke([HumanMessage(content=prompt)])
            return self._extract_content(resp)
        except Exception as e:
            return f"[Intent Analyzer unavailable due to rate limit or error: {e}]"

    # ------------------ MAIN ORCHESTRATION ------------------
    def run(self, query: str):
        plan = self._analyze_intent(query)

        # For simplicity: always call both
        rag_out = self.rag.run(query)
        web_out = self.web.run(query)

        reflections = self._load_reflections()
        combined_ref = "\n".join(reflections)

        reasoning_prompt = f"""
Past improvement guidelines:
{combined_ref}

User Query: {query}

RAG Output:
{rag_out}

Web Output:
{web_out}

Provide structured reasoning for the summarizer:
"""

        try:
            reasoning_resp = self.client.invoke([HumanMessage(content=reasoning_prompt)])
            reasoning = self._extract_content(reasoning_resp)
        except Exception as e:
            reasoning = f"[Reasoning step unavailable due to rate limit or error: {e}]"

        final = self.sum.summarize(
            query=query,
            rag_output=rag_out,
            web_output=web_out,
            reasoning_output=reasoning
        )

        # Save last interaction for feedback
        self.last_query = query
        self.last_rag = rag_out
        self.last_web = web_out
        self.last_reasoning = reasoning

        return final

    # ------------------ FEEDBACK LOOP ------------------
    def handle_feedback(self, feedback: str):
        reflection = self.introspector.generate_reflection(
            query=self.last_query,
            rag_output=self.last_rag,
            web_output=self.last_web,
            reasoning_output=self.last_reasoning,
            feedback=feedback
        )

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO reflections (reflection, created_at) VALUES (?, ?)",
            (reflection, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
