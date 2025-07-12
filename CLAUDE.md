# Aiden Companion App - AI Agent Project

## Project Overview

We are building an agentic (AI-enabled) companion app for the Fellow Aiden coffee maker using the OpenAI Agents SDK. This application will serve as an intelligent interface between users and their coffee brewing devices, providing automated brewing control, personalized recommendations, and cloud-based data management.

## Architecture

- **Frontend**: AI Agent interface using OpenAI Agents SDK
- **Coffee Maker Integration**: fellow-aiden Python library for device control
- **Cloud Integration**: Cloud account management and data synchronization
- **AI Capabilities**: Intelligent brewing recommendations, scheduling, and user interaction

## Technology Stack

### Core Dependencies
- **OpenAI Agents SDK** - AI agent framework
- **fellow-aiden** - Coffee maker API library
- **python-dotenv** - Environment variable management
- **requests** - HTTP client (via fellow-aiden)
- **pydantic** - Data validation (via fellow-aiden)

### Coffee Maker API Library (fellow-aiden)

The fellow-aiden library provides complete control over Fellow Aiden coffee makers. It is fully documented in FELLOW_AIDEN_API_DOCUMENTATION.md but a summary is provided here for quick reference:

#### Key Classes
- `FellowAiden(email, password)` - Main API client
- `CoffeeProfile` - Brewing profile data model
- `CoffeeSchedule` - Scheduling data model

#### Core Functionality
- **Authentication**: Automatic token management and refresh
- **Profile Management**: Create, update, delete, and share brewing profiles
- **Schedule Management**: Automated brewing schedules
- **Device Control**: Real-time brewer settings and status
- **Data Validation**: Comprehensive parameter validation

## Development Guidelines

### Code Style & Conventions

#### Python Code Standards
- Use **snake_case** for variables, functions, and module names
- Use **PascalCase** for class names
- Maximum line length: **88 characters** (Black formatter standard)
- Use type hints for all function parameters and return values
- Follow PEP 8 guidelines

#### Import Organization
```python
# Standard library imports
import os
import json
from typing import List, Dict, Optional

# Third-party imports
from dotenv import load_dotenv
from openai import OpenAI

# Local imports
from fellow_aiden import FellowAiden
```

#### Environment Variables
- Store all sensitive data in `.env` file
- Use descriptive variable names with project prefix:
  ```bash
  FELLOW_EMAIL=your-email@example.com
  FELLOW_PASSWORD=your-password
  OPENAI_API_KEY=your-openai-key
  CLOUD_API_ENDPOINT=your-cloud-endpoint
  ```

#### Error Handling
- Use specific exception types when possible
- Log errors with appropriate context
- Provide meaningful error messages to users
- Implement retry logic for API calls

#### Coffee Profile Data Structure
When working with coffee profiles, use this validated structure:
```python
profile_template = {
    "profileType": 0,
    "title": "Profile Name",  # ≤50 characters
    "ratio": 16.0,  # 14.0-20.0 in 0.5 increments
    "bloomEnabled": True,
    "bloomRatio": 2.0,  # 1.0-3.0 in 0.5 increments
    "bloomDuration": 30,  # 1-120 seconds
    "bloomTemperature": 96.0,  # 50.0-99.0°F in 0.5 increments
    "ssPulsesEnabled": True,
    "ssPulsesNumber": 3,  # 1-10
    "ssPulsesInterval": 23,  # 5-60 seconds
    "ssPulseTemperatures": [96.0, 97.0, 98.0],  # 50.0-99.0°F each
    "batchPulsesEnabled": True,
    "batchPulsesNumber": 2,  # 1-10
    "batchPulsesInterval": 30,  # 5-60 seconds
    "batchPulseTemperatures": [96.0, 97.0]  # 50.0-99.0°F each
}
```

#### Schedule Data Structure
```python
schedule_template = {
    "days": [True, True, False, True, False, True, False],  # Sun-Sat
    "secondFromStartOfTheDay": 28800,  # Seconds from midnight (8 AM = 8*3600)
    "enabled": True,
    "amountOfWater": 950,  # 150-1500 ml
    "profileId": "p7"  # Valid profile ID format: p{number} or plocal{number}
}
```

### Project Structure

```
aidenhelper/
├── .env                    # Environment variables
├── CLAUDE.md              # This file - project documentation
├── FELLOW_AIDEN_API_DOCUMENTATION.md  # Library documentation
├── main.py                # Main application entry point
├── sample.py              # Example usage and testing
├── pyproject.toml         # Project dependencies
└── src/                   # Source code directory
    ├── agents/            # AI agent implementations
    ├── coffee/           # Coffee maker integration
    ├── cloud/            # Cloud service integration
    └── utils/            # Utility functions
```

