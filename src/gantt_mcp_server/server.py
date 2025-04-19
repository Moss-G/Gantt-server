#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MCP 服务器核心逻辑

import json
from typing import Dict, Any
import os
from datetime import datetime

# 确保正确导入FastMCP包
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from mcp.fastmcp import FastMCP
    except ImportError:
        raise ImportError("无法导入FastMCP。请确保正确安装'mcp'包。")

# 从gantt_logic模块导入函数
from .gantt_logic import create_gantt_chart, get_all_projects, add_task_to_project, generate_gantt_chart, get_project_tasks, get_task_details as get_task_details_logic, generate_inline_gantt_html, project_exists, get_project_data, update_task_in_project, delete_task_from_project, delete_project as delete_project_logic
# 从storage模块导入函数
from .storage import DEFAULT_DATA_FILE, load_data

# 创建FastMCP服务器实例
mcp = FastMCP("GanttChart")

@mcp.tool()
async def create_gantt_project(project_name: str, project_owner: str = "None") -> str:
    """Create a new Gantt chart project.
    
    Args:
        project_name: Name of the project
        project_owner: Name of the project owner (optional, default: "None")
    """
    try:
        # 调用gantt_logic中的函数创建项目
        result = create_gantt_chart(project_name, project_owner)
        
        # 返回格式化的字符串结果
        return (f"Project created successfully!\n"
                f"Project ID: {result['project_id']}\n"
                f"Project Name: {result['name']}\n"
                f"Project Owner: {result['owner']}")
    except ValueError as e:
        # 处理验证错误
        return f"Error: {str(e)}"
    except Exception as e:
        # 处理其他错误
        return f"An unexpected error occurred: {str(e)}"

@mcp.tool()
async def list_gantt_projects() -> str:
    """List all existing Gantt chart projects."""
    try:
        projects = get_all_projects()
        
        if not projects:
            return "No projects exist. Please create a project first."
        
        # 构建响应字符串
        response = "Existing projects:\n\n"
        for i, proj in enumerate(projects, 1):
            response += (f"{i}. ID: {proj['project_id']}\n"
                         f"   Name: {proj['name']}\n"
                         f"   Owner: {proj['owner']}\n"
                         f"   Task count: {proj['task_count']}\n\n")
        
        return response
    except Exception as e:
        return f"Error: Failed to get project list: {str(e)}"

@mcp.tool()
async def add_task(
    project_id: str,
    task_name: str,
    description: str = "",
    start_date: str = "",
    duration_days: int = 1,
    end_date: str = "",
    task_owner: str = "None"
) -> str:
    """Add a task to an existing Gantt chart project.
    
    Args:
        project_id: ID of the project to add the task to
        task_name: Name of the task
        description: Task description (optional)
        start_date: Start date in ISO format (YYYY-MM-DD) (optional)
        duration_days: Task duration in days (default: 1)
        end_date: End date in ISO format (YYYY-MM-DD) (optional)
        task_owner: Name of the person responsible for the task (optional, default: "None")
    """
    try:
        # Default empty string to None for optional date parameters
        start_date_param = None if start_date == "" else start_date
        end_date_param = None if end_date == "" else end_date
        
        # Call function in gantt_logic to add task
        result = add_task_to_project(
            project_id=project_id,
            task_name=task_name,
            description=description,
            start_date=start_date_param,
            duration_days=duration_days,
            end_date=end_date_param,
            task_owner=task_owner
        )
        
        # Return formatted string result
        return (f"Task added successfully!\n"
                f"Project ID: {result['project_id']}\n"
                f"Task ID: {result['task_id']}\n"
                f"Task Name: {result['name']}\n"
                f"Task Owner: {result['owner']}\n"
                f"Start Date: {result['start_date']}\n"
                f"End Date: {result['end_date']}\n"
                f"Duration: {result['duration_days']} days")
    except ValueError as e:
        # Specific error handling for validation errors
        return f"Error: {str(e)}"
    except TypeError as e:
        # Handle type errors (such as invalid parameter types)
        return f"Error: Invalid parameter - {str(e)}"
    except Exception as e:
        # Generic error handling
        return f"An unexpected error occurred: {str(e)}"

@mcp.tool()
async def list_tasks(project_id: str) -> str:
    """List all tasks in a Gantt chart project.
    
    Args:
        project_id: ID of the project to list tasks from
    """
    try:
        # Call function in gantt_logic to get tasks
        tasks = get_project_tasks(project_id)
        
        if not tasks:
            return f"No tasks found in project with ID '{project_id}'."
        
        # Build response string
        response = f"Tasks in project '{project_id}':\n\n"
        for i, task in enumerate(tasks, 1):
            response += (f"{i}. ID: {task['task_id']}\n"
                         f"   Name: {task['name']}\n"
                         f"   Owner: {task['owner']}\n"
                         f"   Duration: {task['duration_days']} days\n"
                         f"   Date: {task['start_date']} to {task['end_date']}\n"
                         f"   Progress: {task['progress']}%\n\n")
        
        return response
    except ValueError as e:
        # Handle validation errors
        return f"Error: {str(e)}"
    except Exception as e:
        # Handle other errors
        return f"An unexpected error occurred: {str(e)}"

