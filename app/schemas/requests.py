from typing import Literal

from pydantic import BaseModel, EmailStr


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str


class UserCreateRequest(BaseRequest):
    email: EmailStr
    password: str


class ChatRequest(BaseRequest):
    user_id: str
    chat_input: str
    selector_choices: str
    reasoning_type: Literal["wp", "pdf", "md"] = "wp"
    conversation_id: str = None


class UploadRequest(BaseModel):
    file_path: str
