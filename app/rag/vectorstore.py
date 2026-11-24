
import time
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import get_settings

print("[DEBUG] Loading application settings...")

settings = get_settings()

print("[DEBUG] Settings loaded successfully.")
print(f"[DEBUG] Embedding model configured: {settings.embedding_model}")
print(f"[DEBUG] Pinecone index: {settings.pinecone_index_name}")
print(f"[DEBUG] Pinecone namespace: {settings.pinecone_namespace}")


_embeddings = None
_vectorstore = None


EMBEDDING_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
    "all-minilm-l6-v2": 384
}

def check_index_stats():
    index = ensure_index()
    stats = index.describe_index_stats()

    print("Total vectors:", stats.total_vector_count)
    print("Namespaces:", stats.namespaces)

    
def get_embedding_dimension(model_name: str | None = None) -> int:
    print("\n[DEBUG] Entering get_embedding_dimension()")

    name = (model_name or settings.embedding_model or "").strip()

    print(f"[DEBUG] Model name received: {name}")

    if not name:
        raise RuntimeError("Embedding model is not configured")

    normalized = name.lower()

    if normalized in EMBEDDING_DIMENSIONS:
        dimension = EMBEDDING_DIMENSIONS[normalized]
        print(f"[DEBUG] Exact model match. Dimension: {dimension}")
        return dimension

    if "text-embedding-3-small" in normalized:
        print("[DEBUG] Matched text-embedding-3-small")
        return 1536

    if "text-embedding-3-large" in normalized:
        print("[DEBUG] Matched text-embedding-3-large")
        return 3072

    if "text-embedding-ada-002" in normalized:
        print("[DEBUG] Matched text-embedding-ada-002")
        return 1536

    if "all-minilm" in normalized:
        print("[DEBUG] Matched all-MiniLM model")
        return 384

    raise ValueError(
        f"Unsupported embedding model '{model_name or settings.embedding_model}' for Pinecone. "
        "Add the matching dimension to EMBEDDING_DIMENSIONS."
    )


def get_embeddings():
    global _embeddings

    print("\n[DEBUG] Entering get_embeddings()")

    if _embeddings is None:

        print("[DEBUG] Embedding model not initialized. Initializing now...")

        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is missing")

        print("[DEBUG] GROQ_API_KEY exists.")

        try:
            print("[DEBUG] Loading HuggingFace embedding model...")

            _embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                encode_kwargs={"normalize_embeddings": True},
            )

            print("[DEBUG] HuggingFace embedding model loaded successfully.")

            # Test embedding generation
            print("[DEBUG] Testing embedding generation...")

            test_embedding = _embeddings.embed_query("NEXORA test query")

            print("[DEBUG] Test embedding generated successfully.")
            print(f"[DEBUG] Embedding dimension: {len(test_embedding)}")

        except Exception as e:
            print(f"[ERROR] Embedding initialization failed: {type(e).__name__}: {e}")
            raise

    else:
        print("[DEBUG] Using cached embedding model.")

    return _embeddings


def ensure_index():
    print("\n[DEBUG] Entering ensure_index()")

    if not settings.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY is missing")

    print("[DEBUG] PINECONE_API_KEY exists.")

    try:
        print("[DEBUG] Checking expected embedding dimension...")

        desired_dimension = get_embedding_dimension()

        print(f"[DEBUG] Expected Pinecone dimension: {desired_dimension}")

        print("[DEBUG] Connecting to Pinecone...")

        pc = Pinecone(api_key=settings.pinecone_api_key)

        print("[DEBUG] Pinecone client initialized.")

        print("[DEBUG] Fetching existing indexes...")

        names = [x["name"] for x in pc.list_indexes()]

        print(f"[DEBUG] Existing indexes: {names}")

        if settings.pinecone_index_name in names:

            print("[DEBUG] Requested index already exists.")

            index_info = pc.describe_index(settings.pinecone_index_name)

            print(f"[DEBUG] Index information: {index_info}")

            current_dimension = getattr(index_info, "dimension", None)

            if current_dimension is None and isinstance(index_info, dict):
                current_dimension = index_info.get("dimension")

            print(f"[DEBUG] Current index dimension: {current_dimension}")

            if current_dimension is not None and current_dimension != desired_dimension:

                print("[WARNING] Dimension mismatch detected!")
                print("[WARNING] Deleting existing Pinecone index...")

                pc.delete_index(name=settings.pinecone_index_name)

                print("[DEBUG] Waiting for index deletion...")

                while settings.pinecone_index_name in [
                    x["name"] for x in pc.list_indexes()
                ]:
                    time.sleep(1)

                print("[DEBUG] Old index deleted successfully.")

        if settings.pinecone_index_name not in [
            x["name"] for x in pc.list_indexes()
        ]:

            print("[DEBUG] Index does not exist. Creating new index...")

            print("Pinecone index:", settings.pinecone_index_name)

            pc.create_index(
                name=settings.pinecone_index_name,
                dimension=desired_dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

            print("[DEBUG] Index creation request submitted.")
            print("[DEBUG] Waiting for index to become ready...")

            while not pc.describe_index(
                settings.pinecone_index_name
            ).status["ready"]:
                time.sleep(1)

            print("[DEBUG] Pinecone index is READY.")

        else:
            print("[DEBUG] Existing index has matching configuration.")

        print("[DEBUG] Connecting to Pinecone index...")

        index = pc.Index(settings.pinecone_index_name)

        print("[DEBUG] Pinecone index connection successful.")

        return index

    except Exception as e:
        print(f"[ERROR] ensure_index() failed: {type(e).__name__}: {e}")
        raise


def get_vectorstore():
    global _vectorstore

    print("\n[DEBUG] Entering get_vectorstore()")

    if _vectorstore is None:

        print("[DEBUG] Vector store not initialized.")

        try:
            print("[DEBUG] Calling ensure_index()...")

            index = ensure_index()

            print("[DEBUG] Pinecone index obtained.")

            print("[DEBUG] Calling get_embeddings()...")

            embeddings = get_embeddings()

            print("[DEBUG] Embeddings obtained.")

            print("[DEBUG] Initializing PineconeVectorStore...")

            _vectorstore = PineconeVectorStore(
                index=index,
                embedding=embeddings,
                namespace=settings.pinecone_namespace,
            )

            print("[DEBUG] PineconeVectorStore initialized successfully.")

        except Exception as e:
            print(f"[ERROR] get_vectorstore() failed: {type(e).__name__}: {e}")
            raise

    else:
        print("[DEBUG] Using cached vector store.")

    return _vectorstore


def get_retriever():
    print("\n[DEBUG] Entering get_retriever()")

    try:
        print("[DEBUG] Getting vector store...")

        retriever = get_vectorstore().as_retriever(
            search_kwargs={"k": settings.top_k}
        )

        print(f"[DEBUG] Retriever created successfully. Top K: {settings.top_k}")

        return retriever

    except Exception as e:
        print(f"[ERROR] get_retriever() failed: {type(e).__name__}: {e}")
        raise


def add_documents(chunks):
    print("\n[DEBUG] Entering add_documents()")

    print(f"[DEBUG] Number of chunks received: {len(chunks)}")

    try:
        print("[DEBUG] Getting vector store...")

        store = get_vectorstore()

        print("[DEBUG] Vector store obtained.")

        print("[DEBUG] Adding documents to Pinecone...")

        result = store.add_documents(chunks)

        print("[DEBUG] Documents added successfully.")
        print(f"[DEBUG] Pinecone result: {result}")

        return result

    except Exception as e:
        print(f"[ERROR] add_documents() failed: {type(e).__name__}: {e}")
        raise