### AI Agent Guidelines

#### Agent Personality & Behavior
- **Helpful and Knowledgeable**: Provide coffee brewing expertise
- **Proactive**: Suggest optimal brewing times and profiles
- **Learning**: Adapt to user preferences over time
- **Safety-First**: Always validate brewing parameters
- **Conversational**: Natural language interaction

#### Agent Capabilities
- **Coffee Expertise**: Recommend brewing parameters based on coffee type, grind, and user preferences
- **Schedule Management**: Intelligently schedule brews based on user routines
- **Profile Optimization**: Learn from user feedback to improve brewing profiles
- **Troubleshooting**: Help diagnose and resolve brewing issues
- **Data Analysis**: Analyze brewing history and patterns

#### Response Guidelines
- **Always validate** coffee parameters before sending to device
- **Confirm destructive actions** (deleting profiles/schedules) with user
- **Provide context** for brewing recommendations
- **Use coffee terminology** appropriately but explain when needed
- **Handle errors gracefully** and suggest alternatives

### Integration Patterns

#### Coffee Maker Integration
```python
# Initialize with environment variables
load_dotenv()
aiden = FellowAiden(
    email=os.environ['FELLOW_EMAIL'],
    password=os.environ['FELLOW_PASSWORD']
)

# Always validate data before creating profiles
try:
    profile = aiden.create_profile(profile_data)
    return f"Created profile '{profile['title']}' successfully"
except ValidationError as e:
    return f"Invalid profile data: {e}"
except Exception as e:
    return f"Failed to create profile: {e}"
```

#### AI Agent Integration
- Use OpenAI Agents SDK for natural language processing
- Implement function calling for coffee maker operations
- Maintain conversation context for personalized interactions
- Store user preferences and brewing history

### Testing & Development

#### Testing Commands
- **Lint**: Run code quality checks
- **Type Check**: Validate type annotations
- **Test**: Run unit and integration tests

#### Development Workflow
1. **Environment Setup**: Ensure `.env` file is configured
2. **Feature Development**: Implement in appropriate module
3. **Testing**: Test with actual coffee maker when possible
4. **Validation**: Verify all coffee parameters are within valid ranges
5. **Documentation**: Update relevant documentation

### Security & Safety

#### API Security
- Never log or expose credentials
- Use environment variables for all sensitive data
- Implement proper session management
- Handle authentication errors gracefully

#### Coffee Safety
- Validate all temperature settings (50.0-99.0°F)
- Ensure water amounts are within safe ranges (150-1500ml)
- Confirm schedule times are reasonable
- Prevent creation of conflicting schedules

### Common Patterns

#### Initialize Coffee Maker Connection
```python
def get_aiden_client() -> FellowAiden:
    """Get authenticated Fellow Aiden client."""
    load_dotenv()
    return FellowAiden(
        email=os.environ['FELLOW_EMAIL'],
        password=os.environ['FELLOW_PASSWORD']
    )
```

#### Error Handling Wrapper
```python
def safe_coffee_operation(operation_func):
    """Wrapper for safe coffee maker operations."""
    try:
        return operation_func()
    except ValidationError as e:
        return {"error": f"Invalid data: {e}", "success": False}
    except Exception as e:
        return {"error": f"Operation failed: {e}", "success": False}
```

#### Profile Validation
```python
def validate_profile_data(data: dict) -> bool:
    """Validate profile data before sending to device."""
    try:
        CoffeeProfile.model_validate(data)
        return True
    except ValidationError:
        return False
```

## Quick Reference

### Essential Commands
- **Create Profile**: `aiden.create_profile(profile_data)`
- **Get Profiles**: `aiden.get_profiles()`
- **Create Schedule**: `aiden.create_schedule(schedule_data)`
- **Find Profile**: `aiden.get_profile_by_title(title, fuzzy=True)`
- **Generate Share Link**: `aiden.generate_share_link(profile_id)`

### Parameter Ranges
- **Ratio**: 14.0-20.0 (0.5 increments)
- **Temperature**: 50.0-99.0°F (0.5 increments)
- **Water Amount**: 150-1500ml
- **Time Intervals**: 5-60 seconds
- **Profile Title**: ≤50 characters

### Time Conversion
```python
# Convert time to seconds from midnight
def time_to_seconds(hour: int, minute: int) -> int:
    return hour * 3600 + minute * 60

# 8:30 AM = 8*3600 + 30*60 = 30600 seconds
```