from typing import List, Dict, Optional
from datetime import datetime
import json
from app.models.schemas import LogEntry
from app.models.database import Log, SessionLocal

class LogService:
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        self.db.close()
    
    def get_logs(self, start_date: str, end_date: str, item_id: Optional[str] = None, 
                user_id: Optional[str] = None, action_type: Optional[str] = None) -> List[LogEntry]:
        """
        Get logs filtered by various criteria.
        Returns a list of log entries.
        """
        # Parse dates
        try:
            start_date_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_date_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            return []
        
        # Build query
        query = self.db.query(Log).filter(
            Log.timestamp >= start_date_dt,
            Log.timestamp <= end_date_dt
        )
        
        # Apply additional filters
        if item_id:
            query = query.filter(Log.item_id == item_id)
        
        if user_id:
            query = query.filter(Log.user_id == user_id)
        
        if action_type:
            query = query.filter(Log.action_type == action_type)
        
        # Execute query
        logs = query.order_by(Log.timestamp.desc()).all()
        
        # Convert to response format
        log_entries = []
        
        for log in logs:
            # Build details dictionary
            details = {
                "fromContainer": log.from_container,
                "toContainer": log.to_container,
                "reason": log.reason
            }
            
            # Add any additional details from the details field
            if log.details:
                try:
                    additional_details = json.loads(log.details)
                    if isinstance(additional_details, dict):
                        details.update(additional_details)
                except:
                    # If details is not valid JSON, use it as a string
                    details["description"] = log.details
            
            log_entries.append(LogEntry(
                timestamp=log.timestamp.isoformat(),
                userId=log.user_id or "system",
                actionType=log.action_type,
                itemId=log.item_id,
                details=details
            ))
        
        return log_entries
