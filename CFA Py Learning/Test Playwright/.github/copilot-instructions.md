<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Project Instructions

This project is a Python automation tool that:
1. Reads data from Excel files using pandas
2. Uses Playwright to automate interactions with OneNote
3. Updates OneNote with the Excel data, creating new sections dynamically for different dates

The code should be modular, well-documented, and handle errors gracefully. Focus on creating reusable components for OneNote automation.

## Project Structure

The project follows this structure:
- `main.py` - Entry point and orchestration
- `excel_reader.py` - Handles Excel data reading and processing
- `onenote_updater.py` - Handles OneNote web automation
- `config.py` - Configuration settings
- `data/` - Directory for Excel files
- `utils/` - Utility modules and helpers (optional)
- `tests/` - Test modules (optional)

## Object-Oriented Design Principles

This project should adhere to these OOP principles:
1. **Abstraction**: Use abstract base classes to define interfaces
2. **Encapsulation**: Keep implementation details private
3. **Inheritance**: Use inheritance for code reuse
4. **Polymorphism**: Allow different implementations of the same interface
5. **Single Responsibility**: Each class should have a single purpose
6. **Open/Closed**: Classes should be open for extension but closed for modification
7. **Dependency Injection**: Pass dependencies as parameters
8. **Interface Segregation**: Clients should not depend on methods they don't use
9. **Composition Over Inheritance**: Prefer composition for complex behaviors

## Data Handling Requirements

The Excel data processing should:
1. Handle multiple Excel file formats (.xlsx, .xls, .csv)
2. Support various data structures and layouts
3. Perform basic data validation and cleaning
4. Extract relevant information for OneNote updates
5. Handle large datasets efficiently
6. Support custom data transformations

## OneNote Automation Requirements

The OneNote automation should:
1. Handle authentication securely
2. Create new sections based on dates or other criteria
3. Update existing sections if needed
4. Format content with proper styling (headings, tables, etc.)
5. Handle network issues and retries
6. Support different OneNote structures
7. Be resilient to UI changes in OneNote

## Error Handling and Logging

The project should include:
1. Custom exception classes for different error types
2. Comprehensive logging with different levels
3. Graceful degradation when issues occur
4. Detailed error messages and troubleshooting info
5. Retry mechanisms for transient errors

## Configuration and Extensibility

The project should:
1. Use a configuration system for settings
2. Allow easy extension for new data sources
3. Support custom OneNote update patterns
4. Be adaptable to different environments (dev, test, prod)
5. Support command-line arguments for automation

## Testing Strategy

Consider implementing:
1. Unit tests for core functionality
2. Integration tests for end-to-end flows
3. Mock objects for external dependencies
4. Parameterized tests for different scenarios
5. Test fixtures for common setup and teardown

## Documentation

All code should include:
1. Comprehensive docstrings in Google or NumPy format
2. Type annotations for better IDE support
3. Examples and usage notes
4. Architecture documentation
5. Setup and installation instructions
