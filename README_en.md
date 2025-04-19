# Gantt Chart MCP Server

A Model Context Protocol (MCP) server specifically designed for Gantt chart management, allowing AI assistants to create, manage, and visualize Gantt chart projects and tasks through standardized interfaces.

## Features

* Project Management
  * Create new Gantt chart projects
  * List all existing projects
  * Delete unwanted projects
* Task Management
  * Add new tasks to projects
  * Update task information (name, description, dates, owner, progress)
  * Delete tasks
  * Get task details
* Visualization
  * Generate interactive HTML Gantt charts
  * Automatically open Gantt charts in browser

## Usage Guide

1. Ensure Python 3.10 or higher is installed on your system.
2. Make sure the `uv` tool is installed. If not installed yet, refer to the [uv official installation guide](https://github.com/astral-sh/uv).
3. Clone this repository:
4. Create a virtual environment and install dependencies:

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # Unix/macOS
# or .venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -e .
```

5. Run the server:

```bash
# Run the server directly
uv run run_server.py
```

6. Ensure the data directories exist (first time running):

```bash
mkdir -p data charts
```

## Integration with MCP Client

Add the following configuration:

```json
{
  "mcpServers": {
    "gantt-server": {
      "command": "uv",
      "args": [
        "--directory",
        "<full path to gantt-mcp-server directory>",
        "run",
        "run_server.py"
      ]
    }
  }
}
``` 