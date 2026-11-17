from app.rag.knowledge_base import knowledge_base


query = "What happens when I request a refund?"

result = knowledge_base.search(query)

print()
print("=" * 60)
print("RAG SEARCH RESULTS")
print("=" * 60)

for item in result["results"]:

    print()
    print("SOURCE:", item["source"])
    print("SCORE:", item["score"])
    print()
    print(item["content"])