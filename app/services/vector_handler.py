import os

from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

from app.utils.process import (
    md_chunk,
    md_extract,
    pdf_chunk,
    pdf_extract,
    wp_chunk,
    wp_text,
)

EMBEDDING_MODEL = "nomic-embed-text"


def get_embedding_model() -> OllamaEmbeddings:
    return OllamaEmbeddings(model=EMBEDDING_MODEL)


def create_vector_store_pdf(file_path: str, db_path: str) -> str:
    print(
        "Creating a new vector store from PDF =============================+>>>>>>>>>>>>>>>"
    )
    try:
        if not os.path.exists(db_path):
            text = pdf_extract(file_path)
            chunks = pdf_chunk(text)
            embedding_model = get_embedding_model()
            Chroma.from_documents(
                documents=chunks, embedding=embedding_model, persist_directory=db_path
            )
            return "Document created successfully."
        else:
            return "Document already exists."
    except Exception as e:
        print(f"Error in create_vector_store_if_needed: {e}")
        return "Error creating vector store."


def create_vector_store_wp(file_path: str, db_path: str) -> str:
    print(
        "Creating a new vector store from PDF =============================+>>>>>>>>>>>>>>>"
    )
    try:
        if not os.path.exists(db_path):
            text = wp_text(file_path)
            chunks = wp_chunk(text)
            embedding_model = get_embedding_model()
            Chroma.from_documents(
                documents=chunks, embedding=embedding_model, persist_directory=db_path
            )
            return "Document created successfully."
        else:
            return "Document already exists."
    except Exception as e:
        print(f"Error in create_vector_store_if_needed: {e}")
        return "Error creating vector store."


def create_vector_store_md(file_path: str, db_path: str) -> str:
    print(
        "Creating a new vector store from Markdown =======================+>>>>>>>>>>>>"
    )
    try:
        if not os.path.exists(db_path):
            text = md_extract(file_path)
            chunks = md_chunk(text)
            embedding_model = get_embedding_model()
            Chroma.from_documents(
                documents=chunks, embedding=embedding_model, persist_directory=db_path
            )
            return "Document created successfully."
        return "Document already exists."
    except Exception as e:
        print(f"Error in create_vector_store_md: {e}")
        return "Error creating vector store."


def load_vector_store(selector_choices: str, reasoning_type: str) -> Chroma:
    print("Loading vector store =============================+>>>>>>>>>>>>>>>")
    seletor = "chroma_db_" + reasoning_type + "_ollama"
    db_path = os.path.join("db", seletor, selector_choices)
    embedding_model = get_embedding_model()
    return Chroma(persist_directory=db_path, embedding_function=embedding_model)
