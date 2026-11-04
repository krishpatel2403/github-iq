from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    github_id: int
    username: str
    email: str | None = None

    model_config = {"from_attributes": True}
