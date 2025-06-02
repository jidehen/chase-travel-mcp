import logging
from typing import List, Dict, Any
import sys
from pathlib import Path
import json
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from model.flight_search_request import FlightSearchRequest
from model.flight_search_response import FlightSearchResponse, Flight

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock flight data
MOCK_FLIGHTS = {
    "JFK-LHR": [
        {
            "airline": "British Airways",
            "flight_number": "BA178",
            "departure_time": "10:00",
            "arrival_time": "22:00",
            "price": 800.00,
            "class": "economy"
        },
        {
            "airline": "American Airlines",
            "flight_number": "AA100",
            "departure_time": "11:00",
            "arrival_time": "23:00",
            "price": 850.00,
            "class": "economy"
        },
        {
            "airline": "United Airlines",
            "flight_number": "UA880",
            "departure_time": "12:00",
            "arrival_time": "00:00",
            "price": 900.00,
            "class": "economy"
        },
        {
            "airline": "Delta",
            "flight_number": "DL400",
            "departure_time": "13:00",
            "arrival_time": "01:00",
            "price": 950.00,
            "class": "economy"
        }
    ]
}

# Initialize FastMCP server
mcp = FastMCP("ChaseTravel")

class TravelSearchError(Exception):
    """Custom exception for travel search errors."""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

def search_flights_internal(origin: str, destination: str) -> List[Dict[str, Any]]:
    """
    Search for flights between two cities.
    
    Args:
        origin: Origin city code
        destination: Destination city code
        
    Returns:
        List[Dict[str, Any]]: List of available flights
        
    Raises:
        TravelSearchError: If route not found or other errors occur
    """
    logger.info(f"Processing flight search request: {origin} -> {destination}")
    
    if not origin or not destination:
        raise TravelSearchError(
            "Missing origin or destination",
            "MISSING_ROUTE_INFO",
            {"required": "Both origin and destination must be provided"}
        )
    
    route = f"{origin}-{destination}"
    if route not in MOCK_FLIGHTS:
        raise TravelSearchError(
            f"No flights found for route {route}",
            "ROUTE_NOT_FOUND",
            {
                "invalid_route": route,
                "available_routes": list(MOCK_FLIGHTS.keys())
            }
        )
    
    flights = MOCK_FLIGHTS[route]
    logger.info(f"Found {len(flights)} flights for route {route}")
    return flights

async def search_flights(request: FlightSearchRequest) -> FlightSearchResponse:
    """
    Search for flights between two cities.
    
    Args:
        request: The flight search request containing origin and destination
        
    Returns:
        FlightSearchResponse: The flight search response
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Received flight search request: {request.origin} -> {request.destination}")
    
    try:
        flights = search_flights_internal(request.origin, request.destination)
        
        response_flights = [
            Flight(
                airline=flight["airline"],
                flight_number=flight["flight_number"],
                departure_time=flight["departure_time"],
                arrival_time=flight["arrival_time"],
                price=flight["price"],
                class_type=flight["class"]
            )
            for flight in flights
        ]
        
        response = FlightSearchResponse(flights=response_flights)
        logger.info(f"[{request_id}] Successfully processed request. Found {len(response_flights)} flights")
        return response
        
    except TravelSearchError as e:
        logger.error(f"[{request_id}] Travel search error: {str(e)}", exc_info=True)
        raise TravelSearchError(
            e.message,
            e.error_code,
            {
                **e.details,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}", exc_info=True)
        raise TravelSearchError(
            "An unexpected error occurred while processing the request",
            "INTERNAL_ERROR",
            {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

# Register MCP tool
@mcp.tool()
async def search_flights_tool(request: FlightSearchRequest) -> FlightSearchResponse:
    """MCP tool for searching flights."""
    return await search_flights(request)

if __name__ == "__main__":
    logger.info("Starting Chase Travel MCP server")
    mcp.run() 