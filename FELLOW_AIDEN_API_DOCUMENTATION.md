# Fellow-Aiden Library Documentation

The fellow-aiden library provides complete functionality for interacting with Fellow Aiden coffee brewers through their API. The library consists of 3 main files that handle authentication, profile management, scheduling, and data validation.

## Library Structure

### Files Overview

1. **`__init__.py`** - Main `FellowAiden` class with API interactions
2. **`profile.py`** - `CoffeeProfile` data model with validation
3. **`schedule.py`** - `CoffeeSchedule` data model with validation

## Main Class: `FellowAiden`

### Initialization

```python
from fellow_aiden import FellowAiden

aiden = FellowAiden(email, password)
```

Creates an instance and automatically authenticates with the Fellow API.

### Device & Authentication Methods

| Method | Description |
|--------|-------------|
| `get_device_config(remote=False)` | Get device configuration (cached or fresh from API) |
| `get_display_name()` | Get brewer display name |
| `get_brewer_id()` | Get brewer ID |
| `authenticate()` | Public method to reauthenticate |

### Profile Management

| Method | Description |
|--------|-------------|
| `get_profiles()` | Get all coffee profiles |
| `get_profile_by_title(title, fuzzy=False)` | Find profile by title (exact or fuzzy match) |
| `create_profile(data)` | Create new coffee profile |
| `update_profile(profile_id, data)` | Update existing profile |
| `delete_profile_by_id(pid)` | Delete profile by ID |
| `create_profile_from_link(link)` | Create profile from shared brew link |
| `generate_share_link(pid)` | Generate shareable link for profile |
| `parse_brewlink_url(link)` | Extract profile data from shared link |

### Schedule Management

| Method | Description |
|--------|-------------|
| `get_schedules()` | Get all schedules |
| `create_schedule(data)` | Create new brew schedule |
| `delete_schedule_by_id(sid)` | Delete schedule by ID |
| `toggle_schedule(sid, enabled)` | Enable/disable schedule |

### Device Settings

| Method | Description |
|--------|-------------|
| `adjust_setting(setting, value)` | Modify device settings |

## Data Models

### `CoffeeProfile` (profile.py)

Used for creating and validating coffee brewing profiles.

#### Required Fields

| Field | Type | Description | Valid Range |
|-------|------|-------------|-------------|
| `profileType` | int | Profile type | - |
| `title` | str | Profile name | ≤50 characters |
| `ratio` | float | Coffee ratio | 14.0-20.0 (0.5 increments) |
| `bloomEnabled` | bool | Enable bloom phase | true/false |
| `bloomRatio` | float | Bloom ratio | 1.0-3.0 (0.5 increments) |
| `bloomDuration` | int | Bloom duration | 1-120 seconds |
| `bloomTemperature` | float | Bloom temperature | 50.0-99.0°F (0.5 increments) |
| `ssPulsesEnabled` | bool | Enable single-serve pulses | true/false |
| `ssPulsesNumber` | int | Number of SS pulses | 1-10 |
| `ssPulsesInterval` | int | SS pulse interval | 5-60 seconds |
| `ssPulseTemperatures` | List[float] | SS pulse temperatures | 50.0-99.0°F each |
| `batchPulsesEnabled` | bool | Enable batch pulses | true/false |
| `batchPulsesNumber` | int | Number of batch pulses | 1-10 |
| `batchPulsesInterval` | int | Batch pulse interval | 5-60 seconds |
| `batchPulseTemperatures` | List[float] | Batch pulse temperatures | 50.0-99.0°F each |

#### Example Profile

```python
profile = {
    "profileType": 0,
    "title": "My Custom Profile",
    "ratio": 16,
    "bloomEnabled": True,
    "bloomRatio": 2,
    "bloomDuration": 30,
    "bloomTemperature": 96,
    "ssPulsesEnabled": True,
    "ssPulsesNumber": 3,
    "ssPulsesInterval": 23,
    "ssPulseTemperatures": [96, 97, 98],
    "batchPulsesEnabled": True,
    "batchPulsesNumber": 2,
    "batchPulsesInterval": 30,
    "batchPulseTemperatures": [96, 97]
}
```

