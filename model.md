from langchain_ollama import OllamaEmbeddings, ChatOllama

llm = ChatOllama(
model="llama3.2"
)

embeddings = OllamaEmbeddings(
model="nomic-embed-text"
)
