# aiden_companion/src/app.py

import reflex as rx
from typing import List, Dict, Any
from agents import Runner


# Note: The agent is now imported from its new location
from aiden_companion.agent.barista import aiden_barista_agent

class State(rx.State):
    """The application state."""
    chats: Dict[str, List[Dict[str, Any]]] = {
        "main": [
            {
                "role": "assistant",
                "content": """**Hello!**  
I'm your personal brewing assistant, here to help you master your **Fellow Aiden** and **Ode grinder**. I'm equipped with a deep understanding of everything from **grind settings** and **water chemistry** to advanced **brewing techniques** and **troubleshooting**.

Whether you're:

- looking for a specific recipe for a new bag of beans,  
- trying to fix a cup that tastes a little off, or  
- just want to explore what's possible with your setup —  

**I'm here to help.**

How can I help you **brew a better cup of coffee** today?""",
            }
        ]
    }
    current_chat: str = "main"

    @rx.event
    async def handle_submit(self, form_data: dict):
        """Handle form submission - process the message with the agent."""
        message = form_data.get("message")
        if not message:
            return

        # Add user message to chat
        self.chats[self.current_chat].append({"role": "user", "content": message})
        
        # Convert chat history to the proper format for the agent
        chat_input = []
        for msg in self.chats[self.current_chat]:
            if msg["role"] in ["user", "assistant"]:
                chat_input.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        try:
            # Use streaming for now, but collect the full response
            result = Runner.run_streamed(
                aiden_barista_agent,
                input=chat_input,
            )

            # Add empty assistant message for the response
            self.chats[self.current_chat].append({"role": "assistant", "content": ""})
            
            # Yield to update the UI with the user message and empty assistant message
            yield

            async for event in result.stream_events():
                # Handle raw response events for text streaming
                if event.type == "raw_response_event":
                    from openai.types.responses import ResponseTextDeltaEvent
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        self.chats[self.current_chat][-1]["content"] += event.data.delta
                        # Yield to update UI with each token
                        yield
                
                # Handle run item events for completed items
                elif event.type == "run_item_stream_event":
                    if event.item.type == "tool_call_item":
                        # Get tool name, handling different tool call types
                        tool_name = getattr(event.item.raw_item, 'name', 'unknown_tool')
                        
                        self.chats[self.current_chat].append(
                            {
                                "role": "tool_outputs",
                                "content": "",
                                "tool_call_id": event.item.raw_item.id,
                                "name": tool_name,
                            }
                        )
                        # Yield to update UI with tool call
                        yield
                    elif event.item.type == "tool_call_output_item":
                        # Find the corresponding tool call and update its content
                        call_id = event.item.raw_item.get("call_id")
                        for m in reversed(self.chats[self.current_chat]):
                            if m.get("tool_call_id") == call_id:
                                m["content"] += str(event.item.output)
                                break
                        # Yield to update UI with tool output
                        yield
                    
        except Exception as e:
            # Handle any errors by showing them in the chat
            self.chats[self.current_chat].append({
                "role": "assistant", 
                "content": f"Error: {str(e)}"
            })
            # Yield to update UI with error message
            yield

def message_bubble(message: Dict[str, Any]) -> rx.Component:
    is_user = message["role"] == "user"
    is_tool = message["role"] == "tool_outputs"
    
    return rx.box(
        rx.cond(
            is_tool,
            # Tool content with enhanced styling
            rx.vstack(
                rx.hstack(
                    rx.icon("wrench", size=18, color=rx.color("orange", 6)), 
                    rx.text(
                        f"Tool: {message.get('name', 'Unknown')}", 
                        font_weight="600",
                        color=rx.color("orange", 7),
                        font_size="0.9em"
                    ),
                    spacing="2"
                ),
                rx.code_block(
                    message["content"], 
                    language="json", 
                    can_copy=True, 
                    theme="github", 
                    width="100%",
                    border_radius="0.5em",
                    font_size="0.85em"
                ),
                align_items="flex-start", 
                width="100%", 
                spacing="3"
            ),
            # Enhanced regular content with better markdown styling
            rx.markdown(
                message["content"],
                style={
                    "line-height": "1.6",
                    "color": rx.cond(is_user, "white", rx.color("gray", 12)),
                }
            )
        ),
        padding="1.25em",
        border_radius="1.25em",
        margin_y="0.75em",
        max_width=rx.cond(is_tool, "85%", "75%"),
        box_shadow=rx.cond(
            is_user,
            "rgba(59, 130, 246, 0.15) 0px 4px 12px 0px",
            "rgba(0, 0, 0, 0.08) 0px 2px 8px 0px"
        ),
        border=rx.cond(
            is_tool,
            f"1px solid {rx.color('orange', 4)}",
            "none"
        ),
        align_self=rx.cond(
            is_tool, 
            "center",
            rx.cond(is_user, "flex-end", "flex-start")
        ),
        bg=rx.cond(
            is_tool,
            rx.color("orange", 1),
            rx.cond(is_user, rx.color("blue", 6), "white")
        ),
        # Add subtle hover effect
        _hover={
            "transform": "translateY(-1px)",
            "box_shadow": rx.cond(
                is_user,
                "rgba(59, 130, 246, 0.25) 0px 6px 16px 0px",
                "rgba(0, 0, 0, 0.12) 0px 4px 12px 0px"
            ),
        },
        transition="all 0.2s ease-in-out",
    )

