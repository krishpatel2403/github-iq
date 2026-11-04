from pydantic import BaseModel


class SyncTrigger(BaseModel):
    force: bool = False
