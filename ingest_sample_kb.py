# from pathlib import Path
# from app.core.config import get_settings
# from app.services.ingestion import load_file, chunk_documents
# from app.rag.vectorstore import add_documents

# settings = get_settings()

# folder = Path(settings.sample_kb_dir)
# files = [p for p in folder.iterdir() if p.is_file()]

# all_docs = [] 

# for path in files:
#     all_docs.extend(load_file(path))
# chunks = chunk_documents(all_docs)
# ids = add_documents(chunks)
# print(f"Indexed {len(files)} files -> {len(chunks)} chunks -> {len(ids)} Pinecone vectors")



from pathlib import Path

from app.core.config import get_settings
from app.services.ingestion import load_file, chunk_documents
from app.rag.vectorstore import add_documents

settings = get_settings()

folder = Path(settings.sample_kb_dir)

print("\nKnowledge base folder:", folder.resolve())

if not folder.exists():
    raise FileNotFoundError(f"Folder not found: {folder}")

files = [p for p in folder.rglob("*") if p.is_file()]

print("Files found:", len(files))

all_docs = []

for path in files:
    print(f"\nLoading: {path.name}")

    try:
        docs = load_file(path)
        print("Documents extracted:", len(docs))
        all_docs.extend(docs)
    except Exception as e:
        print(f"ERROR loading {path.name}: {e}")

print("\nTotal documents:", len(all_docs))

chunks = chunk_documents(all_docs)

print("Total chunks:", len(chunks))

if not chunks:
    raise RuntimeError("No chunks generated. Check load_file() and chunk_documents().")

ids = add_documents(chunks)

print(f"\nSuccessfully indexed {len(ids)} vectors.")
