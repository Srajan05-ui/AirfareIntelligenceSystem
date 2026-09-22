from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class RawFareObservation(BaseModel):
    source_tier: str = Field(..., description="Source of the data (e.g., tier1_googleflights)")
    origin: str = Field(..., max_length=3, description="IATA code for origin")
    destination: str = Field(..., max_length=3, description="IATA code for destination")
    departure_date: str = Field(..., description="YYYY-MM-DD")
    airline: str = Field(..., description="Operating airline name")
    flight_number: Optional[str] = Field(None, description="Flight number if available")
    departure_time: str = Field(..., description="Local departure time")
    arrival_time: str = Field(..., description="Local arrival time")
    price: float = Field(..., description="Price in INR")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO8601 UTC timestamp of scrape")
    
    @validator('origin', 'destination')
    def uppercase_iata(cls, v):
        return v.upper()

    @validator('price')
    def check_price(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v
