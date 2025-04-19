#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Gantt chart data structures and manipulation logic

import uuid
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Import storage module for data persistence
from .storage import save_data, load_data

# Use a global dictionary to store all Gantt chart project data
# Structure: {"project_id": {"name": "Project Name", "tasks": {...}}, ...}
gantt_data: Dict[str, Any] = {}

# Directory for storing generated Gantt charts
CHARTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'charts')
# Ensure the directory exists
os.makedirs(CHARTS_DIR, exist_ok=True)

# Load existing data from storage on module initialization
gantt_data = load_data()

def create_gantt_chart(project_name: str, project_owner: str = "None") -> Dict[str, Any]:
    """
    Create a new Gantt chart project.
    
    Args:
        project_name: Name of the project
        project_owner: Name of the project owner (default: "None")
    
    Returns:
        Dictionary containing project ID and name
        
    Raises:
        ValueError: If project_name is empty or invalid
    """
    # Validate project name
    if not project_name or not project_name.strip():
        raise ValueError("Project name cannot be empty")
    
    # Validate project_owner (optional basic validation)
    if not isinstance(project_owner, str):
        raise ValueError("Project owner must be a string")
    
    # Generate unique project ID
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    
    # Ensure project ID is unique
    while project_id in gantt_data:
        project_id = f"proj_{uuid.uuid4().hex[:8]}"
    
    # Create new project structure
    gantt_data[project_id] = {
        "name": project_name,
        "owner": project_owner,
        "tasks": {},
        "created_at": datetime.now().isoformat()
    }
    
    # Save data to persistent storage
    save_data(gantt_data)
    
    return {
        "project_id": project_id,
        "name": project_name,
        "owner": project_owner
    }

def get_all_projects() -> List[Dict[str, Any]]:
    """
    Get a list of all Gantt chart projects.
    
    Returns:
        List of projects, each containing ID and name
    """
    projects = []
    for project_id, project in gantt_data.items():
        projects.append({
            "project_id": project_id,
            "name": project["name"],
            "owner": project.get("owner", "None"),
            "task_count": len(project["tasks"])
        })
    return projects

def project_exists(project_id: str) -> bool:
    """
    Check if a project with the specified ID exists.
    
    Args:
        project_id: The project ID to check
    
    Returns:
        True if the project exists, False otherwise
    """
    return project_id in gantt_data

def get_project_tasks(project_id: str) -> List[Dict[str, Any]]:
    """
    Get a list of all tasks in a specific Gantt chart project.
    
    Args:
        project_id: ID of the project to get tasks from
        
    Returns:
        List of tasks with their details
        
    Raises:
        ValueError: If project doesn't exist
    """
    # Validate project_id
    if not project_id or not isinstance(project_id, str):
        raise ValueError("Project ID must be a non-empty string")
    
    # Check if project exists
    if not project_exists(project_id):
        raise ValueError(f"Project with ID '{project_id}' does not exist")
    
    # Get tasks from the project
    tasks = []
    for task_id, task_data in gantt_data[project_id]["tasks"].items():
        tasks.append({
            "task_id": task_id,
            "name": task_data["name"],
            "description": task_data["description"],
            "owner": task_data["owner"],
            "start_date": task_data["start_date"],
            "end_date": task_data["end_date"],
            "duration_days": task_data["duration_days"],
            "progress": task_data.get("progress", 0)
        })
    
    # Sort tasks by start date
    tasks.sort(key=lambda x: x["start_date"])
    
    return tasks

def get_project_data(project_id: str) -> Dict[str, Any]:
    """
    Get the complete data for a specific project including all its tasks.
    
    Args:
        project_id: ID of the project to get data for
        
    Returns:
        Dictionary containing complete project data
        
    Raises:
        ValueError: If project doesn't exist
    """
    # Validate project_id
    if not project_id or not isinstance(project_id, str):
        raise ValueError("Project ID must be a non-empty string")
    
    # Check if project exists
    if not project_exists(project_id):
        raise ValueError(f"Project with ID '{project_id}' does not exist")
    
    # Return a deep copy of the project data to prevent accidental modifications
    import copy
    return copy.deepcopy(gantt_data[project_id])

