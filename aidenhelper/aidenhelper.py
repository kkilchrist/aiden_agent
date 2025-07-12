# aiden_companion/aiden_companion.py

import reflex as rx
from typing import List, Dict, Any

from aiden_companion.agent import aiden_barista_agent

class State(rx.State):
    """The app state."""

    # The current chat history.
    chats: Dict[str, List[Dict[str, Any]]] = {
        "main": [
            {
                "role": "assistant",
                "content": "Hello! I'm your Aiden Barista. How can I help you brew the perfect cup of coffee today?",
            }
        ]
    }
    current_chat: str = "main"

    async def handle_submit(self, form_data: dict):
        """
        Handle the form submission.

        Args:
            form_data: The form data.
        """
        message = form_data["message"]
        if not message:
            return

        # Add the user's message to the history
        self.chats[self.current_chat].append({"role": "user", "content": message})
        
        # Yield to show the user's message in the UI
        yield

        # Get the agent's response
        response_stream = aiden_barista_agent.run(self.chats[self.current_chat])

        # The initial response is an empty assistant message
        self.chats[self.current_chat].append({"role": "assistant", "content": ""})
        yield

        # Stream the response chunks
        async for chunk in response_stream:
            if chunk.event == "text.delta":
                self.chats[self.current_chat][-1]["content"] += chunk.data
                yield
            if chunk.event == "tool.call":
                self.chats[self.current_chat].append(
                    {
                        "role": "tool_outputs",
                         # We'll fill the content in as it streams
                        "content": "",
                        "tool_call_id": chunk.data.id,
                        "name": chunk.data.name,
                    }
                )
                yield
            if chunk.event == "tool.output":
                # Find the matching tool output message and update it
                for m in reversed(self.chats[self.current_chat]):
                    if m.get("tool_call_id") == chunk.data.tool_call_id:
                        m["content"] += chunk.data.content
                        break
                yield

def message_bubble(message: Dict[str, Any]) -> rx.Component:
    """A message bubble component."""
    is_user = message["role"] == "user"
    
    # Base styles for all bubbles
    bubble_style = {
        "padding": "1em",
        "border_radius": "1em",
        "margin_y": "0.5em",
        "max_width": "70%",
        "box_shadow": "rgba(0, 0, 0, 0.05) 0px 1px 2px 0px",
    }
    
    # Styles for user vs assistant
    if is_user:
        bubble_style.update({
            "bg": rx.color("accent", 4),
            "color": rx.color("accent", 12),
            "align_self": "flex-end",
        })
    else:
         bubble_style.update({
            "bg": rx.color("gray", 4),
            "color": rx.color("gray", 12),
            "align_self": "flex-start",
        })

    if message["role"] == "tool_outputs":
        return rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("wrench", size=16),
                    rx.text(f"Tool: {message['name']}", font_weight="bold"),
                    align="center",
                ),
                rx.code_block(
                    message["content"],
                    language="json",
                    can_copy=True,
                    theme="light",
                    width="100%",
                ),
                align_items="flex-start",
                width="100%",
            ),
            **bubble_style,
            bg=rx.color("gray", 2),
        )

    return rx.box(
        rx.markdown(message["content"], component_map={"p": rx.text}),
        **bubble_style,
    )


def chat_interface() -> rx.Component:
    """The main chat interface."""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.foreach(State.chats[State.current_chat], message_bubble),
                width="100%",
                overflow_y="auto",
                padding="1em",
                flex_grow="1",
            ),
            rx.form(
                rx.hstack(
                    rx.input(
                        id="message",
                        placeholder="Ask your Aiden Barista...",
                        flex_grow="1",
                    ),
                    rx.button("Send", type="submit"),
                    width="100%",
                ),
                on_submit=State.handle_submit,
                width="100%",
                padding="1em",
            ),
            height="90vh",
            width="100%",
            max_width="900px",
            align="center",
            margin="auto",
            border=f"1px solid {rx.color('gray', 5)}",
            border_radius="1em",
        )
    )


def index() -> rx.Component:
    """The main view."""
    return rx.container(
        rx.vstack(
            rx.heading("Aiden Companion", size="8", margin_bottom="0.5em"),
            rx.text("Your AI-powered coffee brewing assistant."),
            chat_interface(),
            align="center",
            padding_top="2em",
        )
    )


# Add state and page to the app.
app = rx.App()
app.add_page(index)

