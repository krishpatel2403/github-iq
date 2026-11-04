from typing import Optional

from pydantic import BaseModel


class UserProfile(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}