def get_task_details(project_id: str, task_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific task in a project.
    
    Args:
        project_id: ID of the project containing the task
        task_id: ID of the task to get details for
        
    Returns:
        Dictionary containing detailed task information
        
    Raises:
        ValueError: If project or task doesn't exist
    """
    # Validate project_id
    if not project_id or not isinstance(project_id, str):
        raise ValueError("Project ID must be a non-empty string")
    
    # Check if project exists
    if not project_exists(project_id):
        raise ValueError(f"Project with ID '{project_id}' does not exist")
    
    # Validate task_id
    if not task_id or not isinstance(task_id, str):
        raise ValueError("Task ID must be a non-empty string")
    
    # Check if task exists in the project
    if task_id not in gantt_data[project_id]["tasks"]:
        raise ValueError(f"Task with ID '{task_id}' does not exist in project '{project_id}'")
    
    # Get task data
    task_data = gantt_data[project_id]["tasks"][task_id]
    
    # Get project information
    project_info = {
        "project_id": project_id,
        "project_name": gantt_data[project_id]["name"],
        "project_owner": gantt_data[project_id]["owner"]
    }
    
    # Build and return full task details
    return {
        # Task basic info
        "task_id": task_id,
        "name": task_data["name"],
        "description": task_data["description"],
        "owner": task_data["owner"],
        
        # Task dates and duration
        "start_date": task_data["start_date"],
        "end_date": task_data["end_date"],
        "duration_days": task_data["duration_days"],
        
        # Task status
        "progress": task_data.get("progress", 0),
        
        # Task relationships
        "dependencies": task_data.get("dependencies", []),
        
        # Additional metadata
        "created_at": task_data["created_at"],
        
        # Project context
        "project": project_info
    }

def add_task_to_project(
    project_id: str,
    task_name: str,
    description: str = "",
    start_date: Optional[str] = None,
    duration_days: int = 1,
    end_date: Optional[str] = None,
    task_owner: str = "None"
) -> Dict[str, Any]:
    """
    Add a task to an existing Gantt chart project.
    
    Args:
        project_id: ID of the project to add the task to
        task_name: Name of the task
        description: Task description (optional)
        start_date: Start date in ISO format (YYYY-MM-DD) (optional)
        duration_days: Task duration in days (default: 1)
        end_date: End date in ISO format (YYYY-MM-DD) (optional)
        task_owner: Name of the person responsible for the task (optional)
    
    Returns:
        Dictionary containing task data
        
    Raises:
        ValueError: If project doesn't exist, task name is empty, or dates are invalid
    """
    # Validate project_id
    if not project_id or not isinstance(project_id, str):
        raise ValueError("Project ID must be a non-empty string")
    
    # Check if project exists
    if not project_exists(project_id):
        raise ValueError(f"Project with ID '{project_id}' does not exist")
    
    # Validate task_name
    if not task_name or not task_name.strip():
        raise ValueError("Task name cannot be empty")
    
    # Validate duration_days
    if not isinstance(duration_days, int) or duration_days <= 0:
        raise ValueError("Duration days must be a positive integer")

    # Generate unique task ID
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    # Ensure task ID is unique within the project
    while task_id in gantt_data[project_id]["tasks"]:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    # Process dates
    today = datetime.now().date()
    
    # Set start date (today if not provided)
    if start_date:
        try:
            start = datetime.fromisoformat(start_date).date()
        except ValueError:
            raise ValueError(f"Invalid start date format: '{start_date}'. Use YYYY-MM-DD format.")
    else:
        start = today
    
    # Calculate end date based on provided parameters
    if end_date:
        try:
            end = datetime.fromisoformat(end_date).date()
            # Calculate duration from start and end dates
            delta = end - start
            duration_days = delta.days + 1  # inclusive of end date
            
            if duration_days <= 0:
                raise ValueError("End date must be after start date")
        except ValueError as e:
            if str(e) == "End date must be after start date":
                raise
            raise ValueError(f"Invalid end date format: '{end_date}'. Use YYYY-MM-DD format.")
    else:
        # Calculate end date from duration
        end = start + timedelta(days=duration_days - 1)  # -1 because duration includes the start day
    
    # Create task structure
    task_data = {
        "id": task_id,
        "name": task_name,
        "description": description,
        "owner": task_owner,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "duration_days": duration_days,
        "dependencies": [],
        "progress": 0,  # 0-100 percentage of completion
        "created_at": datetime.now().isoformat()
    }
    
    # Add task to project
    gantt_data[project_id]["tasks"][task_id] = task_data
    
    # Save data to persistent storage
    save_data(gantt_data)
    
    # Return task data with additional context
    return {
        "project_id": project_id,
        "task_id": task_id,
        "name": task_name,
        "description": description,
        "owner": task_owner,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "duration_days": duration_days
    }

def update_task_in_project(
    project_id: str,
    task_id: str,
    task_name: Optional[str] = None,
    description: Optional[str] = None,
    start_date: Optional[str] = None,
    duration_days: Optional[int] = None,
    end_date: Optional[str] = None,
    task_owner: Optional[str] = None,
    progress: Optional[int] = None
) -> Dict[str, Any]:
    """
    Update an existing task in a Gantt chart project.
    
    Args:
        project_id: ID of the project containing the task
        task_id: ID of the task to update
        task_name: New name of the task (optional)
        description: New task description (optional)
        start_date: New start date in ISO format (YYYY-MM-DD) (optional)
        duration_days: New task duration in days (optional)
        end_date: New end date in ISO format (YYYY-MM-DD) (optional)
        task_owner: New person responsible for the task (optional)
        progress: New progress percentage (0-100) (optional)
    
    Returns:
        Dictionary containing updated task data
        
    Raises:
        ValueError: If project or task doesn't exist, or if parameters are invalid
    """
    # Validate project_id
    if not project_id or not isinstance(project_id, str):
        raise ValueError("Project ID must be a non-empty string")
    
    # Check if project exists
    if not project_exists(project_id):
        raise ValueError(f"Project with ID '{project_id}' does not exist")
    
    # Validate task_id
    if not task_id or not isinstance(task_id, str):
        raise ValueError("Task ID must be a non-empty string")
    
    # Check if task exists in the project
    if task_id not in gantt_data[project_id]["tasks"]:
        raise ValueError(f"Task with ID '{task_id}' does not exist in project '{project_id}'")
    
    # Get the current task data
    task_data = gantt_data[project_id]["tasks"][task_id]
    
    # Validate task_name if provided
    if task_name is not None:
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")
        task_data["name"] = task_name
    
    # Update description if provided
    if description is not None:
        task_data["description"] = description
    
    # Update task owner if provided
    if task_owner is not None:
        task_data["owner"] = task_owner
    
    # Process dates
    start = datetime.fromisoformat(task_data["start_date"]).date()
    end = datetime.fromisoformat(task_data["end_date"]).date()
    
    # Update start date if provided
    if start_date is not None:
        try:
            new_start = datetime.fromisoformat(start_date).date()
            start = new_start
        except ValueError:
            raise ValueError(f"Invalid start date format: '{start_date}'. Use YYYY-MM-DD format.")
    
    # Update end date based on provided parameters
    date_updated = False
    
    if end_date is not None and duration_days is not None:
        raise ValueError("Cannot specify both end_date and duration_days - please provide only one")
    
    if end_date is not None:
        try:
            new_end = datetime.fromisoformat(end_date).date()
            # Calculate duration from start and end dates
            delta = new_end - start
            new_duration = delta.days + 1  # inclusive of end date
            
            if new_duration <= 0:
                raise ValueError("End date must be after start date")
            
            end = new_end
            task_data["duration_days"] = new_duration
            date_updated = True
        except ValueError as e:
            if str(e) == "End date must be after start date":
                raise
            raise ValueError(f"Invalid end date format: '{end_date}'. Use YYYY-MM-DD format.")
    
    if duration_days is not None and not date_updated:
        if not isinstance(duration_days, int) or duration_days <= 0:
            raise ValueError("Duration days must be a positive integer")
        
        # Calculate end date from duration
        end = start + timedelta(days=duration_days - 1)  # -1 because duration includes the start day
        task_data["duration_days"] = duration_days
    
    # Update progress if provided
    if progress is not None:
        if not isinstance(progress, int) or progress < 0 or progress > 100:
            raise ValueError("Progress must be an integer between 0 and 100")
        task_data["progress"] = progress
    
    # Update the task data with the new dates
    task_data["start_date"] = start.isoformat()
    task_data["end_date"] = end.isoformat()
    
    # Add last updated timestamp
    task_data["updated_at"] = datetime.now().isoformat()
    
    # Save data to persistent storage
    save_data(gantt_data)
    
    # Return updated task data with additional context
    return {
        "project_id": project_id,
        "task_id": task_id,
        "name": task_data["name"],
        "description": task_data["description"],
        "owner": task_data["owner"],
        "start_date": task_data["start_date"],
        "end_date": task_data["end_date"],
        "duration_days": task_data["duration_days"],
        "progress": task_data["progress"]
    }

def delete_task_from_project(project_id: str, task_id: str) -> Dict[str, Any]:
    """
    Delete a task from a Gantt chart project.
    
    Args:
        project_id: ID of the project containing the task
        task_id: ID of the task to delete
    
    Returns:
        Dictionary containing information about the deleted task
        
    Raises:
        ValueError: If project or task doesn't exist
    """
    # Validate project_id
    if not project_id or not isinstance(project_id, str):
        raise ValueError("Project ID must be a non-empty string")
    
    # Check if project exists
    if not project_exists(project_id):
        raise ValueError(f"Project with ID '{project_id}' does not exist")
    
    # Validate task_id
    if not task_id or not isinstance(task_id, str):
        raise ValueError("Task ID must be a non-empty string")
    
    # Check if task exists in the project
    if task_id not in gantt_data[project_id]["tasks"]:
        raise ValueError(f"Task with ID '{task_id}' does not exist in project '{project_id}'")
    
    # Get task info before deletion (for return value)
    task_data = gantt_data[project_id]["tasks"][task_id].copy()
    
    # Check if any other task depends on this one
    dependents = []
    for other_task_id, other_task in gantt_data[project_id]["tasks"].items():
        if task_id in other_task.get("dependencies", []):
            dependents.append(other_task_id)
    
    # If there are dependent tasks, prevent deletion
    if dependents:
        dependent_names = [gantt_data[project_id]["tasks"][t_id]["name"] for t_id in dependents]
        raise ValueError(f"Cannot delete task '{task_data['name']}' because it is depended on by: {', '.join(dependent_names)}")
    
    # Perform the deletion
    del gantt_data[project_id]["tasks"][task_id]
    
    # Save data to persistent storage
    save_data(gantt_data)
    
    # Return information about the deleted task
    return {
        "project_id": project_id,
        "task_id": task_id,
        "name": task_data["name"]
    }

def delete_project(project_id: str) -> Dict[str, Any]:
    """
    Delete a Gantt chart project and all its tasks.
    
    Args:
        project_id: ID of the project to delete
    
    Returns:
        Dictionary containing information about the deleted project
        
    Raises:
        ValueError: If project doesn't exist
    """
    # Validate project_id
    if not project_id or not isinstance(project_id, str):
        raise ValueError("Project ID must be a non-empty string")
    
    # Check if project exists
    if not project_exists(project_id):
        raise ValueError(f"Project with ID '{project_id}' does not exist")
    
    # Get project data before deletion (for return value)
    project_data = gantt_data[project_id].copy()
    project_name = project_data["name"]
    task_count = len(project_data["tasks"])
    
    # Perform the deletion
    del gantt_data[project_id]
    
    # Save data to persistent storage
    save_data(gantt_data)
    
    # Return information about the deleted project
    return {
        "project_id": project_id,
        "name": project_name,
        "task_count": task_count
    }

def generate_gantt_html(project_id: str, project: Dict[str, Any]) -> str:
    """
    Generate HTML content for a Gantt chart.
    
    Args:
        project_id: ID of the project
        project: Project data
        
    Returns:
        HTML content for the Gantt chart
    """
    tasks = project["tasks"]
    
    # Find the earliest start date and latest end date to determine chart range
    if tasks:
        # Initialize with the first task's dates
        all_dates = [(datetime.fromisoformat(task["start_date"]).date(), 
                      datetime.fromisoformat(task["end_date"]).date())
                     for task in tasks.values()]
        
        if all_dates:
            min_date = min(date[0] for date in all_dates)
            max_date = max(date[1] for date in all_dates)
        else:
            # Default to current week if no tasks
            today = datetime.now().date()
            min_date = today
            max_date = today + timedelta(days=7)
    else:
        # Default to current week if no tasks
        today = datetime.now().date()
        min_date = today
        max_date = today + timedelta(days=7)
    
    # Add some padding to the date range
    min_date = min_date - timedelta(days=1)
    max_date = max_date + timedelta(days=1)
    
    # Calculate total days for the chart
    total_days = (max_date - min_date).days + 1
    
    # Prepare tasks for the chart
    task_list = []
    for task_id, task in tasks.items():
        start_date = datetime.fromisoformat(task["start_date"]).date()
        end_date = datetime.fromisoformat(task["end_date"]).date()
        
        # Calculate position and width as percentages
        start_pos = ((start_date - min_date).days / total_days) * 100
        width = ((end_date - start_date).days + 1) / total_days * 100
        
        task_list.append({
            "id": task_id,
            "name": task["name"],
            "start_pos": start_pos,
            "width": width,
            "start_date": task["start_date"],
            "end_date": task["end_date"],
            "progress": task.get("progress", 0),
            "owner": task.get("owner", "None")
        })
    
    # Generate the HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project["name"]} - Gantt Chart</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1, h2 {{
            color: #333;
        }}
        .project-info {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .gantt-container {{
            overflow-x: auto;
            margin-top: 20px;
            background-color: #fff;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .gantt-chart {{
            position: relative;
            width: 100%;
            overflow-x: auto;
        }}
        .timeline {{
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 10px;
            padding-bottom: 5px;
        }}
        .day {{
            flex: 1;
            text-align: center;
            font-size: 12px;
            min-width: 30px;
            color: #666;
        }}
        .task-row {{
            display: flex;
            margin-bottom: 15px;
            align-items: center;
        }}
        .task-label {{
            width: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-weight: bold;
            color: #333;
        }}
        .task-timeline {{
            flex-grow: 1;
            position: relative;
            height: 30px;
            border-radius: 4px;
            background-color: #f0f0f0;
        }}
        .task-bar {{
            position: absolute;
            height: 100%;
            background-color: #4caf50;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        .task-bar:hover {{
            background-color: #3e8e41;
        }}
        .task-progress {{
            position: absolute;
            height: 100%;
            background-color: rgba(0,0,0,0.1);
            bottom: 0;
        }}
        .tooltip {{
            display: none;
            position: absolute;
            bottom: 105%; /* 定位到任务条下方 */
            left: 50%;    /* 水平居中 */
            transform: translateX(-50%); /* 精确水平居中 */
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.16);
            z-index: 1000;
            font-size: 12px;
            min-width: 200px;
            pointer-events: none;
        }}
        .task-bar:hover .tooltip {{
            display: block;
        }}
        .no-tasks {{
            color: #666;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="project-info">
        <h1>{project["name"]} - Gantt Chart</h1>
        <p><strong>Project ID:</strong> {project_id}</p>
        <p><strong>Owner:</strong> {project.get("owner", "None")}</p>
        <p><strong>Created:</strong> {datetime.fromisoformat(project["created_at"]).strftime("%Y-%m-%d %H:%M")}</p>
        <p><strong>Tasks:</strong> {len(tasks)}</p>
    </div>
    
    <div class="gantt-container">
        <h2>Tasks Timeline</h2>
        
        <div class="gantt-chart">
            <!-- Timeline header -->
            <div class="timeline">
"""
    
    # Add day labels
    current_date = min_date
    for _ in range(total_days):
        date_str = current_date.strftime("%m-%d")
        html += f'                <div class="day">{date_str}</div>\n'
        current_date += timedelta(days=1)
    
    html += """            </div>
            
            <!-- Task bars -->
"""
    
    if task_list:
        for task in task_list:
            html += f"""            <div class="task-row">
                <div class="task-label" title="{task['name']}">{task['name']}</div>
                <div class="task-timeline">
                    <div class="task-bar" style="left: {task['start_pos']}%; width: {task['width']}%;">
                        {task['name']}
                        <div class="tooltip">
                            <p><strong>Task:</strong> {task['name']}</p>
                            <p><strong>Owner:</strong> {task['owner']}</p>
                            <p><strong>Start:</strong> {task['start_date']}</p>
                            <p><strong>End:</strong> {task['end_date']}</p>
                            <p><strong>Progress:</strong> {task['progress']}%</p>
                        </div>
                        <div class="task-progress" style="width: {task['progress']}%;"></div>
                    </div>
                </div>
            </div>
"""
    else:
        html += """            <div class="no-tasks">
                No tasks added to this project yet.
            </div>
"""
    
    html += """        </div>
    </div>
    
    <script>
        // You can add JavaScript to enhance the chart if needed
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Gantt chart loaded');
        });
    </script>
</body>
</html>"""
    
    return html

def generate_inline_gantt_html(project_id: str, project: Dict[str, Any], max_width: int = 600) -> str:
    """
    Generate simplified inline HTML content for a Gantt chart suitable for embedding in chat interfaces.
    
    Args:
        project_id: ID of the project
        project: Project data
        max_width: Maximum width of the gantt chart in pixels
        
    Returns:
        Simplified HTML content that can be embedded in chat messages
    """
    tasks = project["tasks"]
    
    # Find the earliest start date and latest end date to determine chart range
    if tasks:
        # Initialize with the first task's dates
        all_dates = [(datetime.fromisoformat(task["start_date"]).date(), 
                      datetime.fromisoformat(task["end_date"]).date())
                     for task in tasks.values()]
        
        if all_dates:
            min_date = min(date[0] for date in all_dates)
            max_date = max(date[1] for date in all_dates)
        else:
            # Default to current week if no tasks
            today = datetime.now().date()
            min_date = today
            max_date = today + timedelta(days=7)
    else:
        # Default to current week if no tasks
        today = datetime.now().date()
        min_date = today
        max_date = today + timedelta(days=7)
    
    # Add some padding to the date range
    min_date = min_date - timedelta(days=1)
    max_date = max_date + timedelta(days=1)
    
    # Calculate total days for the chart
    total_days = (max_date - min_date).days + 1
    
    # Prepare tasks for the chart
    task_list = []
    for task_id, task in tasks.items():
        start_date = datetime.fromisoformat(task["start_date"]).date()
        end_date = datetime.fromisoformat(task["end_date"]).date()
        
        # Calculate position and width as percentages
        start_pos = ((start_date - min_date).days / total_days) * 100
        width = ((end_date - start_date).days + 1) / total_days * 100
        
        task_list.append({
            "id": task_id,
            "name": task["name"],
            "start_pos": start_pos,
            "width": width,
            "start_date": task["start_date"],
            "end_date": task["end_date"],
            "progress": task.get("progress", 0),
            "owner": task.get("owner", "None")
        })
    
    # Generate the inline HTML - optimized for chat interfaces
    html = f"""<div style="font-family: Arial, sans-serif; max-width: {max_width}px; margin: 0 auto; background-color: #fff; border-radius: 8px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee;">
        <h3 style="margin: 0; color: #333; font-size: 16px;">{project["name"]} - Gantt Chart</h3>
        <div style="font-size: 12px; color: #666;">
            <span>Project ID: {project_id} | </span>
            <span>Owner: {project.get("owner", "None")} | </span>
            <span>Tasks: {len(tasks)}</span>
        </div>
    </div>
    
    <div style="overflow-x: auto;">
        <div style="min-width: {max_width-20}px;">
            <!-- Timeline header -->
            <div style="display: flex; border-bottom: 1px solid #ddd; margin-bottom: 8px; padding-bottom: 4px;">
"""
    
    # Add day labels
    current_date = min_date
    for _ in range(total_days):
        date_str = current_date.strftime("%m-%d")
        html += f'<div style="flex: 1; text-align: center; font-size: 10px; min-width: 24px; color: #888;">{date_str}</div>\n'
        current_date += timedelta(days=1)
    
    html += """</div>
            
            <!-- Task bars -->
"""
    
    if task_list:
        for task in task_list:
            # Use a lighter green for better visual in chat
            bar_color = "#4caf50"
            html += f"""<div style="display: flex; margin-bottom: 10px; align-items: center;">
                <div style="width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: bold; font-size: 12px; color: #333; padding-right: 5px;" title="{task['name']}">{task['name']}</div>
                <div style="flex-grow: 1; position: relative; height: 20px; border-radius: 3px; background-color: {bar_color}; border-radius: 3px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); left: {task['start_pos']}%; width: {task['width']}%; font-size: 10px; color: white; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;">
                    {task['name']}
                </div>
            </div>
"""
    else:
        html += """<div style="color: #666; font-style: italic; padding: 10px; text-align: center; font-size: 12px;">
                No tasks added to this project yet.
            </div>
"""
    
    html += """        </div>
    </div>
    <div style="text-align: right; font-size: 10px; color: #999; margin-top: 5px;">Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """</div>
</div>"""
    
    return html

def generate_gantt_chart(project_id: str) -> Dict[str, Any]:
    """
    Generate a Gantt chart for the specified project and return the link.
    
    Args:
        project_id: ID of the project to generate the Gantt chart for
        
    Returns:
        Dictionary containing the link to the Gantt chart and project info
        
    Raises:
        ValueError: If project doesn't exist
    """
    # Validate project_id
    if not project_id or not isinstance(project_id, str):
        raise ValueError("Project ID must be a non-empty string")
    
    # Check if project exists
    if not project_exists(project_id):
        raise ValueError(f"Project with ID '{project_id}' does not exist")
    
    # Get project data
    project = gantt_data[project_id]
    
    # Create HTML content for the Gantt chart
    html_content = generate_gantt_html(project_id, project)
    
    # Create file name with timestamp to avoid caching issues
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"gantt_{project_id}_{timestamp}.html"
    filepath = os.path.join(CHARTS_DIR, filename)
    
    # Write the HTML to a file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Get the absolute file path
    abs_filepath = os.path.abspath(filepath)
    
    # Create a file URL
    file_url = f"file://{abs_filepath}"
    
    return {
        "project_id": project_id,
        "project_name": project["name"],
        "task_count": len(project["tasks"]),
        "chart_file": abs_filepath,
        "chart_url": file_url
    } 