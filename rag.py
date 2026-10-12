"""LangChain RAG: document loader -> text splitter -> embeddings -> FAISS -> retriever."""
from pathlib import Path
from functools import lru_cache
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

BASE_DIR = Path(__file__).resolve().parent
POLICY_DIR = BASE_DIR / "company_data" / "policies"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_retriever():
    documents = []
    for file_path in sorted(POLICY_DIR.glob("*.txt")):
        loaded_docs = TextLoader(str(file_path), encoding="utf-8").load()
        for doc in loaded_docs:
            doc.metadata["source"] = str(file_path.relative_to(BASE_DIR))
        documents.extend(loaded_docs)
    if not documents:
        raise FileNotFoundError(f"No policy .txt documents found in {POLICY_DIR}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

def retrieve_policy(query: str):
    docs = get_retriever().invoke(query)
    return [{"content": d.page_content, "source": d.metadata.get("source", "unknown")} for d in docs]
