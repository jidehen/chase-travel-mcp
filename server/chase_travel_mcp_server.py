import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from model.flight_search_request import FlightSearchRequest
from model.flight_search_response import FlightSearchResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock flight data
MOCK_FLIGHTS = [
    {
        "flight_id": "AA100",
        "airline": "American Airlines",
        "origin": "JFK",
        "destination": "MIA",
        "departure_time": "08:00",
        "arrival_time": "11:00",
        "duration": "3h 00m",
        "stops": 0,
        "price": 299.99,
        "class": "economy"
    },
    {
        "flight_id": "DL200",
        "airline": "Delta",
        "origin": "JFK",
        "destination": "MIA",
        "departure_time": "10:30",
        "arrival_time": "13:45",
        "duration": "3h 15m",
        "stops": 0,
        "price": 349.99,
        "class": "economy"
    },
    {
        "flight_id": "UA300",
        "airline": "United",
        "origin": "LAX",
        "destination": "LAS",
        "departure_time": "09:15",
        "arrival_time": "10:30",
        "duration": "1h 15m",
        "stops": 0,
        "price": 199.99,
        "class": "economy"
    },
    {
        "flight_id": "B6500",
        "airline": "JetBlue",
        "origin": "LAX",
        "destination": "LAS",
        "departure_time": "14:00",
        "arrival_time": "15:15",
        "duration": "1h 15m",
        "stops": 0,
        "price": 179.99,
        "class": "economy"
    },
    {
        "flight_id": "WN400",
        "airline": "Southwest",
        "origin": "JFK",
        "destination": "MIA",
        "departure_time": "13:00",
        "arrival_time": "16:30",
        "duration": "3h 30m",
        "stops": 1,
        "price": 249.99,
        "class": "economy"
    }
]

# City to airport mappings
CITY_AIRPORTS = {
    "NYC": ["JFK", "LGA", "EWR"],
    "LA": ["LAX", "BUR", "ONT"],
    "CHI": ["ORD", "MDW"],
    "MIA": ["MIA", "FLL"],
    "LAS": ["LAS"]
}

# Initialize FastMCP server
mcp = FastMCP("ChaseTravel")

def get_airports_for_city(city: str) -> List[str]:
    """
    Get all airports for a given city.
    
    Args:
        city: The city code (e.g., "NYC", "LA")
        
    Returns:
        List[str]: List of airport codes for the city
    """
    return CITY_AIRPORTS.get(city.upper(), [city.upper()])

def filter_flights(
    flights: List[Dict[str, Any]],
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str],
    passengers: int,
    class_type: str
) -> List[Dict[str, Any]]:
    """
    Filter flights based on search criteria.
    
    Args:
        flights: List of all available flights
        origin: Origin city code
        destination: Destination city code
        departure_date: Departure date
        return_date: Return date (optional)
        passengers: Number of passengers
        class_type: Class type (economy, business, first)
        
    Returns:
        List[Dict[str, Any]]: Filtered list of flights
    """
    origin_airports = get_airports_for_city(origin)
    dest_airports = get_airports_for_city(destination)
    
    filtered_flights = []
    for flight in flights:
        if (flight["origin"] in origin_airports and 
            flight["destination"] in dest_airports and
            flight["class"] == class_type.lower()):
            filtered_flights.append(flight)
    
    return filtered_flights

@mcp.tool()
async def search_flights(request: FlightSearchRequest) -> List[FlightSearchResponse]:
    """
    Search for flights based on the provided criteria.
    
    Args:
        request: The flight search request containing search parameters
        
    Returns:
        List[FlightSearchResponse]: List of matching flights
    """
    logger.info(f"Searching flights from {request.origin} to {request.destination}")
    
    try:
        # Filter flights based on search criteria
        matching_flights = filter_flights(
            MOCK_FLIGHTS,
            request.origin,
            request.destination,
            request.departure_date,
            request.return_date,
            request.passengers,
            request.class_type
        )
        
        # Convert to response objects
        response_flights = [
            FlightSearchResponse(
                flight_id=flight["flight_id"],
                airline=flight["airline"],
                origin=flight["origin"],
                destination=flight["destination"],
                departure_time=flight["departure_time"],
                arrival_time=flight["arrival_time"],
                duration=flight["duration"],
                stops=flight["stops"],
                price=flight["price"],
                class_type=flight["class"]
            )
            for flight in matching_flights
        ]
        
        logger.info(f"Found {len(response_flights)} matching flights")
        return response_flights
        
    except Exception as e:
        error_msg = f"Error searching flights: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return []

if __name__ == "__main__":
    logger.info("Starting ChaseTravel MCP server")
    mcp.run() 