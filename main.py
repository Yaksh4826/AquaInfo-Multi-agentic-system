from agents.InHouseSearch_agent import IHouseRAGAgent

rag_agent = IHouseRAGAgent()

query = "what are the safest ways to drink water or maintaining the water quality"
response = rag_agent.run(query)

print("\n===== RAG ANSWER =====\n")
print(response)
print("\n=======================\n")
