import os
from urllib.parse import urlparse

from fastapi import APIRouter, status

from app.schemas.requests import ChatRequest, UploadRequest
from app.schemas.responses import ChatResponse, UploadResponse
from app.services.rag_chain import build_rag_chain
from app.services.vector_handler import create_vector_store_pdf, create_vector_store_wp
from app.utils.process import generate_conversation_id
from app.utils.save_history import load_chat_history, save_chat_history

PERSISTENT_DIRECTORY = os.path.join("db")


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    description="Send message to chatbot and receive reply.",
)
async def chatbot_reply(data: ChatRequest) -> ChatResponse:
    user_id = data.user_id
    conversation_id = data.conversation_id
    chat_input_text = data.chat_input

    if not conversation_id:
        conversation_id = generate_conversation_id()

    # load history
    chat_history = load_chat_history(user_id, conversation_id)

    print(f"Chat history: {chat_history}")
    # save history
    if chat_input_text:
        chat_history.append((chat_input_text, None))
    elif not chat_history:
        return ChatResponse(reply="Please enter a question.")

    # create answer
    rag_chain = build_rag_chain()
    result = rag_chain.invoke(
        {
            "selector_choices": data.selector_choices,
            "chat_input": data.chat_input,
            "reasoning_type": data.reasoning_type,
        }
    )
    # save history response
    chat_history[-1] = (chat_history[-1][0], result)

    # save history to file
    save_chat_history(chat_history, user_id, conversation_id)

    chat_history_for_response = [{"user": u, "bot": b} for u, b in chat_history]
    return ChatResponse(
        answer=result,
        history=chat_history_for_response,
        conversation_id=conversation_id,
    )


@router.post(
    "/upload/pdf",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    description="Upload document to chatbot.",
)
async def upload_doc(data: UploadRequest) -> UploadResponse:
    try:
        file_id = os.path.splitext(os.path.basename(data.file_path))[0]
        db_path = os.path.join("db", "chroma_db_pdf_ollama", file_id)
        status = create_vector_store_pdf(data.file_path, db_path)
        print(f"Status: {status}")
        return UploadResponse(message=status)
    except Exception:
        return UploadResponse(message=status)


@router.post(
    "/upload/wp",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    description="Upload website to chatbot.",
)
async def upload_website(data: UploadRequest) -> UploadResponse:
    try:
        parsed_url = urlparse(data.file_path)
        website_name = parsed_url.netloc.replace("www.", "").replace(".", "_")

        db_path = os.path.join("db", "chroma_db_wp_ollama", website_name)
        status = create_vector_store_wp(data.file_path, db_path)
        print(f"Status: {status}")
        return UploadResponse(message=status)
    except Exception:
        return UploadResponse(message=status)
