import asyncio
from model.flight_search_request import FlightSearchRequest
from server.chase_travel_mcp_server import search_flights

async def test_search():
    # Test case 1: NYC to MIA
    request1 = FlightSearchRequest(
        origin="NYC",
        destination="MIA",
        departure_date="2024-03-20",
        passengers=1,
        class_type="economy"
    )
    
    results1 = await search_flights(request1)
    print("\nTest 1 - NYC to MIA:")
    for flight in results1:
        print(f"Flight {flight.flight_id}: {flight.airline} - ${flight.price}")
    
    # Test case 2: LA to LAS
    request2 = FlightSearchRequest(
        origin="LA",
        destination="LAS",
        departure_date="2024-03-20",
        passengers=2,
        class_type="economy"
    )
    
    results2 = await search_flights(request2)
    print("\nTest 2 - LA to LAS:")
    for flight in results2:
        print(f"Flight {flight.flight_id}: {flight.airline} - ${flight.price}")

if __name__ == "__main__":
    asyncio.run(test_search()) 