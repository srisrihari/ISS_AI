from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.schemas import ItemBase, PlacementItem, RearrangementStep, Position, Coordinates
from ..models.database import Item, Container, Log, SessionLocal

class EmergencyService:
    """
    Service for managing emergency protocols and ensuring critical items
    are easily accessible during emergency situations.
    """
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        self.db.close()
    
    def identify_critical_items(self) -> List[Dict]:
        """
        Identify high-priority items that should be accessible in emergencies.
        Returns a list of critical items with their accessibility status.
        """
        # Find high-priority items (90+)
        critical_items = self.db.query(Item).filter(Item.priority >= 90).all()
        
        result = []
        for item in critical_items:
            # Check if the item is easily accessible
            accessibility_score = self._calculate_accessibility(item)
            
            result.append({
                "itemId": item.id,
                "name": item.name,
                "priority": item.priority,
                "containerId": item.container_id,
                "zone": self._get_container_zone(item.container_id) if item.container_id else None,
                "accessibilityScore": accessibility_score,
                "isAccessible": accessibility_score >= 0.8,
                "retrievalSteps": self._count_retrieval_steps(item)
            })
        
        # Sort by priority (highest first) and then by accessibility (most accessible first)
        result.sort(key=lambda x: (-x["priority"], -x["accessibilityScore"]))
        
        return result
    
    def optimize_emergency_access(self) -> Dict:
        """
        Rearrange items to ensure critical items are easily accessible.
        Returns a summary of the optimization results.
        """
        # Identify critical items that are not easily accessible
        critical_items_data = self.identify_critical_items()
        items_to_optimize = [item for item in critical_items_data if not item["isAccessible"]]
        
        if not items_to_optimize:
            return {
                "success": True,
                "message": "All critical items are already easily accessible",
                "optimizedItems": 0,
                "criticalItems": len(critical_items_data)
            }
        
        optimized_count = 0
        
        # Process each item that needs optimization
        for item_data in items_to_optimize:
            item_id = item_data["itemId"]
            container_id = item_data["containerId"]
            
            if not container_id:
                continue  # Skip items not in containers
            
            # Get the item and container
            item = self.db.query(Item).filter(Item.id == item_id).first()
            container = self.db.query(Container).filter(Container.id == container_id).first()
            
            if not item or not container:
                continue
            
            # Try to optimize position
            success = self._optimize_item_position(item, container)
            
            if success:
                optimized_count += 1
        
        # Commit changes
        self.db.commit()
        
        # Get updated data
        updated_critical_items = self.identify_critical_items()
        
        return {
            "success": True,
            "message": f"Optimized {optimized_count} critical items for emergency access",
            "optimizedItems": optimized_count,
            "criticalItems": len(critical_items_data),
            "items": updated_critical_items
        }
    
    def declare_emergency(self, emergency_type: str, affected_zones: List[str] = None) -> Dict:
        """
        Declare an emergency and get quick access plans for critical items.
        Returns emergency response plan with critical items access instructions.
        """
        # Get current timestamp
        timestamp = datetime.utcnow()
        
        # Log emergency declaration
        log = Log(
            timestamp=timestamp,
            user_id="system",
            action_type="emergency_declaration",
            item_id="N/A",
            from_container=None,
            to_container=None,
            reason=emergency_type,
            details=f"Emergency declared: {emergency_type}, Affected zones: {affected_zones}"
        )
        self.db.add(log)
        
        # Identify critical items
        all_critical_items = self.identify_critical_items()
        
        # Filter by affected zones if specified
        critical_items = all_critical_items
        if affected_zones:
            critical_items = [item for item in all_critical_items if not item["zone"] or item["zone"] in affected_zones]
        
        # Get quick access plans for each critical item
        access_plans = []
        for item_data in critical_items:
            # Get retrieval steps
            item = self.db.query(Item).filter(Item.id == item_data["itemId"]).first()
            if not item or not item.container_id:
                continue
                
            retrieval_steps = self._get_retrieval_steps(item)
            
            access_plans.append({
                "itemId": item_data["itemId"],
                "name": item_data["name"],
                "priority": item_data["priority"],
                "containerId": item_data["containerId"],
                "zone": item_data["zone"],
                "isAccessible": item_data["isAccessible"],
                "retrievalSteps": retrieval_steps
            })
        
        # Sort by priority (highest first) and then by accessibility (most accessible first)
        access_plans.sort(key=lambda x: (-x["priority"], len(x["retrievalSteps"])))
        
        # Commit the log
        self.db.commit()
        
        return {
            "success": True,
            "emergencyType": emergency_type,
            "affectedZones": affected_zones,
            "timestamp": timestamp.isoformat(),
            "criticalItems": len(access_plans),
            "accessPlans": access_plans
        }
    
    def _calculate_accessibility(self, item: Item) -> float:
        """
        Calculate an accessibility score for an item (0-1).
        Higher scores indicate better accessibility.
        """
        if not item.container_id:
            return 0.0  # Item not in a container
        
        # Get retrieval step count
        retrieval_steps = self._count_retrieval_steps(item)
        
        # Calculate position-based accessibility
        # Items closer to the container opening (lower depth) are more accessible
        container = self.db.query(Container).filter(Container.id == item.container_id).first()
        if not container:
            return 0.0
        
        # Calculate depth ratio (0 at the front, 1 at the back)
        depth_ratio = item.position_depth / container.depth if container.depth > 0 else 1.0
        
        # Calculate accessibility score
        # 1. No retrieval steps needed = 1.0
        if retrieval_steps == 0:
            retrieval_score = 1.0
        # 2. 1-2 steps = 0.8
        elif retrieval_steps <= 2:
            retrieval_score = 0.8
        # 3. 3-5 steps = 0.5
        elif retrieval_steps <= 5:
            retrieval_score = 0.5
        # 4. More than 5 steps = 0.2
        else:
            retrieval_score = 0.2
        
        # Final score combines retrieval steps and position depth
        # Weight retrieval steps more heavily (70%) than depth (30%)
        return (0.7 * retrieval_score) + (0.3 * (1.0 - depth_ratio))
    
    def _count_retrieval_steps(self, item: Item) -> int:
        """
        Count the number of steps needed to retrieve an item.
        This is a simplified version that counts the number of items that need to be moved.
        """
        if not item.container_id:
            return 0  # Item not in a container
        
        # Get all items in the same container
        items_in_container = self.db.query(Item).filter(
            Item.container_id == item.container_id,
            Item.id != item.id
        ).all()
        
        # Count items that block access to this item
        blocking_items = 0
        for other_item in items_in_container:
            # An item blocks access if:
            # 1. It's in front of our target item (lower depth)
            # 2. It overlaps with our item in width and height
            if (other_item.position_depth < item.position_depth and
                self._check_overlap(
                    (other_item.position_width, other_item.position_width + other_item.width),
                    (item.position_width, item.position_width + item.width)
                ) and
                self._check_overlap(
                    (other_item.position_height, other_item.position_height + other_item.height),
                    (item.position_height, item.position_height + item.height)
                )):
                blocking_items += 1
        
        return blocking_items

    def _check_overlap(self, range1: Tuple[float, float], range2: Tuple[float, float]) -> bool:
        """Helper function to check if two ranges overlap."""
        return not (range1[1] <= range2[0] or range2[1] <= range1[0])
    
    def _get_container_zone(self, container_id: Optional[str]) -> Optional[str]:
        """
        Get the zone of a container.
        Returns None if container_id is None or container not found.
        """
        if not container_id:
            return None
            
        container = self.db.query(Container).filter(Container.id == container_id).first()
        return container.zone if container else None
    
    def _optimize_item_position(self, item: Item, container: Container) -> bool:
        """
        Optimize the position of a critical item for better accessibility.
        Returns True if successful, False otherwise.
        """
        # Strategy: Move the item to the front of the container if possible
        
        # Get container dimensions
        width, depth, height = int(container.width), int(container.depth), int(container.height)
        
        # Create a 3D grid of the container to track occupied space
        grid = np.zeros((width, depth, height), dtype=bool)
        
        # Mark all items in the container as occupied
        items_in_container = self.db.query(Item).filter(
            Item.container_id == container.id,
            Item.id != item.id
        ).all()
        
        for other_item in items_in_container:
            x1, y1, z1 = int(other_item.position_width), int(other_item.position_depth), int(other_item.position_height)
            x2, y2, z2 = x1 + int(other_item.width), y1 + int(other_item.depth), z1 + int(other_item.height)
            grid[x1:x2, y1:y2, z1:z2] = True
        
        # Try to find a position at the front of the container
        for x in range(width - int(item.width) + 1):
            for z in range(height - int(item.height) + 1):
                # Check if space is available at the front (depth=0)
                if not np.any(grid[x:x+int(item.width), 0:int(item.depth), z:z+int(item.height)]):
                    # Found an available position at the front
                    item.position_width = float(x)
                    item.position_depth = 0.0
                    item.position_height = float(z)
                    return True
        
        # If front positions are not available, try positions with minimal depth
        min_depth = float('inf')
        best_position = None
        
        for x in range(width - int(item.width) + 1):
            for y in range(depth - int(item.depth) + 1):
                for z in range(height - int(item.height) + 1):
                    if not np.any(grid[x:x+int(item.width), y:y+int(item.depth), z:z+int(item.height)]):
                        if y < min_depth:
                            min_depth = y
                            best_position = (x, y, z)
        
        if best_position:
            x, y, z = best_position
            item.position_width = float(x)
            item.position_depth = float(y)
            item.position_height = float(z)
            return True
        
        return False
    
    def _get_retrieval_steps(self, item: Item) -> List[Dict]:
        """
        Get detailed steps for retrieving an item.
        Returns a list of step descriptions.
        """
        if not item.container_id:
            return []  # Item not in a container
        
        # Get all items in the same container
        items_in_container = self.db.query(Item).filter(
            Item.container_id == item.container_id,
            Item.id != item.id
        ).all()
        
        # Check if item is directly accessible (at the front of the container)
        if item.position_depth == 0:
            return [{
                "step": 1,
                "action": "retrieve",
                "itemId": item.id,
                "itemName": item.name,
                "description": f"Retrieve {item.name} directly from the front of container {item.container_id}"
            }]
        
        # Find items that block access to this item
        blocking_items = []
        for other_item in items_in_container:
            # An item blocks access if:
            # 1. It's in front of our target item (lower depth)
            # 2. It overlaps with our item in width and height
            if (other_item.position_depth < item.position_depth and
                self._check_overlap(
                    (other_item.position_width, other_item.position_width + other_item.width),
                    (item.position_width, item.position_width + item.width)
                ) and
                self._check_overlap(
                    (other_item.position_height, other_item.position_height + other_item.height),
                    (item.position_height, item.position_height + item.height)
                )):
                blocking_items.append(other_item)
        
        # Sort blocking items by depth (front to back)
        blocking_items.sort(key=lambda x: x.position_depth)
        
        # Create retrieval steps
        steps = []
        for i, blocking_item in enumerate(blocking_items, 1):
            steps.append({
                "step": i,
                "action": "move",
                "itemId": blocking_item.id,
                "itemName": blocking_item.name,
                "description": f"Move {blocking_item.name} to access {item.name}"
            })
        
        # Add final retrieval step
        steps.append({
            "step": len(steps) + 1,
            "action": "retrieve",
            "itemId": item.id,
            "itemName": item.name,
            "description": f"Retrieve {item.name} from container {item.container_id}"
        })
        
        return steps 