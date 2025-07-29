"""
Example script demonstrating HelpingAI tool calling functionality.

This script shows how to create and use tools with the HelpingAI SDK.
"""

import json
from rich import print

# Import HelpingAI client and tools
from HelpingAI import HAI

def generate(user_prompt, prints=True):
    """
    Generate a response using HelpingAI with tool calling support.
    
    Args:
        user_prompt (str): The user's input prompt
        prints (bool): Whether to print debug information
    
    Returns:
        str: The AI's response content
    """
    # Create a client instance
    client = HAI(api_key="*********************************")
    tools = [
        {'mcpServers': {
            'time': {'command': 'uvx', 'args': ['mcp-server-time']},
            'fetch': {'command': 'uvx', 'args': ['mcp-server-fetch']},
            # 'ddg-search': {
            #     'command': 'npx',
            #     'args': ['-y', '@oevortex/ddg_search@latest']
            # }
        }},
        'code_interpreter',
        # 'web_search'
    ]
    
    # Initialize messages
    messages = [
        {"role": "user", "content": user_prompt}
    ]
    
    # Create the chat completion with tools
    response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        stream=False,
        hide_think=True,
    )
    
    response_message = response.choices[0].message
    
    # Handle tool calls
    tool_calls = response_message.tool_calls
    if tool_calls:
        if prints:
            print(f"Tool calls detected: {len(tool_calls)}")
        
        messages.append(response_message)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if prints:
                print(f"Calling tool: {function_name}")
                print(f"Arguments: {function_args}")
            
            try:
                # Use HelpingAI's built-in tool calling mechanism
                function_response = client.call(function_name, function_args, tools=tools)
                
                if prints:
                    print(f"Tool response: {function_response}")
                
            except Exception as e:
                function_response = f"Error executing tool {function_name}: {str(e)}"
                if prints:
                    print(function_response)
            
            # Add tool response to messages
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(function_response),
            })
        
        # Get final response from HelpingAI after tool execution
        second_response = client.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=messages,
            tools=tools,
            stream=False,
            hide_think=True,
        )
        return second_response.choices[0].message.content
    
    else:
        return response.choices[0].message.content


if __name__ == "__main__":
    # Example usage:
    user_query = "https://huggingface.co/CharacterEcho/Rohit-Sharma tell me about downloads of this model"
    response = generate(user_prompt=user_query, prints=True)
    print("\nFinal Response:")
    print("-" * 50)
    print(response)