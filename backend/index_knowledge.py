from app.rag.knowledge_base import knowledge_base


result = knowledge_base.load_documents()

print()
print("=" * 60)
print("SUPPORTFLOW KNOWLEDGE BASE")
print("=" * 60)
print()
print(result)
print()
print("Knowledge base indexing complete.")