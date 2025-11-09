# FSC Assistant Tools

This directory contains all the tools available to the FSC assistant. These tools are organized into logical groups and can be dynamically discovered and loaded by the system.

## Tool Organization

Tools are grouped by functionality:

- **builtin**: Core system tools like shell commands, time functions
- **document**: File I/O operations (loading/saving text files)
- **repository**: Repository-related operations (project folder, image loading)  
- **tools**: General utility tools (Google search, JIRA queries)
- **web**: Web scraping and browsing tools
- **agent_tools**: Agent-specific tools for task management

## Tool Discovery

The system automatically discovers all available tools by scanning the modules in this directory. Each tool module should define a `TOOL_REGISTRY` list containing the tool classes.

## Creating New Tools

To create a new tool:

1. Create a new Python file in this directory
2. Define your tool class inheriting from `BaseTool`
3. Implement the required methods (`execute`, etc.)
4. Add your tool class to the `TOOL_REGISTRY` list at the bottom of the module
5. The system will automatically discover and make it available

## Tool Interface

All tools must implement:
- `name`: Unique identifier for the tool
- `description`: Human-readable description  
- `parameters`: Dictionary defining required/optional parameters
- `execute(**kwargs)`: Main execution method that returns a dictionary with results

Example structure:

```python
class MyTool(BaseTool):
    name = "my_tool"
    description = "Description of what this tool does"
    parameters = {
        "param1": {
            "type": "string",
            "description": "What param1 is for",
            "required": True
        }
    }

    def execute(self, **kwargs) -> dict:
        # Implementation here
        return {"success": True, "result": "something"}
```