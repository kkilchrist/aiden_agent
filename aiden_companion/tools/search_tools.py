# aiden_companion/src/tools/search_tools.py
import os
from agents.tool import function_tool
from serpapi import GoogleSearch

@function_tool(strict_mode=False)
def google_search(query: str) -> str:
    """
    Performs a Google search to find information.
    Useful for finding brewing parameters for specific coffee types.
    """
    try:
        api_key = os.environ.get("SERPAPI_API_KEY")
        if not api_key:
            return "Error: SERPAPI_API_KEY not found in environment variables."

        params = {"q": query, "api_key": api_key}
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "organic_results" in results and results["organic_results"]:
            snippets = [
                f"Title: {r.get('title', '')}\nSnippet: {r.get('snippet', '')}\nLink: {r.get('link', '')}"
                for r in results["organic_results"][:3] # Return top 3 results
            ]
            return "\n\n---\n\n".join(snippets)
        return "No relevant search results found."
    except Exception as e:
        return f"Error performing search: {e}"