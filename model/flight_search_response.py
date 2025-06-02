from pydantic import BaseModel

class FlightSearchResponse(BaseModel):
    """
    Response model for flight search results.
    """
    flight_id: str
    airline: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    stops: int
    price: float
    class_type: str 