# aiden_companion/src/tools/aiden_tools.py

import time
import threading
from typing import Dict, Any, List, Optional
from agents.tool import function_tool
from pydantic import ValidationError
from fellow_aiden.profile import CoffeeProfile
from fellow_aiden.schedule import CoffeeSchedule
from aiden_companion.core.aiden_client import get_aiden_client

# Profile cache configuration
_profile_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 300  # 5 minutes TTL (300 seconds)
}

def _is_cache_valid() -> bool:
    """Check if the current cache is still valid based on TTL."""
    return (
        _profile_cache["data"] is not None and 
        time.time() - _profile_cache["timestamp"] < _profile_cache["ttl"]
    )

def _update_profile_cache(data: List[Dict[str, Any]]) -> None:
    """Update the profile cache with new data."""
    _profile_cache["data"] = data
    _profile_cache["timestamp"] = time.time()

def _clear_profile_cache() -> None:
    """Clear the profile cache."""
    _profile_cache["data"] = None
    _profile_cache["timestamp"] = 0

def _refresh_cache_background() -> None:
    """Refresh the profile cache in a background thread."""
    def refresh():
        try:
            fresh_profiles = get_aiden_client().get_profiles()
            _update_profile_cache(fresh_profiles)
        except Exception:
            # If refresh fails, clear cache so next request fetches fresh data
            _clear_profile_cache()
    
    # Start background thread to refresh cache
    thread = threading.Thread(target=refresh, daemon=True)
    thread.start()

@function_tool
def get_brew_profile_by_name(profile_name: str) -> Optional[Dict[str, Any]]:
    """Fetches a specific brew profile by name from the Fellow Aiden brewer."""
    try:
        profile = get_aiden_client().get_profile_by_title(profile_name)
        return profile
    except Exception as e:
        return f"Error fetching profile {profile_name}: {e}"

@function_tool(strict_mode=False)
def list_aiden_profiles() -> List[Dict[str, Any]]:
    """Lists all available coffee profiles from the Fellow Aiden brewer.
    
    Uses caching to reduce API calls - profiles are cached for 5 minutes.
    Cache can be manually cleared using flush_profile_cache().
    """
    try:
        # Return cached data if valid
        if _is_cache_valid():
            return _profile_cache["data"]
        
        # Fetch fresh data from API
        profiles = get_aiden_client().get_profiles()
        
        # Update cache with fresh data
        _update_profile_cache(profiles)
        
        return profiles
    except Exception as e:
        return f"Error listing profiles: {e}"

@function_tool(strict_mode=False)
def flush_profile_cache() -> str:
    """Clears the profile cache, forcing the next profile request to fetch fresh data from the API.
    
    Use this when you know profiles have been modified outside of this application
    or when you want to ensure you're getting the most up-to-date profile data.
    """
    _clear_profile_cache()
    return "Profile cache has been cleared. Next profile request will fetch fresh data from the API."

@function_tool(strict_mode=False)
def create_aiden_profile(coffee_profile: CoffeeProfile) -> str:
    """Creates a new coffee profile on the Fellow Aiden brewer.
    
    Returns success immediately and refreshes the profile cache in the background.
    """
    try:
        profile_data = coffee_profile.model_dump()
        new_profile = get_aiden_client().create_profile(profile_data)
        
        # Refresh cache in background thread (non-blocking)
        _refresh_cache_background()
        
        return f"Successfully created profile: '{new_profile.get('title')}' with ID {new_profile.get('id')}"
    except ValidationError as e:
        return f"Invalid profile data. Error: {e}"
    except Exception as e:
        return f"Error creating profile: {e}"

@function_tool(strict_mode=False)
def delete_aiden_profile(profile_id: str) -> str:
    """Deletes a coffee profile by its ID.
    
    Returns success immediately and refreshes the profile cache in the background.
    """
    try:
        get_aiden_client().delete_profile_by_id(profile_id)
        
        # Refresh cache in background thread (non-blocking)
        _refresh_cache_background()
        
        return f"Successfully deleted profile with ID: {profile_id}"
    except Exception as e:
        return f"Error deleting profile {profile_id}: {e}"

@function_tool(strict_mode=False)
def create_aiden_schedule(schedule_data: Dict[str, Any]) -> str:
    """Creates a new brew schedule on the Fellow Aiden brewer."""
    try:
        CoffeeSchedule.model_validate(schedule_data)
        new_schedule = get_aiden_client().create_schedule(schedule_data)
        return f"Successfully created schedule with ID {new_schedule.get('id')}"
    except ValidationError as e:
        return f"Invalid schedule data. Error: {e}"
    except Exception as e:
        return f"Error creating schedule: {e}"