# Changelog

All notable changes to the HelpingAI Python SDK will be documented in this file.

## [1.2.2] - 2025-05-08

### Added
- **🔄 Multi-Format API Support**: Enhanced models API to support both HelpingAI format (array of strings) and OpenAI v1/models compatible format
- **🔧 Auto-Detection**: Automatic detection of response format in `list()` method for seamless compatibility
- **🔗 OpenAI Compatibility**: New `from_openai_data()` method for explicit OpenAI v1/models format handling
- **📊 Custom Logging System**: New `HelpingAI/logging.py` with structured logging, colored output, and environment configuration (may get replaced with LITPRINTER)
- **🎨 Enhanced Error Diagnostics**: Advanced error parsing with helpful suggestions and context-aware recommendations 

### Changed
- **🧹 Major Refactor**: Split `HelpingAI/client.py` into modular submodules: `base.py`, `completions.py`, `chat.py`, and `main.py` under `HelpingAI/client/` for improved maintainability and clarity
- **🔄 Backward Compatibility**: The original `client.py` now re-exports all main client classes for seamless transition
- **🧩 Internal Structure**: All client logic and classes are now organized in dedicated files, reducing file size and improving code navigation
- **🔐 Enhanced Security**: Models endpoint now requires authentication (`auth_required=True`)
- **🧹 Code Cleanup**: Removed all hardcoded model names for fully dynamic API-driven model management
- **📡 Dynamic Model Loading**: Models are now fetched entirely from API responses instead of fallback hardcoded lists

### Enhanced
- **🧠 Simplified Think Logic**: Simplified complex `hide_think` parameter logic as it is now internally handled by HelpingAI's backend
- **🎯 Flexible Data Handling**: `Model.from_api_data()` now accepts both string (HelpingAI format) and dict (OpenAI format) inputs
- **🔍 Better Error Reporting**: Error messages now show actual available models from API responses
- **🧩 Format Agnostic**: Seamless handling of different API response structures without breaking changes
- **🛠️ Advanced Error Handling**: Modular error parsing with helper methods for message extraction, model name detection, and streaming suggestions
- **📋 Smart Error Messages**: Context-aware error enhancement with actionable suggestions based on status codes and request patterns
- **🌈 Colored Log Output**: Custom logging system with color-coded levels, timestamps, and configurable output destinations
- **⚙️ Environment Configuration**: Logging configuration via environment variables (`HAI_LOG_LEVEL`, `HAI_LOG_FILE`, `HAI_LOG_CONSOLE`)

## [1.2.0] - 2025-07-20

### Added
- **🔌 MCP Integration**: Full [Model context Protocol (MCP)](docs/mcp_integration.md) support for external tool connections
- **🖥️ Multiple Transport Types**: Support for stdio, SSE, and streamable-http MCP servers
- **🔄 Automatic Tool Discovery**: MCP tools automatically converted to OpenAI-compatible format
- **📁 Resource Support**: Built-in `list_resources` and `read_resource` tools for MCP resources
- **🔀 Mixed Tools Support**: Seamlessly combine MCP servers with regular OpenAI-format tools
- **⚡ Process Management**: Automatic cleanup of MCP server processes on exit
- **🔁 Reconnection Logic**: Handles server disconnections automatically
- **🛡️ Graceful Error Handling**: Works without MCP package installed with helpful error messages
- **📦 Optional MCP Dependency**: Install with `pip install HelpingAI[mcp]` for MCP features
- New MCP integration documentation and examples

### Enhanced
- **🛠️ Extended Tools Compatibility**: Enhanced tools framework to support MCP server configurations
- **🌐 Popular MCP Servers**: Ready support for mcp-server-time, mcp-server-fetch, mcp-server-filesystem, and more
- **🏗️ Backward Compatibility**: Fully backward compatible with no breaking changes to existing functionality

## [1.1.3] - 2025-07-18

### Added
- **🔧 Tool Calling Framework**: New [`@tools decorator`](HelpingAI/tools/core.py:144) for effortless tool creation
- **🔄 Direct Tool Execution**: New `.call()` method on HAI client for executing tools without registry manipulation
- **🤖 Automatic Schema Generation**: Type hint-based JSON schema creation with docstring parsing
- **📝 Smart Documentation**: Multi-format docstring parsing (Google, Sphinx, NumPy styles)
- **🧠 Thread-Safe Tool Registry**: Reliable tool management in multi-threaded environments
- **🔍 Tool Validation**: Automatic parameter validation against JSON schema
- **Extended Python Support**: Now supports Python 3.7-3.14
- **Streaming Support**: Real-time response streaming
- **Advanced Filtering**: Hide reasoning blocks with `hide_think` parameter
- New comprehensive [Tool Calling Guide](docs/tool_calling.md)

### Changed
- **🔄 Universal Compatibility**: Seamless integration with existing OpenAI-format tools
- **Updated Models**: Support for latest models (Dhanishtha-2.0-preview, Dhanishtha-2.0-preview-mini)
- **Improved Model Management**: Better fallback handling and detailed model descriptions
- **Simplified Tool Execution**: Direct tool calling with `client.call(tool_name, arguments)` syntax
- Deprecated `get_tools_format()` in favor of `get_tools()`
- Updated documentation to reflect current model names and best practices

### Enhanced
- **🛡️ Enhanced Tool Error Handling**: Comprehensive exception types for tool operations
- **Dhanishtha-2.0 Integration**: World's first intermediate thinking model with multi-phase reasoning
- **Dhanishtha Models**: Advanced reasoning capabilities with transparent thinking processes
- **OpenAI-Compatible Interface**: Familiar API design
- **Enhanced Error Handling**: Comprehensive exception types

## [1.1.2] - 2025-06-15

### Added
- Support for Dhanishtha-2.0-preview model
- Improved error handling for API requests
- Enhanced streaming capabilities

### Fixed
- Various bug fixes and performance improvements

## [1.1.1] - 2025-05-20

### Added
- Initial support for tool calling
- Enhanced type hints for better IDE support

### Fixed
- Connection handling for unstable networks
- Token counting accuracy

## [1.1.0] - 2025-04-10

### Added
- Initial public release
- Support for chat completions
- Basic streaming functionality
- Error handling framework

---

For more details, see the [documentation](docs/) or [GitHub repository](https://github.com/HelpingAI/HelpingAI-python).