### `CoffeeSchedule` (schedule.py)

Used for creating and validating brew schedules.

#### Required Fields

| Field | Type | Description | Valid Range |
|-------|------|-------------|-------------|
| `days` | List[bool] | Days of week (Sun-Sat) | Exactly 7 boolean values |
| `secondFromStartOfTheDay` | int | Time in seconds from midnight | 0-86399 |
| `enabled` | bool | Schedule enabled status | true/false |
| `amountOfWater` | int | Water amount in ml | 150-1500 |
| `profileId` | str | Valid profile ID | Format: "p{number}" or "plocal{number}" |

#### Example Schedule

```python
schedule = {
    "days": [True, True, False, True, False, True, False],  # Sun, Mon, Wed, Fri
    "secondFromStartOfTheDay": 28800,  # 8:00 AM (8 * 3600)
    "enabled": True,
    "amountOfWater": 950,
    "profileId": "p7"
}
```

## API Configuration

- **Base URL:** `https://l8qtmnc692.execute-api.us-west-2.amazonaws.com/v1`
- **User-Agent:** `Fellow/5 CFNetwork/1568.300.101 Darwin/24.2.0`
- **Authentication:** Bearer token with automatic refresh on 401 errors

## Key Features

### Automatic Authentication Management
- Automatic token refresh when API returns 401 errors
- Session persistence with proper headers
- Secure credential handling

### Data Validation
- Comprehensive validation using Pydantic models
- Clear error messages for invalid data
- Type checking and range validation

### Error Handling
- Graceful handling of API errors
- Detailed error messages with context
- Automatic retry on authentication failures

### Advanced Features
- Fuzzy profile name matching (similarity > 65%)
- Shared profile link parsing and creation
- Debug logging with colored output
- Server-side field filtering for clean data

## Usage Examples

### Basic Setup

```python
import os
from dotenv import load_dotenv
from fellow_aiden import FellowAiden

# Load environment variables
load_dotenv()

# Initialize
aiden = FellowAiden(
    email=os.environ['FELLOW_EMAIL'],
    password=os.environ['FELLOW_PASSWORD']
)

# Get brewer info
name = aiden.get_display_name()
profiles = aiden.get_profiles()
```

### Profile Management

```python
# Create a profile
profile_data = {
    "profileType": 0,
    "title": "Morning Brew",
    "ratio": 15.5,
    "bloomEnabled": True,
    "bloomRatio": 2.5,
    "bloomDuration": 45,
    "bloomTemperature": 95.0,
    # ... other required fields
}
new_profile = aiden.create_profile(profile_data)

# Find profile by name
profile = aiden.get_profile_by_title('Morning', fuzzy=True)

# Generate share link
share_link = aiden.generate_share_link(profile['id'])

# Create from shared link
aiden.create_profile_from_link('https://brew.link/p/abc123')
```

### Schedule Management

```python
# Create a schedule
schedule_data = {
    "days": [False, True, True, True, True, True, False],  # Weekdays only
    "secondFromStartOfTheDay": 21600,  # 6:00 AM
    "enabled": True,
    "amountOfWater": 400,
    "profileId": "p1"
}
new_schedule = aiden.create_schedule(schedule_data)

# Toggle schedule
aiden.toggle_schedule('s0', enabled=False)
```

## Error Handling

The library provides comprehensive error handling:

- **Authentication Errors**: Automatic retry with fresh tokens
- **Validation Errors**: Clear messages about invalid data
- **API Errors**: Detailed error responses from the server
- **Network Errors**: Standard HTTP error handling

## Dependencies

- `requests` - HTTP client for API calls
- `pydantic` - Data validation and modeling
- `python-dotenv` - Environment variable management (for your application)