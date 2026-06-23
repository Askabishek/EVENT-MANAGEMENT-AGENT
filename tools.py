"""Event Task Manager Tools for Google ADK Agent"""
from datetime import datetime
from typing import Optional

_tasks = {}
_connections = {}
_notes = {}
_task_counter = 1


def create_task(title: str, description: str, priority: str = "medium",
                deadline: Optional[str] = None, event_name: Optional[str] = None) -> dict:
    """Create a new event-related task.
    Args:
        title: Short title of the task
        description: Detailed description
        priority: 'low', 'medium', or 'high'
        deadline: Optional deadline YYYY-MM-DD
        event_name: Event this task belongs to
    Returns: Created task details
    """
    global _task_counter
    task_id = f"task_{_task_counter}"
    _task_counter += 1
    task = {"task_id": task_id, "title": title, "description": description,
            "priority": priority, "deadline": deadline, "event_name": event_name,
            "status": "pending", "created_at": datetime.now().isoformat()}
    _tasks[task_id] = task
    return {"success": True, "task": task, "message": f"Task '{title}' created with ID {task_id}"}


def list_tasks(status: Optional[str] = None, priority: Optional[str] = None,
               event_name: Optional[str] = None) -> dict:
    """List tasks with optional filters.
    Args:
        status: 'pending', 'in_progress', or 'done'
        priority: 'low', 'medium', or 'high'
        event_name: Filter by event
    Returns: List of tasks
    """
    tasks = list(_tasks.values())
    if status: tasks = [t for t in tasks if t["status"] == status]
    if priority: tasks = [t for t in tasks if t["priority"] == priority]
    if event_name: tasks = [t for t in tasks if t.get("event_name") == event_name]
    return {"success": True, "tasks": tasks, "count": len(tasks)}


def update_task_status(task_id: str, status: str) -> dict:
    """Update task status.
    Args:
        task_id: ID of the task
        status: 'pending', 'in_progress', or 'done'
    Returns: Updated task
    """
    if task_id not in _tasks:
        return {"success": False, "message": f"Task {task_id} not found"}
    _tasks[task_id]["status"] = status
    _tasks[task_id]["updated_at"] = datetime.now().isoformat()
    return {"success": True, "task": _tasks[task_id], "message": f"Task updated to '{status}'"}


def add_connection(name: str, role: str, event_name: str,
                   notes: Optional[str] = None, contact: Optional[str] = None) -> dict:
    """Add a speaker or connection met at an event.
    Args:
        name: Full name of the person
        role: Their role e.g. Speaker, Developer
        event_name: Event where you met them
        notes: What you discussed
        contact: LinkedIn, email, GitHub etc.
    Returns: Created connection
    """
    conn_id = f"conn_{len(_connections)+1}"
    connection = {"conn_id": conn_id, "name": name, "role": role,
                  "event_name": event_name, "notes": notes, "contact": contact,
                  "met_at": datetime.now().isoformat()}
    _connections[conn_id] = connection
    return {"success": True, "connection": connection, "message": f"Connection '{name}' added!"}


def list_connections(event_name: Optional[str] = None) -> dict:
    """List all connections.
    Args:
        event_name: Optional filter by event
    Returns: List of connections
    """
    conns = list(_connections.values())
    if event_name: conns = [c for c in conns if c["event_name"] == event_name]
    return {"success": True, "connections": conns, "count": len(conns)}


def add_event_note(event_name: str, topic: str, content: str) -> dict:
    """Save a learning note from an event.
    Args:
        event_name: Name of the event
        topic: Topic of the note e.g. ADK Overview
        content: Key learnings
    Returns: Created note
    """
    note_id = f"note_{len(_notes)+1}"
    note = {"note_id": note_id, "event_name": event_name, "topic": topic,
            "content": content, "created_at": datetime.now().isoformat()}
    _notes[note_id] = note
    return {"success": True, "note": note, "message": f"Note on '{topic}' saved!"}


def get_event_summary(event_name: str) -> dict:
    """Get full summary of tasks, connections and notes for an event.
    Args:
        event_name: Event name to summarize
    Returns: Full event summary
    """
    tasks = [t for t in _tasks.values() if t.get("event_name") == event_name]
    conns = [c for c in _connections.values() if c.get("event_name") == event_name]
    notes = [n for n in _notes.values() if n.get("event_name") == event_name]
    return {"success": True, "event_name": event_name,
            "summary": {"total_tasks": len(tasks),
                        "pending": len([t for t in tasks if t["status"] == "pending"]),
                        "done": len([t for t in tasks if t["status"] == "done"]),
                        "connections": len(conns), "notes": len(notes)},
            "tasks": tasks, "connections": conns, "notes": notes}
