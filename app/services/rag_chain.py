from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama

from .vector_handler import load_vector_store

LLM_MODEL = "llama3.2"
template = """ You are an AI model trained for question answering. You should answer the
given question based on the given context only.

Question : {query}
\n
Context : {context}
\n
If the answer is not present in the given context, respond as: 
'The answer to this question is not available in the provided content.'
"""
RAG_PROMPT_PDF = PromptTemplate.from_template(template)


def retrieve_context(db, query: str) -> str:
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    print("Retrieving relevant chunks =============================+>>>>>>>>>>>>>>>")
    chunks = retriever.invoke(query)
    return "\n\n".join([chunk.page_content for chunk in chunks])


def get_context(inputs: dict[str, str]) -> dict[str, str]:
    print("Getting context =============================+>>>>>>>>>>>>>>>")
    print(f"Inputs: {inputs}")
    selector_choices = inputs["selector_choices"]
    reasoning_type = inputs["reasoning_type"]
    db = load_vector_store(selector_choices, reasoning_type)
    context = retrieve_context(db, inputs["chat_input"])
    return {"context": context, "query": inputs["chat_input"]}


def build_rag_chain():
    llm = ChatOllama(model=LLM_MODEL)
    str_parser = StrOutputParser()
    return RunnableLambda(get_context) | RAG_PROMPT_PDF | llm | str_parser
