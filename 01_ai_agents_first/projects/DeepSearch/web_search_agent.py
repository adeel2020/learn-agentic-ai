import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, ModelSettings, set_tracing_disabled, set_default_openai_client,  set_default_openai_api, ItemHelpers
from agents.run import RunConfig, RunContextWrapper
from agents.tool import function_tool
import asyncio
from dataclasses import dataclass
from tavily import AsyncTavilyClient
from typing import Optional
from openai.types.responses import ResponseTextDeltaEvent
from pprint import pprint
import json
# Use tavily_client.search() in your agent logic
_: bool = load_dotenv(find_dotenv())

gemini_api_key: str | None = os.environ.get("GEMINI_API_KEY")

tavily_api_key: str | None = os.environ.get("TAVILY_API_KEY")

tavily_client = AsyncTavilyClient(api_key=tavily_api_key)

set_tracing_disabled(True)

set_default_openai_api("chat_completions")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_default_openai_client(external_client)

@dataclass
class IndustrySearchContext:
    industry: str                   # e.g., "telco", "finance", "healthcare", "retail"
    technology: Optional[str] = None     # e.g., "churn analysis", "fraud detection", "core KPIs"
    intent: Optional[str] = None    # e.g., "troubleshooting", "benchmarking", "strategy"

from pydantic import BaseModel

class UserProfile(BaseModel):
    name: str
    city: str
    topic: str

def fetch_user_profile(user_id: str) -> UserProfile:
    # In reality, query DB here
    return UserProfile(
        name="Alex",
        city="Berlin",
        topic="AI use cases"
    )

@function_tool
async def deep_search(wrapper: RunContextWrapper[IndustrySearchContext]) -> str:
    """
    Performs a real-time deep search using Tavily based on industry context.
    """
    ctx = wrapper.context
    query_parts = [
        f"Share success story for the "
        f"{ctx.intent}" if ctx.intent else "",
        f"for {ctx.technology} domain" if ctx.technology else "",
        f"in {ctx.industry} industry",
        f"which were implemented successfully",
    ]

    full_query = " ".join(query_parts).strip()

    # Replace this with your actual Tavily call
    result = await tavily_client.search(query=full_query, max_results=5)

    return result


def research_instructions(agent, user_input: str) -> str:
    """
    Assess the user research needs "deep research" or "summarize research" and assist the using accordingly 
    based on the output of deep_search tool
    """
    ctx = agent.context
    # First turn — store profile in context
    if not hasattr(ctx, "user_profile"):
        ctx.user_profile = fetch_user_profile(user_id="111")

    profile = ctx.user_profile

    personalised_prefix = (
        f"You’re helping {profile.name} from {profile.city} "
        f"who likes {profile.topic}. Personalise examples accordingly."
    )

    # Combine with actual user input
    return f"{personalised_prefix}\n\nUser request: {agent.context}"


ds_agent: Agent = Agent(name="DeepSearchAgent", 
                          model="gemini-2.5-flash",
                          tools=[deep_search],
                          instructions=research_instructions,
                          )

#user_input=  "Explain the AI implementation"
context = IndustrySearchContext(industry="Telecom", technology="5G", intent="AI use cases")

async def call_agent():


    result = Runner.run_streamed(starting_agent=ds_agent, 
                                input=user_input,
                                context=context
                                )
    async for event in result.stream_events():
        if event.type== "delta":
            print(event.delta, end="", flush=True)
                # Delay for visualization
            await asyncio.sleep(0.1)  # 100ms delay between chunks
        # We'll ignore the raw responses event deltas
        elif event.type == "raw_response_event":
            continue
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            # elif event.item.type == "tool_call_output_item":
            #     print(f"-- Tool output: {json.dumps(event.item.output, indent=2)}")
            elif event.item.type == "message_output_item":
                print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
                await asyncio.sleep(0.5)
            else:
                pass  # Ignore other event types

    print("=== Run complete ===")   
    # # ✅ Extract string from agent's result (depends on the SDK version)
    # output = result.final_output

    # # ✅ Make sure it's a string (print it to check format)
    # print("\nAgent Output:\n", output)



if __name__ == "__main__":

    lines = []
    print("What do you want to research today?")

    while True:
        user_input = input() # The prompt is implicit and appears on a new line each time
        if user_input.lower() == 'quit':
            break  # Exit the loop if the user types 'quit'
        else: lines.append(user_input)
        asyncio.run(call_agent())
