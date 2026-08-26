from pydantic import BaseModel, ConfigDict, EmailStr


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AccessTokenResponse(BaseResponse):
    token_type: str = "Bearer"
    access_token: str
    expires_at: int
    refresh_token: str
    refresh_token_expires_at: int


class UserResponse(BaseResponse):
    user_id: str
    email: EmailStr


class ChatResponse(BaseResponse):
    answer: str
    history: list[dict[str, str | None]] = None
    conversation_id: str | None = None


class UploadResponse(BaseResponse):
    message: str
    selector_choices: str | None = None
