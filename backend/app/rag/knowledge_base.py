import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

load_dotenv()


class KnowledgeBase:

    COLLECTION_NAME = "supportflow_knowledge"
    EMBEDDING_MODEL = "gemini-embedding-001"
    VECTOR_SIZE = 768

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        # Local Qdrant database
        self.qdrant = QdrantClient(
            path="qdrant_data"
        )

        self.knowledge_path = Path(
            "data/knowledge"
        )

        self._create_collection()

    # ========================================================
    # CREATE COLLECTION
    # ========================================================

    def _create_collection(self):

        collections = self.qdrant.get_collections()

        existing_names = [
            collection.name
            for collection in collections.collections
        ]

        if self.COLLECTION_NAME not in existing_names:

            self.qdrant.create_collection(

                collection_name=self.COLLECTION_NAME,

                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    # ========================================================
    # GENERATE EMBEDDING
    # ========================================================

    def _embed(
        self,
        text: str,
        task_type: str,
    ):

        response = self.client.models.embed_content(

            model=self.EMBEDDING_MODEL,

            contents=text,

            config={
                "task_type": task_type,
                "output_dimensionality": self.VECTOR_SIZE,
            },
        )

        return response.embeddings[0].values

    # ========================================================
    # LOAD DOCUMENTS
    # ========================================================

    def load_documents(self):

        if not self.knowledge_path.exists():

            raise FileNotFoundError(
                f"Knowledge directory not found: "
                f"{self.knowledge_path}"
            )

        documents = list(
            self.knowledge_path.glob("*.txt")
        )

        if not documents:

            raise ValueError(
                "No knowledge-base documents found."
            )

        points = []

        point_id = 1

        for file_path in documents:

            text = file_path.read_text(
                encoding="utf-8"
            ).strip()

            if not text:
                continue

            vector = self._embed(
                text,
                "RETRIEVAL_DOCUMENT",
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "source": file_path.name,
                        "content": text,
                    },
                )
            )

            point_id += 1

        if points:

            self.qdrant.upsert(

                collection_name=self.COLLECTION_NAME,

                points=points,
            )

        return {
            "success": True,
            "documents_loaded": len(points),
        }

    # ========================================================
    # SEARCH KNOWLEDGE BASE
    # ========================================================

    def search(
        self,
        query: str,
        limit: int = 3,
    ):

        query_vector = self._embed(
            query,
            "RETRIEVAL_QUERY",
        )

        results = self.qdrant.query_points(

            collection_name=self.COLLECTION_NAME,

            query=query_vector,

            limit=limit,

        ).points

        matches = []

        for result in results:

            matches.append(
                {
                    "source": result.payload.get(
                        "source"
                    ),
                    "content": result.payload.get(
                        "content"
                    ),
                    "score": result.score,
                }
            )

        return {
            "success": True,
            "results": matches,
        }


knowledge_base = KnowledgeBase()