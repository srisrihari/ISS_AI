from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from ..models.schemas import SimulationItem, SimulationItemStatus, SimulationChanges
from ..models.database import Item, Log, SessionLocal

class SimulationService:
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        self.db.close()
    
    def simulate_days(self, num_of_days: Optional[int] = None, to_timestamp: Optional[str] = None, 
                     items_to_be_used_per_day: List[SimulationItem] = None) -> Tuple[str, SimulationChanges]:
        """
        Simulate the passage of time.
        Returns a tuple of (new_date, changes)
        """
        # Get current date from database or use current UTC time
        current_date_query = self.db.query(Log).order_by(Log.timestamp.desc()).first()
        
        if current_date_query:
            current_date = current_date_query.timestamp
        else:
            current_date = datetime.utcnow()
        
        # Calculate target date
        if to_timestamp:
            try:
                target_date = datetime.fromisoformat(to_timestamp.replace('Z', '+00:00'))
            except ValueError:
                target_date = current_date
        elif num_of_days:
            target_date = current_date + timedelta(days=num_of_days)
        else:
            target_date = current_date + timedelta(days=1)  # Default to one day
        
        # Ensure target date is in the future
        if target_date <= current_date:
            target_date = current_date + timedelta(days=1)
        
        # Calculate number of days to simulate
        days_to_simulate = (target_date - current_date).days
        
        # Initialize changes
        items_used = []
        items_expired = []
        items_depleted_today = []
        
        # Process each day
        for day in range(days_to_simulate):
            current_date += timedelta(days=1)
            
            # Process item usage for this day
            if items_to_be_used_per_day:
                for usage_item in items_to_be_used_per_day:
                    # Find the item in the database
                    if usage_item.itemId:
                        item = self.db.query(Item).filter(Item.id == usage_item.itemId).first()
                    elif usage_item.name:
                        item = self.db.query(Item).filter(Item.name == usage_item.name).first()
                    else:
                        continue
                    
                    if not item:
                        continue
                    
                    # Decrement remaining uses
                    if item.remaining_uses > 0:
                        item.remaining_uses -= 1
                        
                        # Add to items used
                        items_used.append(SimulationItemStatus(
                            itemId=item.id,
                            name=item.name,
                            remainingUses=item.remaining_uses
                        ))
                        
                        # Check if item is now depleted
                        if item.remaining_uses == 0:
                            item.is_waste = True
                            items_depleted_today.append(SimulationItemStatus(
                                itemId=item.id,
                                name=item.name
                            ))
            
            # Check for expired items
            expired_items_query = self.db.query(Item).filter(
                Item.expiry_date.isnot(None),
                Item.expiry_date <= current_date,
                Item.is_waste == False
            ).all()
            
            for item in expired_items_query:
                item.is_waste = True
                items_expired.append(SimulationItemStatus(
                    itemId=item.id,
                    name=item.name
                ))
            
            # Log the day simulation
            log = Log(
                timestamp=current_date,
                user_id="system",
                action_type="simulation",
                item_id="N/A",
                from_container=None,
                to_container=None,
                reason=None,
                details=f"Simulated day {current_date.strftime('%Y-%m-%d')}"
            )
            self.db.add(log)
        
        # Commit changes
        self.db.commit()
        
        # Create changes object
        changes = SimulationChanges(
            itemsUsed=items_used,
            itemsExpired=items_expired,
            itemsDepletedToday=items_depleted_today
        )
        
        return target_date.isoformat(), changes