@mcp.tool()
async def get_task_details(project_id: str, task_id: str) -> str:
    """Get detailed information about a specific task.
    
    Args:
        project_id: ID of the project containing the task
        task_id: ID of the task to get details for
    """
    try:
        # Call function in gantt_logic to get task details
        task = get_task_details_logic(project_id, task_id)
        
        # Format the response string
        response = f"Details for task '{task['name']}' (ID: {task_id}):\n\n"
        
        # Basic information
        response += "Basic Information:\n"
        response += f"- Name: {task['name']}\n"
        response += f"- Description: {task['description'] or 'None'}\n"
        response += f"- Owner: {task['owner']}\n\n"
        
        # Dates and duration
        response += "Time Information:\n"
        response += f"- Start Date: {task['start_date']}\n"
        response += f"- End Date: {task['end_date']}\n"
        response += f"- Duration: {task['duration_days']} days\n\n"
        
        # Status
        response += "Status Information:\n"
        response += f"- Progress: {task['progress']}%\n"
        
        # Dependencies
        if task['dependencies']:
            response += "\nDependencies:\n"
            for dep in task['dependencies']:
                response += f"- Depends on: {dep}\n"
        
        # Project context
        response += f"\nProject Context:\n"
        response += f"- Project ID: {task['project']['project_id']}\n"
        response += f"- Project Name: {task['project']['project_name']}\n"
        response += f"- Project Owner: {task['project']['project_owner']}\n"
        
        # Creation time
        response += f"\nCreated At: {task['created_at']}\n"
        
        return response
    except ValueError as e:
        # Handle validation errors
        return f"Error: {str(e)}"
    except Exception as e:
        # Handle other errors
        return f"An unexpected error occurred: {str(e)}"

@mcp.tool()
async def view_gantt_chart(project_id: str) -> str:
    """Generate and view a Gantt chart for a project.
    
    Args:
        project_id: ID of the project to generate the Gantt chart for
    """
    try:
        # Call function in gantt_logic to generate the chart
        result = generate_gantt_chart(project_id)
        
        # Try to automatically open the file in the default web browser
        import webbrowser
        try:
            # Use the file URL to open the browser
            webbrowser.open(result['chart_url'])
            browser_opened = True
        except Exception as browser_error:
            # If browser fails to open, just log the error and continue
            print(f"Failed to open browser: {str(browser_error)}")
            browser_opened = False
        
        # Return formatted string result with the link
        if browser_opened:
            return (f"Gantt chart for '{result['project_name']}' generated and opened in browser!\n\n"
                    f"If the chart didn't open automatically, you can access it at:\n"
                    f"{result['chart_url']}\n\n"
                    f"Project ID: {result['project_id']}\n"
                    f"Tasks: {result['task_count']}")
        else:
            return (f"Gantt chart for '{result['project_name']}' generated successfully!\n\n"
                    f"Please open this link in your browser to view the chart:\n"
                    f"{result['chart_url']}\n\n"
                    f"Project ID: {result['project_id']}\n"
                    f"Tasks: {result['task_count']}\n"
                    f"Local file: {result['chart_file']}")
    except ValueError as e:
        # Handle validation errors
        return f"Error: {str(e)}"
    except Exception as e:
        # Handle other errors
        return f"An unexpected error occurred: {str(e)}"

@mcp.tool()
async def update_task(
    project_id: str,
    task_id: str,
    task_name: str = "",
    description: str = "",
    start_date: str = "",
    duration_days: str = "",
    end_date: str = "",
    task_owner: str = "",
    progress: str = ""
) -> str:
    """Update an existing task in a Gantt chart project.
    
    Args:
        project_id: ID of the project containing the task
        task_id: ID of the task to update
        task_name: New name of the task (optional)
        description: New task description (optional)
        start_date: New start date in ISO format (YYYY-MM-DD) (optional)
        duration_days: New task duration in days (optional)
        end_date: New end date in ISO format (YYYY-MM-DD) (optional, cannot be used with duration_days)
        task_owner: New person responsible for the task (optional)
        progress: New progress percentage (0-100) (optional)
    """
    try:
        # Process parameters, convert empty strings to None so they don't trigger updates
        task_name_param = None if task_name == "" else task_name
        description_param = None if description == "" else description
        start_date_param = None if start_date == "" else start_date
        end_date_param = None if end_date == "" else end_date
        task_owner_param = None if task_owner == "" else task_owner
        
        # Process numeric parameters
        duration_days_param = None
        if duration_days != "":
            try:
                duration_days_param = int(duration_days)
            except ValueError:
                return f"Error: Duration days must be a valid integer"
        
        progress_param = None
        if progress != "":
            try:
                progress_param = int(progress)
                if progress_param < 0 or progress_param > 100:
                    return f"Error: Progress must be between 0 and 100"
            except ValueError:
                return f"Error: Progress must be a valid integer"
        
        # Call the update function from gantt_logic
        result = update_task_in_project(
            project_id=project_id,
            task_id=task_id,
            task_name=task_name_param,
            description=description_param,
            start_date=start_date_param,
            duration_days=duration_days_param,
            end_date=end_date_param,
            task_owner=task_owner_param,
            progress=progress_param
        )
        
        # Return formatted string result
        return (f"Task updated successfully!\n"
                f"Project ID: {result['project_id']}\n"
                f"Task ID: {result['task_id']}\n"
                f"Task Name: {result['name']}\n"
                f"Description: {result['description']}\n"
                f"Owner: {result['owner']}\n"
                f"Start Date: {result['start_date']}\n"
                f"End Date: {result['end_date']}\n"
                f"Duration: {result['duration_days']} days\n"
                f"Progress: {result['progress']}%")
    except ValueError as e:
        # Handle validation errors
        return f"Error: {str(e)}"
    except TypeError as e:
        # Handle type errors
        return f"Error: Invalid parameter - {str(e)}"
    except Exception as e:
        # Handle other errors
        return f"An unexpected error occurred: {str(e)}"

