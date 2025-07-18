# Changelog

All notable changes to the HelpingAI Python SDK will be documented in this file.

## [1.1.3] - 2025-07-18

### Added
- **🔧 Tool Calling Framework**: New [`@tools decorator`](HelpingAI/tools/core.py:144) for effortless tool creation
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