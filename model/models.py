from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union


class TripParams(BaseModel):
    city: str = Field(description="The primary city or destination (e.g., Delhi). Infer if not explicit.")
    country: Optional[str] = Field(description="Country, default to Italy if not specified.")
    duration: Optional[str] = Field(default="1 week", description="Trip length (e.g., '1 week', '3 days'). Infer reasonable default if missing.")
    month: Optional[str] = Field(description="Month or season of travel (e.g., 'July', 'June-August'). Infer from seasons.")
    start_date: Optional[str] = Field(description="Inferred start date in YYYY-MM-DD, based on current date if vague.")
    currency: Optional[str] = Field(description="Currency code for target currency which user want to covert.")

    