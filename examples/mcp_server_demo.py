"""
Example MCP Server with Sample Tools

This demonstrates how to create an MCP server with various sample tools
using the @tools decorator from the HelpingAI tools system.
"""

import math
import datetime
from typing import List, Optional

from HelpingAI.tools import tools
from HelpingAI.mcp_server import run_server


# Mathematical tools
@tools
def add(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    return a + b


@tools
def multiply(a: float, b: float) -> float:
    """Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
    """
    return a * b


@tools
def calculate_circle_area(radius: float) -> float:
    """Calculate the area of a circle given its radius.
    
    Args:
        radius: The radius of the circle
    """
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * radius ** 2


# String manipulation tools
@tools
def reverse_string(text: str) -> str:
    """Reverse a string.
    
    Args:
        text: The string to reverse
    """
    return text[::-1]


@tools
def count_words(text: str) -> int:
    """Count the number of words in a text.
    
    Args:
        text: The text to analyze
    """
    return len(text.strip().split())


@tools
def capitalize_words(text: str) -> str:
    """Capitalize the first letter of each word.
    
    Args:
        text: The text to capitalize
    """
    return text.title()


# Utility tools
@tools
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.datetime.now().isoformat()


@tools
def format_number(number: float, decimal_places: int = 2) -> str:
    """Format a number with specified decimal places.
    
    Args:
        number: The number to format
        decimal_places: Number of decimal places to show
    """
    return f"{number:.{decimal_places}f}"


@tools
def find_max(numbers: List[float]) -> float:
    """Find the maximum value in a list of numbers.
    
    Args:
        numbers: List of numbers to search
    """
    if not numbers:
        raise ValueError("List cannot be empty")
    return max(numbers)


@tools
def calculate_tip(bill_amount: float, tip_percentage: float = 15.0) -> dict:
    """Calculate tip and total amount for a bill.
    
    Args:
        bill_amount: The original bill amount
        tip_percentage: Tip percentage (default: 15.0)
    """
    if bill_amount < 0:
        raise ValueError("Bill amount cannot be negative")
    if tip_percentage < 0:
        raise ValueError("Tip percentage cannot be negative")
    
    tip = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip
    
    return {
        "bill_amount": bill_amount,
        "tip_percentage": tip_percentage,
        "tip_amount": tip,
        "total_amount": total
    }


@tools
def greet_user(name: str, greeting: str = "Hello") -> str:
    """Generate a personalized greeting.
    
    Args:
        name: The person's name
        greeting: The greeting to use (default: "Hello")
    """
    return f"{greeting}, {name}! Welcome to the MCP server."


if __name__ == "__main__":
    print("Starting MCP Server with Example Tools...")
    print("\nRegistered tools:")
    
    from HelpingAI.tools import get_tools
    tools_list = get_tools()
    
    for tool in tools_list:
        print(f"  - {tool.name}: {tool.description}")
    
    print(f"\nTotal tools: {len(tools_list)}")
    print("\nStarting server on http://localhost:8000")
    print("Available endpoints:")
    print("  GET  /tools  - List available tools")
    print("  POST /call   - Execute a tool")
    print("  GET  /health - Health check")
    print("\nPress Ctrl+C to stop the server")
    
    # Start the server
    run_server('localhost', 8000)