# 暂时隐藏此工具 - 当客户端支持HTML渲染时再开放
# @mcp.tool()
async def get_inline_gantt_chart(project_id: str, max_width: int = 600) -> str:
    """Get HTML content for a Gantt chart that can be embedded in chat messages.
    
    NOTE: This tool is currently hidden and will be exposed in the future when
    client-side HTML rendering is supported.
    
    Args:
        project_id: ID of the project to generate the Gantt chart for
        max_width: Maximum width of the chart in pixels (default: 600)
    """
    try:
        # Validate project_id
        if not project_id or not isinstance(project_id, str):
            raise ValueError("Project ID must be a non-empty string")
        
        # Check if project exists using the imported function
        if not project_exists(project_id):
            raise ValueError(f"Project with ID '{project_id}' does not exist")
        
        # Get project data using the safe accessor function
        project = get_project_data(project_id)
        
        # Generate inline HTML content for the Gantt chart
        html_content = generate_inline_gantt_html(project_id, project, max_width)
        
        # Return the HTML content directly
        return html_content
    except ValueError as e:
        # Handle validation errors
        return f"Error: {str(e)}"
    except Exception as e:
        # Handle other errors
        return f"An unexpected error occurred: {str(e)}"

@mcp.tool()
async def delete_task(project_id: str, task_id: str) -> str:
    """Delete a task from a Gantt chart project.
    
    Args:
        project_id: ID of the project containing the task
        task_id: ID of the task to delete
    """
    try:
        # Call function in gantt_logic to delete the task
        result = delete_task_from_project(project_id, task_id)
        
        # Return formatted string result
        return (f"Task deleted successfully!\n"
                f"Project ID: {result['project_id']}\n"
                f"Task ID: {result['task_id']}\n"
                f"Task Name: {result['name']}")
    except ValueError as e:
        # Handle validation errors
        return f"Error: {str(e)}"
    except Exception as e:
        # Handle other errors
        return f"An unexpected error occurred: {str(e)}"

@mcp.tool()
async def delete_project(project_id: str) -> str:
    """Delete a Gantt chart project and all its tasks.
    
    Args:
        project_id: ID of the project to delete
    """
    try:
        # Call function in gantt_logic to delete the project
        result = delete_project_logic(project_id)
        
        # Return formatted string result
        return (f"Project deleted successfully!\n"
                f"Project ID: {result['project_id']}\n"
                f"Project Name: {result['name']}\n"
                f"Tasks deleted: {result['task_count']}")
    except ValueError as e:
        # Handle validation errors
        return f"Error: {str(e)}"
    except Exception as e:
        # Handle other errors
        return f"An unexpected error occurred: {str(e)}"

# 暂时隐藏此工具 - 当客户端支持HTML渲染时再开放
# @mcp.tool()
async def get_storage_info() -> str:
    """Get information about the persistent storage.
    
    NOTE: This tool is currently hidden and will be exposed in the future with
    proper access controls for administrative purposes.
    """
    try:
        # Load the data directly from storage to ensure we see the latest saved state
        storage_data = load_data()
        
        # Get the file path of storage
        file_path = DEFAULT_DATA_FILE
        
        # Check if file exists
        if not os.path.exists(file_path):
            return f"No storage file found at {file_path}. Data will be created when a project is added."
        
        # Get file information
        file_size = os.path.getsize(file_path) / 1024  # Size in KB
        last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Count projects and tasks
        project_count = len(storage_data)
        task_count = sum(len(project.get("tasks", {})) for project in storage_data.values())
        
        # Build the response
        response = "Storage Information:\n\n"
        response += f"Storage file: {file_path}\n"
        response += f"File size: {file_size:.2f} KB\n"
        response += f"Last modified: {last_modified}\n\n"
        response += f"Stored projects: {project_count}\n"
        response += f"Total tasks: {task_count}\n"
        
        if "metadata" in storage_data:
            response += f"\nMetadata:\n"
            for key, value in storage_data["metadata"].items():
                response += f"- {key}: {value}\n"
        
        return response
    except Exception as e:
        return f"An error occurred while retrieving storage information: {str(e)}"

def run_server():
    """Start the MCP server."""
    mcp.run(transport="stdio") 