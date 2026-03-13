import json
from database.local_db import LocalDB

from agents.WebScraper_agent import WebScraper_agent
from agents.InHouseSearch_agent import InHouseSearch_agent
from agents.Summarizer_agent import SummarizerAgent
from agents.Introspection_Agent import IntrospectionAgent


class CoordinatorAgent:
    """
    For the AquaInfo multi-agent system,
    Routes queries, triggers agents, coordinates output,
    performs introspection, and stores memory.
    """

    def __init__(self, db_path="memory.db"):
        # Initialize local database
        self.db = LocalDB(db_path)

        # Initialize agents
        self.web_agent = WebScraper_agent()
        self.inhouse_agent = InHouseSearch_agent()
        self.summarizer = SummarizerAgent()
        self.introspector = IntrospectionAgent(db_path=db_path)

    def handle_query(self, user_query: str, user_feedback: str = None):
        """
        Process a full query-response.
        """

        # Save user raw query
        self.db.save_user_query(user_query)

        # INTENT ANALYSIS
        intent_result = self.intent_agent.analyze(user_query)
        task_type = intent_result.get("task_type")

        # ROUTE TASK
        if task_type == "web_search":
            agent_output = self.web_agent.run(user_query)

        elif task_type == "inhouse_search":
            agent_output = self.inhouse_agent.query(user_query)

        elif task_type == "reasoning":
            agent_output = self.intent_agent.deep_reason(user_query)

        final_answer = self.summarizer.summarize(agent_output)
        self.db.save_summary(final_answer)

        reflection_data = self.introspector.run(
            query=user_query,
            answer=final_answer,
            feedback=user_feedback
        )

        return {
            "final_answer": final_answer,
            "reflection": reflection_data
        }
