from typing import Literal

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    messageId: str
    rating: Literal["helpful", "not_helpful"]
    comment: str | None = None
