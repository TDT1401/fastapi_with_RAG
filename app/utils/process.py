from datetime import datetime

from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def pdf_extract(pdf_path: str) -> list[Document]:
    print("PDF file text is extracted =============================+>>>>>>>>>>>>>>>")
    loader = PyPDFLoader(pdf_path)
    pdf_text = loader.load()

    return pdf_text


def pdf_chunk(pdf_text: list[Document]) -> list[Document]:
    try:
        print("PDF file text is chunked =============================+>>>>>>>>>>>>>>>")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        chunks = text_splitter.split_documents(pdf_text)

        return chunks
    except Exception as e:
        print(f"Error in pdf_chunk: {e}")
        return []


def wp_text(page_url: str) -> list[Document]:
    try:
        print("Extracting web page text...")
        loader = WebBaseLoader(page_url)
        documents = loader.load()
        return documents
    except Exception as e:
        print(f"Error in wp_text: {e}")
        return []


def wp_chunk(webpage_text: list[Document]) -> list[Document]:
    print("Chunking web page text...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_documents(webpage_text)


def md_extract(markdown_path: str) -> list[Document]:
    print("Markdown file text is extracted =============================+>>>>>>>>>>>>>")
    loader = TextLoader(markdown_path, encoding="utf-8")
    return loader.load()


def md_chunk(markdown_text: list[Document]) -> list[Document]:
    print("Markdown file text is chunked =============================+>>>>>>>>>>>>>>>")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_documents(markdown_text)


def generate_conversation_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
