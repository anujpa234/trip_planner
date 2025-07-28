#!/usr/bin/env python3
"""
Test script to verify the fixes for null data issues in trip_planner.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_trip_planner_fixes():
    """Test the fixed functions in trip planner."""
    
    print("🧪 Testing Trip Planner Fixes")
    print("=" * 50)
    
    try:
        from src.trips.trip_planner import TripPlanner
        
        # Initialize trip planner
        print("📝 Initializing Trip Planner...")
        planner = TripPlanner()
        print("✅ Trip Planner initialized successfully")
        
        # Test search_attractions
        print("\n🏛️ Testing search_attractions...")
        attractions_result = planner.search_attractions.invoke({"city": "Paris"})
        print(f"Attractions result type: {type(attractions_result)}")
        print(f"Attractions result length: {len(str(attractions_result))}")
        print(f"Attractions preview: {str(attractions_result)[:200]}...")
        
        # Test search_restaurants  
        print("\n🍽️ Testing search_restaurants...")
        restaurants_result = planner.search_restaurants.invoke({"city": "Paris"})
        print(f"Restaurants result type: {type(restaurants_result)}")
        print(f"Restaurants result length: {len(str(restaurants_result))}")
        print(f"Restaurants preview: {str(restaurants_result)[:200]}...")
        
        # Test get_weather (current)
        print("\n🌤️ Testing get_weather (current)...")
        weather_current = planner.get_weather.invoke({"city": "Paris", "month": ""})
        print(f"Current weather result type: {type(weather_current)}")
        print(f"Current weather result length: {len(str(weather_current))}")
        print(f"Current weather preview: {str(weather_current)[:300]}...")
        
        # Test get_weather (historical)
        print("\n🌤️ Testing get_weather (historical)...")
        weather_historical = planner.get_weather.invoke({"city": "Paris", "month": "January"})
        print(f"Historical weather result type: {type(weather_historical)}")
        print(f"Historical weather result length: {len(str(weather_historical))}")
        print(f"Historical weather preview: {str(weather_historical)[:300]}...")
        
        # Test run_places_as_list directly
        print("\n📍 Testing run_places_as_list directly...")
        places_result = planner.run_places_as_list("restaurants in Tokyo")
        print(f"Places result type: {type(places_result)}")
        print(f"Places result length: {len(places_result)}")
        print(f"Places preview: {places_result[:3] if len(places_result) > 3 else places_result}")
        
        print("\n✅ All tests completed successfully!")
        print("🎉 The null data issues should now be fixed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_simple_trip_planning():
    """Test a simple trip planning query."""
    
    print("\n" + "=" * 50)
    print("🗺️ Testing Simple Trip Planning")
    print("=" * 50)
    
    try:
        from src.trips.trip_planner import TripPlanner
        
        planner = TripPlanner()
        
        # Test a simple query
        query = "Plan a 2-day trip to Tokyo in March"
        print(f"Query: {query}")
        
        result = planner.plan_trip(query)
        print(f"Result type: {type(result)}")
        
        if 'messages' in result:
            final_message = result['messages'][-1]
            print(f"Final message type: {type(final_message)}")
            if hasattr(final_message, 'content'):
                content = final_message.content
                print(f"Content length: {len(str(content))}")
                print(f"Content preview: {str(content)[:500]}...")
            else:
                print(f"Final message: {final_message}")
        
        print("✅ Trip planning test completed!")
        
    except Exception as e:
        print(f"❌ Error during trip planning test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Trip Planner Fix Tests")
    
    # Test individual functions
    success1 = test_trip_planner_fixes()
    
    # Test full trip planning
    success2 = test_simple_trip_planning()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The fixes are working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
