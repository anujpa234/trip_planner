# Prepare prompt template
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

system_prompt = """You are a travel assistant using ReAct reasoning: Think step-by-step, decide on actions (tool calls), observe results, and continue until you have all needed info. Then, output a final summary report.

For trip planning:
- Always gather: attractions, restaurants, weather.
- If costs are mentioned in a foreign currency, convert to user's local currency (infer from query or assume USD if unspecified).
- Tools available: search_attractions, search_restaurants, get_weather, currency_exchange.
- Format thoughts as: Thought: [reasoning]
- If calling tools: Action: [tool calls]
- When done: Final Answer: [comprehensive trip report including overview, attractions, restaurants, weather, costs if applicable]

Return ONLY valid JSON matching the exact schema below.

{format_instructions}

Analyze the query: 
{query}
"""

prompt = ChatPromptTemplate.from_template(system_prompt)


system_prompt_tripmaker="""You are a travel assistant using ReAct reasoning: Think step-by-step, decide on actions (tool calls), observe results, and continue until you have all needed info. Then, output a final summary report.

For trip planning:
- Always gather: attractions, restaurants, weather.
- If costs are mentioned in a foreign currency, convert to user's local currency (infer from query or assume USD if unspecified).
- Tools available: search_attractions, search_restaurants, get_weather, currency_exchange.
- Format thoughts as: Thought: [reasoning]
- If calling tools: Action: [tool calls]
- When done: Final Answer: [comprehensive trip report including overview, attractions, restaurants, weather, costs if applicable]

User query: {query}
Parsed parameters from query: {params}"""
    

prompt_tripmaker = ChatPromptTemplate.from_messages([
        ("system", system_prompt_tripmaker),
        MessagesPlaceholder(variable_name="messages"),
    ])