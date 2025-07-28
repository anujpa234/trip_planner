import os
import sys
import requests
import json
import datetime
import time
import calendar
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import TripPlannerPortalException
from langchain.output_parsers import OutputFixingParser
from typing import List, Optional, TypedDict, Annotated
from operator import add
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage, AnyMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_community.tools import GooglePlacesTool
from model.models import *
from prompt.prompt_library import *

class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add]
    params: Optional[TripParams]

class TripPlanner:
    """
    Trip planner using ReAct pattern with LangGraph.
    Analyzes user queries and creates comprehensive trip plans.
    """
    
    def __init__(self):
        """Initialize the trip planner with all necessary components."""
        self.log = CustomLogger().get_logger(__name__)
        try:
            # Initialize core components
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()
            
            # Prepare parsers
            self.parser = PydanticOutputParser(pydantic_object=TripParams)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
            
            # Initialize prompts
            self.prompt = prompt
            self.prompt_tripmaker = prompt_tripmaker
            
            # Define tools as instance methods
            self._setup_tools()
            
            # Build the workflow graph
            self._build_workflow()
            
            self.log.info("Trip planner initialized successfully")
            
        except Exception as e:
            self.log.error(f"Error initializing Trip planner: {e}")
            raise TripPlannerPortalException("Error in Trip planner initialization", sys)
    
    def _setup_tools(self):
        """Setup all the tools needed for trip planning."""
        
        @tool
        def search_attractions(city: str) -> str:
            """Search for attractions in a city."""
            try:
                query = f"top tourist attractions monuments museums sightseeing places in {city}"
                print(f"Search attraction query: {query} \n")
                # call google places function to fetch the list of attractions
                attractions = self.run_places_as_list(query)
                
                # Validate and return the results
                if attractions and len(attractions) > 0:
                    return "\n".join(attractions)
                else:
                    return f"No attractions found for {city}. Please try a different city or check your internet connection."
                    
            except Exception as e:
                self.log.error(f"Error searching attractions for {city}: {str(e)}")
                return f"Error searching attractions for {city}: {str(e)}"
        
        @tool
        def search_restaurants(city: str) -> str:
            """Search for restaurants in a city."""
            try:
                query = f"best restaurants cafes local food dining places in {city}"
                print(f"Search restaurant query: {query}\n")
                # call google places function to fetch the list of restaurants
                restaurants = self.run_places_as_list(query)
                
                # Validate and return the results
                if restaurants and len(restaurants) > 0:
                    return "\n".join(restaurants)
                else:
                    return f"No restaurants found for {city}. Please try a different city or check your internet connection."
                    
            except Exception as e:
                self.log.error(f"Error searching restaurants for {city}: {str(e)}")
                return f"Error searching restaurants for {city}: {str(e)}"
        
        @tool
        def get_weather(city: str, month: str) -> str:
            """Get weather report for a city."""
            try:
                # Check if month is provided for historical data
                if not month or not month.strip():
                    # Get current weather
                    url = "https://api.weatherapi.com/v1/current.json"
                    params = {
                        "key": "fda01f7a7601446881b104214252807",
                        "q": city
                    }
                else:
                    # Get historical weather data
                    url = "https://api.weatherapi.com/v1/current.json"
                   
                    params = {
                        "key": "fda01f7a7601446881b104214252807",
                        "q": city
                    }
                
                print(f"Weather API request: {url} with params: {params}")
                response = requests.get(url, params=params, timeout=10)
                
                # Check if request was successful
                if response.status_code != 200:
                    self.log.error(f"Weather API error: {response.status_code} - {response.text}")
                    return f"Weather API error for {city}: {response.status_code} - {response.text}"
                
                weather_data = response.json()
                
                # Check if API returned an error
                if "error" in weather_data:
                    error_msg = weather_data["error"].get("message", "Unknown error")
                    self.log.error(f"Weather API returned error: {error_msg}")
                    return f"Weather data error for {city}: {error_msg}"
                
                # Format the weather data nicely
                if "current" in weather_data:
                    current = weather_data["current"]
                    location = weather_data.get("location", {})
                    weather_summary = f"""
Weather for {location.get('name', city)}, {location.get('country', '')}:
- Temperature: {current.get('temp_c', 'N/A')}°C ({current.get('temp_f', 'N/A')}°F)
- Condition: {current.get('condition', {}).get('text', 'N/A')}
- Humidity: {current.get('humidity', 'N/A')}%
- Wind: {current.get('wind_kph', 'N/A')} km/h
- Feels like: {current.get('feelslike_c', 'N/A')}°C
"""
                    return weather_summary.strip()
                elif "forecast" in weather_data:
                    # Handle historical data format
                    forecast = weather_data["forecast"]["forecastday"][0]["day"]
                    location = weather_data.get("location", {})
                    weather_summary = f"""
Historical Weather for {location.get('name', city)} in {month}:
- Max Temperature: {forecast.get('maxtemp_c', 'N/A')}°C ({forecast.get('maxtemp_f', 'N/A')}°F)
- Min Temperature: {forecast.get('mintemp_c', 'N/A')}°C ({forecast.get('mintemp_f', 'N/A')}°F)
- Average Temperature: {forecast.get('avgtemp_c', 'N/A')}°C
- Condition: {forecast.get('condition', {}).get('text', 'N/A')}
- Humidity: {forecast.get('avghumidity', 'N/A')}%
"""
                    return weather_summary.strip()
                else:
                    # Fallback: return raw JSON if format is unexpected
                    weather_str = json.dumps(weather_data, indent=2)
                    return weather_str
                    
            except requests.exceptions.Timeout:
                self.log.error(f"Weather API timeout for {city}")
                return f"Weather API timeout for {city}. Please try again later."
            except requests.exceptions.RequestException as e:
                self.log.error(f"Weather API request error for {city}: {str(e)}")
                return f"Weather API request error for {city}: {str(e)}"
            except Exception as e:
                self.log.error(f"Unexpected error getting weather for {city}: {str(e)}")
                return f"Error getting weather for {city}: {str(e)}"
        
        @tool
        def currency_exchange(amount: float, from_currency: str, to_currency: str) -> str:
            """Convert amount from one currency to another."""
            try:
                # Placeholder conversion - you can integrate with real exchange rate API
                exchange_rates = {
                    ("EUR", "USD"): 1.1,
                    ("USD", "EUR"): 0.91,
                    ("GBP", "USD"): 1.25,
                    ("USD", "GBP"): 0.8,
                    ("JPY", "USD"): 0.0067,
                    ("USD", "JPY"): 149.0
                }
                
                rate = exchange_rates.get((from_currency, to_currency), 1.0)
                converted = round(amount * rate, 2)
                return f"{amount} {from_currency} = {converted} {to_currency} (approximate rate: {rate})"
            except Exception as e:
                return f"Error converting currency: {str(e)}"
        
        # Store tools as instance variables
        self.search_attractions = search_attractions
        self.search_restaurants = search_restaurants
        self.get_weather = get_weather
        self.currency_exchange = currency_exchange
        
        # Create tools list
        self.tools = [
            self.search_attractions, 
            self.search_restaurants, 
            self.get_weather, 
            self.currency_exchange
        ]
    
    @staticmethod
    def month_name_to_number(month_name: str) -> int:
        try:
            return list(calendar.month_name).index(month_name.capitalize())
        except ValueError:
            raise ValueError(f"Invalid month name: {month_name}")
    
    def run_places_as_list(self, query: str) -> List[str]:
        """Utility method to get places as a list using GooglePlacesTool."""
        try:
            # Initialize GooglePlacesTool with proper error handling
            places = GooglePlacesTool()
            self.log.info(f"Searching places with query: {query}")
            
            result = places.run(query)
            self.log.info(f"Google Places API raw result type: {type(result)}")
            
            # Handle different result types
            if isinstance(result, list):
                # Filter out empty or invalid entries
                valid_results = [str(item).strip() for item in result if item and str(item).strip()]
                self.log.info(f"Found {len(valid_results)} valid places")
                return valid_results if valid_results else ["No places found for this query."]
                
            elif isinstance(result, str):
                if result.strip():
                    # Split by newlines and filter out empty lines
                    lines = [line.strip() for line in result.strip().split("\n") if line.strip()]
                    self.log.info(f"Parsed {len(lines)} places from string result")
                    return lines if lines else ["No places found for this query."]
                else:
                    return ["No places found for this query."]
            else:
                # Handle other types (dict, etc.)
                result_str = str(result).strip()
                if result_str and result_str.lower() not in ['none', 'null', '']:
                    return [result_str]
                else:
                    return ["No places found for this query."]
                    
        except ImportError as e:
            self.log.error(f"GooglePlacesTool import error: {str(e)}")
            return [f"Google Places API not available. Please check if langchain_community is installed and GPLACES_API_KEY is set."]
        except Exception as e:
            self.log.error(f"Error fetching places for query '{query}': {str(e)}")
            return [f"Error fetching places: {str(e)}. Please check your internet connection and API key."]
    
    def extract_params(self, state: AgentState) -> dict:
        """
        Extract structured parameters from user query.
        """
        try:
            query = state["messages"][0].content
            parser = self.fixing_parser
            format_instructions = parser.get_format_instructions()
  
            prompt = self.prompt
            chain = prompt | self.llm | parser
            result = chain.invoke({"query": query, "format_instructions": format_instructions})
            
            self.log.info(f"Extracted parameters: {result}")
            return {"params": result}

        except Exception as e:
            self.log.error(f"Parameter extraction failed: {str(e)}")
            raise TripPlannerPortalException("Parameter extraction failed") from e
        
    def react_agent(self, state: AgentState) -> dict:
        """
        ReAct agent: Decides to call tools or output final summary.
        """
        try:
            prompt = self.prompt_tripmaker
            llm_with_tools = self.llm.bind_tools(self.tools)
            
            # Chain: Pass query, params, and messages
            chain = (
                {
                    "query": lambda x: x["messages"][0].content,
                    "params": lambda x: x["params"].model_dump_json(indent=2) if x.get("params") else "{}",
                    "messages": lambda x: x["messages"]
                }
                | prompt
                | llm_with_tools
            )
            
            response = chain.invoke(state)
            self.log.info(f"Agent response: {response}")
            
            return {"messages": [response]}
            
        except Exception as e:
            self.log.error(f"ReAct agent failed: {str(e)}")
            raise TripPlannerPortalException("ReAct agent execution failed") from e
    
    def should_continue(self, state: AgentState) -> str:
        """
        Check if we should continue (call tools) or end.
        """
        try:
            last_message = state["messages"][-1]
            
            # If there are tool calls, route to action (tools)
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                self.log.info("Routing to tools for execution")
                return "action"
            
            # Otherwise, end (final answer)
            self.log.info("Ending workflow - final answer ready")
            return END
            
        except Exception as e:
            self.log.error(f"Error in should_continue: {str(e)}")
            return END
    
    def _build_workflow(self):
        """Build the LangGraph workflow."""
        try:
            # Create the workflow graph
            workflow = StateGraph(AgentState)

            # Add nodes
            workflow.add_node("extract_params", self.extract_params)
            workflow.add_node("agent", self.react_agent)
            workflow.add_node("action", ToolNode(self.tools))

            # Add edges
            workflow.add_edge(START, "extract_params")
            workflow.add_edge("extract_params", "agent")
            workflow.add_conditional_edges(
                "agent",
                self.should_continue,
                {
                    "action": "action",
                    END: END,
                }
            )
            workflow.add_edge("action", "agent")  # Loop back to agent after tools

            # Compile the graph
            self.react_graph = workflow.compile()
            self.log.info("Workflow built successfully")
            
        except Exception as e:
            self.log.error(f"Error building workflow: {str(e)}")
            raise TripPlannerPortalException("Workflow building failed") from e
    
    def plan_trip(self, user_query: str) -> dict:
        """
        Main method to plan a trip based on user query.
        
        Args:
            user_query (str): The user's trip planning request
            
        Returns:
            dict: The final trip plan
        """
        try:
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=user_query)],
                "params": None
            }
            
            self.log.info(f"Starting trip planning for query: {user_query}")
            
            # Run the workflow
            final_state = self.react_graph.invoke(initial_state)
            
            self.log.info("Trip planning completed successfully")
            return final_state
            
        except Exception as e:
            self.log.error(f"Trip planning failed: {str(e)}")
            raise TripPlannerPortalException("Trip planning execution failed") from e
    
    def get_workflow_graph(self):
        """Return the compiled workflow graph for external use."""
        return self.react_graph
