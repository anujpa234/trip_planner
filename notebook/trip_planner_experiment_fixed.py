print("all okay")
import os

from dotenv import load_dotenv

from langchain_core.tools import tool

from langchain_core.messages import HumanMessage, AIMessage

from langgraph.graph import StateGraph,MessagesState,START,END

from langgraph.prebuilt import ToolNode

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field

from typing import Optional,Annotated,TypedDict

from datetime import datetime

load_dotenv()

os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
from langchain_openai import ChatOpenAI

model_openai="gpt-4o"

llm=ChatOpenAI(model=model_openai)
# define pydantic class to define the structure of the data

class TripParams(BaseModel):
    city: str = Field(description="The primary city or destination (e.g., Delhi). Infer if not explicit.")
    country: Optional[str] = Field(description="Country, default to Italy if not specified.")
    duration: Optional[str] = Field(default="1 week", description="Trip length (e.g., '1 week', '3 days'). Infer reasonable default if missing.")
    month: Optional[str] = Field(description="Month or season of travel (e.g., 'July', 'June-August'). Infer from seasons.")
    start_date: Optional[str] = Field(description="Inferred start date in YYYY-MM-DD, based on current date if vague.")

parser = PydanticOutputParser(pydantic_object=TripParams)

# FIXED VERSION - RECOMMENDED: Using separate system and human prompts
def trip_maker(state: MessagesState):
    """
    Fixed version of trip_maker function with proper ChatPromptTemplate usage
    """
    # Extract the question content properly
    question = state["messages"][-1].content if hasattr(state["messages"][-1], 'content') else str(state["messages"][-1])
    
    # Separate system and human prompts for better structure
    system_prompt = """You are an expert trip planner and trip advisor.
    Based on user queries, you analyze and extract trip planning information to help create memorable travel experiences.
    
    Always return your response as a JSON object in the following format:
    {format_instructions}"""
    
    human_prompt = "Please analyze this trip planning request: {query}"
    
    # Correct ChatPromptTemplate usage with separate messages
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ]).partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | llm | parser
    response = chain.invoke({"query": question})
    
    # Return properly formatted message
    return {"messages": [AIMessage(content=str(response))]}

# ALTERNATIVE VERSION - Single template approach (if you prefer)
def trip_maker_single_template(state: MessagesState):
    """
    Alternative implementation using single template
    """
    question = state["messages"][-1].content if hasattr(state["messages"][-1], 'content') else str(state["messages"][-1])
    
    template = """You are an expert trip planner and trip advisor.
    Based on the user query, analyze the appropriate information needed to plan a memorable trip.
    
    Return your response as a JSON object in the following format:
    {format_instructions}
    
    User Query: {query}"""
    
    # Correct syntax for single template
    prompt = ChatPromptTemplate.from_template(template).partial(
        format_instructions=parser.get_format_instructions()
    )
    
    chain = prompt | llm | parser
    response = chain.invoke({"query": question})
    
    return {"messages": [AIMessage(content=str(response))]}

# ORIGINAL VERSION WITH FIXES (for comparison)
def trip_maker_original_fixed(state: MessagesState):
    """
    Original version with syntax fixes applied
    """
    question = state["messages"][-1].content if hasattr(state["messages"][-1], 'content') else str(state["messages"][-1])
    
    template = """
    You are an expert in trip planner and trip advisor.
    Based on the user query, you have to analyze the appropriate tool required to fetch the data and plan trip for the user to make his trip memorable.  
    Return your response as a JSON object in the following format:
    {format_instructions}
    
    Query: {query}"""
    
    # Fixed ChatPromptTemplate syntax - the original had these issues:
    # 1. input_variable should be input_variables (plural)
    # 2. Missing comma after input_variables
    # 3. Wrong constructor usage
    prompt = ChatPromptTemplate.from_template(template).partial(
        format_instructions=parser.get_format_instructions()
    )
    
    chain = prompt | llm | parser
    response = chain.invoke({"query": question})
    
    return {"messages": [AIMessage(content=str(response))]}

@tool
def search_attractions(state:MessagesState):
    """Searches for attractions in the given state."""
    # Get the current state
    query=state['messages'][-1]
    
    template="""
            You are a helpful Trip Advisor bot. You have to serach for attraction by using appropriate tool whereever required.
            {query}
            {format_instructions}
    """
    return state

# Summary of Issues Found in Original Code:
"""
ISSUES IN ORIGINAL trip_maker FUNCTION:

1. ChatPromptTemplate Constructor Issues:
   - Used `input_variable` instead of `input_variables` (should be plural)
   - Missing comma after `input_variables=["query"]`
   - Used wrong constructor syntax - should use ChatPromptTemplate.from_template() or from_messages()

2. Template Structure Issues:
   - Inconsistent formatting in template string
   - Missing proper variable substitution

3. State Handling Issues:
   - Not properly extracting content from message objects
   - Return format could be improved with proper AIMessage wrapper

RECOMMENDED SOLUTION:
Use separate system and human prompts with ChatPromptTemplate.from_messages() for better:
- Role definition
- Context separation  
- Model understanding
- Maintainability
- Following modern LLM best practices
"""
