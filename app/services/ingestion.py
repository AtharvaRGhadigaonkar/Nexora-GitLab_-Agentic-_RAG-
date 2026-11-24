from pathlib import Path
from typing import Iterable
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from docx import Document as DocxDocument
import fitz
import pytesseract
from PIL import Image
import io


SUPPORTED = {".pdf", ".txt", ".md", ".docx"}



def load_file(path: Path) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

        pdf = fitz.open(str(path))
        documents = []

        for page_num, page in enumerate(pdf):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image = Image.open(io.BytesIO(pix.tobytes("png")))

            text = pytesseract.image_to_string(image)

            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": str(path),
                            "page": page_num + 1
                        }
                    )
                )

        return documents
    if suffix in {".txt", ".md"}:
        return TextLoader(str(path), encoding="utf-8").load()
    if suffix == ".docx":
        doc = DocxDocument(str(path))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [Document(page_content=text, metadata={"source": str(path)})]
    raise ValueError(f"Unsupported file type: {suffix}")




def chunk_documents(docs: Iterable[Document]) -> list[Document]:
    docs = list(docs)

    print("\n[CHUNK DEBUG]")
    print("Documents received:", len(docs))

    valid_docs = []

    for i, doc in enumerate(docs):
        text = doc.page_content or ""

        print(
            f"Document {i + 1}: "
            f"Characters={len(text)}, "
            f"Source={doc.metadata.get('source', 'Unknown')}"
        )

        if text.strip():
            valid_docs.append(doc)

    print("Documents with actual text:", len(valid_docs))

    if valid_docs:
        print("\nSample extracted text:")
        print(repr(valid_docs[0].page_content[:300]))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=120,
        add_start_index=True
    )

    chunks = splitter.split_documents(valid_docs)

    print("\nChunks generated:", len(chunks))

    return chunks
