from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import os

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../../../../data/chroma_store")

# Load embedding model once (runs locally, no API needed)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def store_products(products: list[dict], session_id: str) -> Chroma:
    """Embed product data and store in ChromaDB."""
    docs = []
    for p in products:
        content = f"{p.get('name', '')} {p.get('description', '')} {str(p.get('specs', {}))}"
        docs.append(Document(
            page_content=content,
            metadata={"name": p.get("name", ""), "session_id": session_id}
        ))

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=f"session_{session_id}"
    )
    return vectorstore

def retrieve_similar(query: str, session_id: str, k: int = 5) -> list[Document]:
    """Retrieve top-k similar products for a query."""
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=f"session_{session_id}"
    )
    return vectorstore.similarity_search(query, k=k)