from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TokenData(BaseModel):
    email: str
    exp: Optional[datetime] = None
