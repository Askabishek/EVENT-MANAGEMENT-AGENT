"""
MongoDB Service - Chat history storage (free tier - MongoDB Atlas)
"""
import os
from datetime import datetime
from pymongo import MongoClient

_client = None
_db = None


def init_mongo():
    global _client, _db
    if _client is not None:
        return
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI secret not set!")
    _client = MongoClient(uri)
    _db = _client["event_task_manager"]


def get_collection():
    init_mongo()
    return _db["chat_sessions"]


def save_message(session_id: str, role: str, content: str):
    """Save a single message to MongoDB."""
    col = get_collection()
    message = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
    col.update_one(
        {"session_id": session_id},
        {"$push": {"messages": message}, "$set": {"updated_at": datetime.now().isoformat()}},
        upsert=True,
    )


def get_chat_history(session_id: str) -> list:
    """Load chat history for a session from MongoDB."""
    col = get_collection()
    doc = col.find_one({"session_id": session_id})
    if doc:
        return doc.get("messages", [])
    return []
