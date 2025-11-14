# Frequently Asked Questions (FAQ)

This FAQ provides answers to common questions about the HelpingAI Python SDK.

## General

**What is the HelpingAI Python SDK?**

The HelpingAI Python SDK is a comprehensive client library that provides a convenient and idiomatic Python interface for interacting with the HelpingAI API. It simplifies the process of integrating advanced AI capabilities into your Python applications, offering a developer-friendly experience similar to other popular AI SDKs.

**What can I do with the HelpingAI API?**

The HelpingAI API empowers you to build intelligent applications with a wide range of functionalities, including but not limited to:

-   **Chat Completions**: Generate human-like text, engage in conversational AI, and create interactive chatbots.
-   **Tool Calling**: Extend the AI's capabilities by giving it access to external functions, services, and real-time data (e.g., fetching weather, executing code, searching the web).
-   **Model Information**: Programmatically list and retrieve details about the available AI models.

For a detailed overview of all available functionalities and their usage, please refer to the [API Reference](api_reference.md).

## Authentication

**How do I get an API key?**

Your API key is essential for authenticating your requests to the HelpingAI API. You can securely generate and manage your API keys from your [HelpingAI Dashboard](https://helpingai.co/dashboard).

**How do I set my API key?**

There are two primary ways to provide your API key to the SDK:

1.  **Using an Environment Variable (Recommended)**:
    For security and convenience, we strongly recommend setting your API key as an environment variable named `HAI_API_KEY`. This prevents your sensitive key from being hardcoded directly into your codebase and makes it easier to manage across different environments.

    ```bash
    export HAI_API_KEY='your-api-key-here'
    ```

    When the `HAI_API_KEY` environment variable is set, the `HAI` client will automatically detect and use it upon initialization:

    ```python
    from HelpingAI import HAI

    client = HAI() # API key is automatically loaded from environment variable
    ```

2.  **Passing Directly to the Client**: 
    You can also pass your API key directly as an argument when initializing the `HAI` client. This method is suitable for quick tests or when environment variables are not feasible.

    ```python
    from HelpingAI import HAI

    client = HAI(api_key="your-api-key-here")
    ```

    **Note**: If both an environment variable and a direct argument are provided, the direct argument will take precedence.

## Chat Completions

**How do I create a chat completion?**

You can create a chat completion using the `client.chat.completions.create()` method. This method allows you to send a list of messages (representing a conversation) to the model and receive a text-based response. For more details and examples, refer to the [Chat Completions section in the API Reference](api_reference.md#chat-completions) and the [Basic Chat Completion example](examples.md#basic-chat-completion).

**How do I stream a chat completion?**

To receive the model's response incrementally, set the `stream` parameter to `True` in the `client.chat.completions.create()` method. This is ideal for real-time applications as it provides a more responsive user experience. See the [Streaming Completions example](examples.md#streaming-completions) for a practical demonstration.

## Tool Calling

**How do I define a tool?**

The HelpingAI SDK provides several flexible ways to define tools:
-   **`@tools` decorator**: The simplest and most recommended method for defining tools from Python functions.
-   **`Fn` class**: For programmatic tool creation, offering more control.
-   **Standard tool definition schema**: For compatibility with existing standard tool definitions.

You can find detailed explanations and examples for each method in the [Defining Tools section of the Tool Calling Guide](tool_calling.md#defining-tools).

**How do I use a tool with the model?**

To enable the model to use your defined tools, pass a list of your tool definitions to the `tools` parameter of the `client.chat.completions.create()` method. You can also control the model's tool-calling behavior using the `tool_choice` parameter. Refer to the [Using Tools section in the Tool Calling Guide](tool_calling.md#using-tools) for comprehensive examples.

**How do I handle a tool call from the model?**

When the model decides to use a tool, it will return a `tool_calls` object within its response message. Your application is then responsible for executing these tool calls and providing the results back to the model. The SDK provides helper methods like `client.call()` to facilitate this process. A detailed workflow and examples are available in the [Handling Tool Calls section of the Tool Calling Guide](tool_calling.md#handling-tool-calls).

**How do I call a tool directly?**

You can directly invoke any registered tool using the `client.call()` method. This is useful for programmatically executing tools outside of the model's conversational flow. See the [client.call() documentation in the API Reference](api_reference.md#clientcall) for more information.

## MCP Integration

**What is MCP?**

MCP (Model Context Protocol) is a standardized communication protocol that allows the HelpingAI SDK to communicate with external tool servers. This enables you to extend the functionality of the AI models by giving them access to a wide range of external tools and data sources. For a deeper understanding, refer to the [What is MCP? section in the MCP Integration Guide](mcp_integration.md#what-is-mcp).

**How do I use MCP tools?**

MCP tools are configured within the `tools` parameter of your `client.chat.completions.create()` call, similar to other tool definitions. The SDK handles the communication with the MCP server automatically. Detailed configuration and usage examples can be found in the [Configuring MCP Servers](mcp_integration.md#configuring-mcp-servers) and [Using MCP Tools](mcp_integration.md#using-mcp-tools) sections of the MCP Integration Guide.

## Error Handling

**How do I handle API errors?**

The HelpingAI SDK provides a robust error handling mechanism. All custom exceptions raised by the SDK are subclasses of `HAIError`. You should wrap your API calls in `try...except` blocks to gracefully handle potential errors. The [Error Handling section in the API Reference](api_reference.md#error-handling) provides a comprehensive list of all exception types and their meanings. You can also find an [Error Handling example](examples.md#error-handling) in the examples documentation.

## Troubleshooting

**I'm having trouble with the SDK. What should I do?**

If you encounter issues while using the SDK, consider the following troubleshooting steps:

-   **Update the SDK**: Ensure you have the latest version of the HelpingAI SDK installed by running:
    ```bash
    pip install --upgrade HelpingAI
    ```
-   **Check Documentation**: Review the [API Reference](api_reference.md), [Tool Calling Guide](tool_calling.md), [MCP Integration Guide](mcp_integration.md), and [Examples](examples.md) for detailed information and common use cases.
-   **Verify API Key**: Double-check that your API key is correctly set and has the necessary permissions.
-   **Review Error Messages**: Pay close attention to the error messages and types. They often provide specific clues about the problem.
-   **Community Support**: If you're still facing issues, consider opening an issue on our [GitHub repository](https://github.com/HelpingAI/HelpingAI-python/issues). Provide as much detail as possible, including your code, the full error traceback, and your environment details.