def index() -> rx.Component:
    return rx.box(
        # Background with subtle pattern
        rx.container(
            # Header section with gradient background
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("coffee", size=32, color="white"),
                        rx.heading(
                            "Aiden Companion", 
                            size="8", 
                            color="white",
                            font_weight="700"
                        ),
                        spacing="3",
                        align_items="center"
                    ),
                    rx.text(
                        "Your AI-powered coffee brewing assistant", 
                        color="rgba(255, 255, 255, 0.9)",
                        font_size="1.1em",
                        font_weight="400"
                    ),
                    spacing="2",
                    align_items="center",
                    text_align="center"
                ),
                background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                padding="2em",
                border_radius="1.5em 1.5em 0 0",
                width="100%"
            ),
            
            # Chat messages area with better styling
            rx.box(
                rx.foreach(State.chats[State.current_chat], message_bubble),
                width="100%", 
                overflow_y="auto", 
                padding="1.5em", 
                flex_grow="1",
                max_height="55vh",
                min_height="55vh",
                background="linear-gradient(to bottom, #f8fafc 0%, #e2e8f0 100%)",
                style={
                    "scrollbar-width": "thin",
                    "scrollbar-color": f"{rx.color('gray', 4)} transparent",
                }
            ),
            
            # Input form with modern design
            rx.box(
                rx.form(
                    rx.hstack(
                        rx.text_area(
                            placeholder="", 
                            flex_grow="1",
                            name="message",
                            id="message",
                            padding="1.25em 1.5em",
                            border_radius="1.5em",
                            border=f"2px solid {rx.color('gray', 3)}",
                            font_size="1.1em",
                            height="4.5em",
                            min_height="4.5em",
                            max_height="8em",
                            resize="vertical",
                            bg="white",
                            _focus={
                                "border_color": rx.color('blue', 5),
                                "box_shadow": f"0 0 0 3px {rx.color('blue', 2)}",
                                "outline": "none",
                            },
                            _hover={
                                "border_color": rx.color('gray', 4),
                            },
                            transition="all 0.2s ease-in-out"
                        ),
                        rx.button(
                            rx.icon("send", size=22),
                            type="submit",
                            padding="1.25em 1.75em",
                            border_radius="1.5em",
                            height="4.5em",
                            min_height="4.5em",
                            background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            color="white",
                            border="none",
                            font_weight="600",
                            _hover={
                                "background": "linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)",
                                "transform": "translateY(-1px)",
                                "box_shadow": "0 4px 12px rgba(102, 126, 234, 0.4)",
                            },
                            _active={
                                "transform": "translateY(0px)",
                            },
                            transition="all 0.2s ease-in-out",
                            cursor="pointer"
                        ),
                        spacing="3",
                        width="100%",
                        align_items="center"
                    ),
                    on_submit=State.handle_submit,
                    reset_on_submit=True,
                    width="100%"
                ),
                padding="1.5em",
                background="white",
                border_radius="0 0 1.5em 1.5em",
                border_top=f"1px solid {rx.color('gray', 3)}",
                width="100%"
            ),
            
            # Main container styling
            height="85vh", 
            width="100%", 
            max_width="1000px", 
            margin="2em auto",
            border_radius="1.5em",
            box_shadow="0 20px 40px rgba(0, 0, 0, 0.1)",
            overflow="hidden",
            display="flex",
            flex_direction="column",
            background="white"
        ),
        # Page background with subtle gradient
        background="linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
        min_height="100vh",
        padding="1em"
    )

app = rx.App()
app.add_page(index)