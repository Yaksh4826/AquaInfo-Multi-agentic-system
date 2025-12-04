# backend/agents/summarizer_agent.py
# Summarizer Agent: uses Mistral LLM to generate real summaries

import os
from mistralai import Mistral

# Read API key from environment variable
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "your key value")
MISTRAL_MODEL_NAME = "mistral-small-latest"


class SummarizerAgent:
    def __init__(self):
        if not MISTRAL_API_KEY or MISTRAL_API_KEY == "YOUR_MISTRAL_KEY_HERE":
            raise ValueError(
                "MISTRAL_API_KEY is not set. Please export it in your environment."
            )
        self.client = Mistral(api_key=MISTRAL_API_KEY)

    def summarize(self, query: str, inhouse_text: str, web_text: str, plan=None) -> str:
        """
        Uses real LLM to generate a bilingual structured summary.
        """

        system_prompt = """
        You are a Water Pollution & Quality Summarization Agent.
        Your job is to:
        - merge internal water-quality documents and web content,
        - check consistency between internal and web evidence,
        - and produce a structured answer with this structure:
          1) Background
          2) Key water-quality data
          3) Risk analysis
          4) Recommendations
        The answer MUST be bilingual: English first, then Chinese translation.
        Be concise but informative, suitable for a research analyst.
        """

        user_prompt = f"""
        USER QUESTION:
        {query}

        PLANNER PLAN (topic, focus, need_web):
        {plan}

        INTERNAL DOCUMENTS (in-house corpus):
        {inhouse_text}

        WEB CONTENT (if any):
        {web_text}

        TASK:
        - Merge the above information.
        - Resolve or explain any conflicts between internal and web data.
        - Follow the required structure.
        - Output English + Chinese (each bullet point can have EN + CN).
        """

        response = self.client.chat.complete(
            model=MISTRAL_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content

        # return response.choices[0].message["content"]
    
