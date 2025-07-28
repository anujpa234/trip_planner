#!/usr/bin/env python3
"""
Test script for the fixed TripPlanner class.
This demonstrates how to use the trip planner with proper OOP structure.
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.trips.trip_planner import TripPlanner
from langchain_core.messages import HumanMessage

def test_trip_planner():
    """Test the trip planner functionality."""
    
    print("🚀 Testing Trip Planner...")
    print("=" * 50)
    
    try:
        # Initialize the trip planner
        print("1. Initializing Trip Planner...")
        planner = TripPlanner()
        print("✅ Trip Planner initialized successfully!")
        
        # Test query
        test_query = "I want to plan a 5-day trip to Paris in July. I'm interested in attractions, good restaurants, and weather information. My budget is 500 EUR and I want to convert it to USD."
        
        print(f"\n2. Testing with query: '{test_query}'")
        print("-" * 50)
        
        # Plan the trip
        result = planner.plan_trip(test_query)
        
        print("\n3. Trip Planning Results:")
        print("-" * 30)
        
        # Display results
        if result and "messages" in result:
            for i, message in enumerate(result["messages"]):
                print(f"Message {i+1}: {type(message).__name__}")
                if hasattr(message, 'content'):
                    print(f"Content: {message.content[:200]}...")
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    print(f"Tool calls: {len(message.tool_calls)}")
                print()
        
        if result and "params" in result and result["params"]:
            print("Extracted Parameters:")
            print(f"- City: {result['params'].city}")
            print(f"- Duration: {result['params'].duration}")
            print(f"- Month: {result['params'].month}")
            print(f"- Currency: {result['params'].currency}")
        
        print("✅ Trip planning completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

def test_individual_tools():
    """Test individual tools separately."""
    
    print("\n🔧 Testing Individual Tools...")
    print("=" * 50)
    
    try:
        planner = TripPlanner()
        
        # Test each tool
        print("1. Testing search_attractions...")
        attractions = planner.search_attractions("Paris")
        print(f"Result: {attractions}")
        
        print("\n2. Testing search_restaurants...")
        restaurants = planner.search_restaurants("Paris")
        print(f"Result: {restaurants}")
        
        print("\n3. Testing get_weather...")
        weather = planner.get_weather("Paris")
        print(f"Result: {weather}")
        
        print("\n4. Testing currency_exchange...")
        exchange = planner.currency_exchange(500.0, "EUR", "USD")
        print(f"Result: {exchange}")
        
        print("\n✅ All tools tested successfully!")
        
    except Exception as e:
        print(f"❌ Error testing tools: {str(e)}")
        import traceback
        traceback.print_exc()

def test_workflow_structure():
    """Test the workflow structure."""
    
    print("\n🏗️ Testing Workflow Structure...")
    print("=" * 50)
    
    try:
        planner = TripPlanner()
        
        # Check if workflow is properly built
        if hasattr(planner, 'react_graph'):
            print("✅ Workflow graph exists")
            
            # Check tools
            if hasattr(planner, 'tools') and planner.tools:
                print(f"✅ Tools loaded: {len(planner.tools)} tools")
                for i, tool in enumerate(planner.tools):
                    print(f"   - Tool {i+1}: {tool.name}")
            else:
                print("❌ No tools found")
            
            # Check methods
            required_methods = ['extract_params', 'react_agent', 'should_continue', 'plan_trip']
            for method in required_methods:
                if hasattr(planner, method):
                    print(f"✅ Method '{method}' exists")
                else:
                    print(f"❌ Method '{method}' missing")
        else:
            print("❌ Workflow graph not found")
            
    except Exception as e:
        print(f"❌ Error testing workflow: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Trip Planner Test Suite")
    print("=" * 60)
    
    # Run tests
    # test_workflow_structure()
    #test_individual_tools()
    test_trip_planner()
    
    print("\n🎉 Testing completed!")
