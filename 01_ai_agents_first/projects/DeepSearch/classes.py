from pydantic import BaseModel
from typing import List, Optional

class IndustryInsight(BaseModel):
    industry: str
    products: Optional[List[str]] = None
    services: Optional[List[str]] = None
    revenue: Optional[str] = None  # Can also be a number if structured
    trends: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    sources: Optional[List[str]] = None  # URLs or citations
