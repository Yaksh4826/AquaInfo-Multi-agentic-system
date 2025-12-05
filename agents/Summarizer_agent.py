# backend/agents/summarizer_agent.py
# Summarizer Agent: uses Mistral LLM to generate real summaries

import os
from dotenv import load_dotenv
from mistralai import Mistral
import re

# Read API key from environment variable
MISTRAL_MODEL_NAME = "mistral-small-latest"


class SummarizerAgent:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("MISTRALAI_API_KEY") or os.getenv("MISTRAL_API_KEY")
        if not api_key or api_key == "YOUR_MISTRAL_KEY_HERE":
            raise ValueError(
                "MISTRALAI_API_KEY is not set. Please export it in your environment."
            )
        self.client = Mistral(api_key=api_key)

    def summarize(
        self,
        query: str,
        rag_output: str = None,
        web_output=None,
        reasoning_output: str = None,
        inhouse_text: str = None,
        web_text: str = None,
        plan=None,
    ) -> str:
        """
        Uses real LLM to generate a bilingual structured summary.
        Maintains backward compatibility with previous call signatures.
        """

        # Heuristic: if user explicitly asks for N lines/sentences, keep it tight.
        requested_lines = self._detect_requested_lines(query)

        # Prefer explicit args, but fall back to the names used by the coordinator
        inhouse_content = inhouse_text if inhouse_text is not None else (rag_output or "")

        if web_text is not None:
            web_content = web_text
        elif isinstance(web_output, dict):
            web_content = (
                web_output.get("summary")
                or web_output.get("results")
                or ""
            )
        elif web_output is not None:
            web_content = str(web_output)
        else:
            web_content = ""

        plan_text = plan if plan is not None else reasoning_output

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
        Be concise but informative, suitable for a research analyst.
        """

        user_prompt = f"""
        USER QUESTION:
        {query}

        PLANNER PLAN (topic, focus, need_web):
        {plan_text}

        INTERNAL DOCUMENTS (in-house corpus):
        {inhouse_content}

        WEB CONTENT (if any):
        {web_content}

        TASK:
        - Merge the above information.
        - Resolve or explain any conflicts between internal and web data.
        - Follow the required structure.
        - Output English 
        """

        try:
            response = self.client.chat.complete(
                model=MISTRAL_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            # Response object may expose message as attr or dict depending on SDK version
            message = response.choices[0].message
            text = message["content"] if isinstance(message, dict) else message.content
            final_text = self._enforce_line_limit(text, requested_lines)
            print(f"[SummarizerAgent] Generated summary ({len(final_text)} chars).")
            return final_text
        except Exception as e:
            # Safe fallback summary to avoid blank UI if the LLM call fails
            fallback = [
                "Summary unavailable from model; showing combined context instead.",
                f"Reason: {e}",
                "",
                "Context from internal docs:",
                inhouse_content or "(none)",
                "",
                "Context from web search:",
                web_content or "(none)",
            ]
            return "\n".join(fallback)

    @staticmethod
    def _detect_requested_lines(query: str) -> int:
        """Detect explicit 'N line' requests in the query (e.g., '2 line summary')."""
        match = re.search(r"\b(\d+)\s*line", query.lower())
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return 0
        return 0

    @staticmethod
    def _enforce_line_limit(text: str, max_lines: int) -> str:
        """Trim the summary to the requested number of sentences if specified."""
        if not max_lines or max_lines <= 0:
            return text
        # Split by sentence terminators; keep it simple.
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        trimmed = " ".join(sentences[:max_lines]).strip()
        return trimmed or text

