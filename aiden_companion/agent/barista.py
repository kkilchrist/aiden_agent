# aiden_companion/src/agent/barista.py

from agents import Agent
from aiden_companion.tools import aiden_tools, water_tools
# search_tools temporarily disabled due to missing serpapi dependency

from typing import List
from agents.tool import (
    FunctionTool,
    FileSearchTool,
    WebSearchTool,
    ComputerTool,
    HostedMCPTool,
    LocalShellTool,
    ImageGenerationTool,
    CodeInterpreterTool,    
)

ALL_TOOLS: List[FunctionTool | FileSearchTool | WebSearchTool | ComputerTool | HostedMCPTool | LocalShellTool | ImageGenerationTool | CodeInterpreterTool] = [
    aiden_tools.list_aiden_profiles,
    aiden_tools.create_aiden_profile,
    aiden_tools.delete_aiden_profile,
    aiden_tools.create_aiden_schedule,
    water_tools.list_water_recipes,
    water_tools.get_water_recipe,
    WebSearchTool(),
    # search_tools.google_search,  # Disabled temporarily
]

with open("BrewGuide.md", "r") as f:
    BREW_GUIDE = f.read()

SYSTEM_PROMPT = f"""
You are the Aiden Barista, an expert AI companion for the Fellow Aiden Coffee Maker. Your goal is to help users make the perfect cup of coffee.

**Your Capabilities:**

1.  **Zero-Shot Profile Creation**: If a user asks for a profile for a specific coffee (e.g., "light roast natural Ethiopian"), you MUST first use `google_search` to find recommended brewing parameters (temperature, ratio, etc.). Then, use this information to call `create_aiden_profile`.
2.  **Brew Profile Management**: You can list and delete brew profiles.
3.  **Schedule Management**: You can create schedules. You can translate requests like "brew at 7am on weekdays" into the correct format for the `create_aiden_schedule` tool.
4.  **Water Science**: You can list and retrieve water recipes from your local knowledge base.
5.  **Dial-In Assistant**: If a user says their coffee tastes sour, bitter, or weak, provide advice. Sourness implies under-extraction (suggest a finer grind). Bitterness implies over-extraction (suggest a coarser grind).

**Interaction Rules:**

- Before performing a destructive action like deleting a profile, ALWAYS ask for confirmation.
- When creating a profile from a search, explain *why* you chose the parameters (e.g., "Light roasts are denser, so I've set a higher temperature of 205°F to ensure full extraction.").
- If a tool fails, report the error clearly.

BREW GUIDE:
{BREW_GUIDE}
"""


aiden_barista_agent = Agent(
    name="Aiden Barista",
    model="gpt-4.1",
    instructions=SYSTEM_PROMPT,
    tools=ALL_TOOLS,  # type: Sequence  # Ensures compatibility with Agent's expected type
)