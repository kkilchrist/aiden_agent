# aiden_companion/src/tools/water_tools.py
import json
import os
from typing import Dict, Any, List, Optional
from agents.tool import function_tool

WATER_RECIPE_FILE = os.path.join(os.path.dirname(__file__), "../core/water_recipes.json")

@function_tool(strict_mode=False)
def list_water_recipes() -> List[Dict[str, Any]]:
    """Lists all available custom water recipes from the local knowledge base."""
    try:
        with open(WATER_RECIPE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        return f"Error reading water recipes: {e}"

@function_tool(strict_mode=False)
def get_water_recipe(name: str) -> Optional[Dict[str, Any]]:
    """Retrieves a specific water recipe by its name."""
    try:
        recipes = list_water_recipes()
        for recipe in recipes:
            if recipe.get("name", "").lower() == name.lower():
                return recipe
        return f"Water recipe '{name}' not found."
    except Exception as e:
        return f"Error getting water recipe: {e}"