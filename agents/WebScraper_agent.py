from typing import Dict, Any, List
from tools.web_search_tool import WebSearchTool


class WebSearchAgent:


    def __init__(self) -> None:
        self.name = "Web Search Agent"
        self.tool = WebSearchTool()

    def run(self, query: str) -> Dict[str, Any]:
       
        raw_results: List[Dict[str, str]] = self.tool.search(query)

        summary_lines = [f"Web search results for: '{query}'"]
        for idx, res in enumerate(raw_results, start=1):
            summary_lines.append(
                f"{idx}. {res['title']} — {res['snippet']} "
                f"(source: {res['url']})"
            )

        summary_text = "\n".join(summary_lines)

        return {
            "agent": "web_search",
            "query": query,
            "results": raw_results,
            "summary": summary_text,
        }


if __name__ == "__main__":
    agent = WebSearchAgent()
    demo = agent.run("Explain nitrate pollution in water")
    print(demo["summary"])
