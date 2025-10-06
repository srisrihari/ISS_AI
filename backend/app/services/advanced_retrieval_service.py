from typing import List, Dict, Tuple, Optional, Set
import numpy as np
from datetime import datetime
from app.models.schemas import SearchItem, RetrievalStep, Position, Coordinates
from app.models.database import Item, Container, Log, SessionLocal

class AdvancedRetrievalService:
    """
    Advanced retrieval service with more sophisticated algorithms for optimizing
    item retrieval from containers.
    """
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        self.db.close()
    
    def find_item(self, item_id: Optional[str] = None, item_name: Optional[str] = None) -> Tuple[bool, Optional[SearchItem], List[RetrievalStep]]:
        """
        Find an item by ID or name using advanced retrieval optimization.
        Returns a tuple of (found, item_data, retrieval_steps)
        """
        # Query the database for the item
        query = self.db.query(Item)
        
        if item_id:
            query = query.filter(Item.id == item_id)
        elif item_name:
            query = query.filter(Item.name == item_name)
        else:
            return False, None, []
        
        # Get items that match the criteria
        items = query.all()
        
        if not items:
            return False, None, []
        
        # If multiple items match, choose the optimal one based on multiple factors
        best_item = None
        best_score = float('-inf')
        
        for item in items:
            if not item.container_id:
                continue  # Skip items not in a container
            
            # Calculate retrieval score
            score = self._calculate_retrieval_score(item)
            
            if score > best_score:
                best_score = score
                best_item = item
        
        if not best_item:
            return False, None, []
        
        # Get container information
        container = self.db.query(Container).filter(Container.id == best_item.container_id).first()
        
        if not container:
            return False, None, []
        
        # Create search item response
        item_data = SearchItem(
            itemId=best_item.id,
            name=best_item.name,
            containerId=container.id,
            zone=container.zone,
            position=Position(
                startCoordinates=Coordinates(
                    width=best_item.position_width,
                    depth=best_item.position_depth,
                    height=best_item.position_height
                ),
                endCoordinates=Coordinates(
                    width=best_item.position_width + best_item.width,
                    depth=best_item.position_depth + best_item.depth,
                    height=best_item.position_height + best_item.height
                )
            )
        )
        
        # Calculate optimal retrieval steps
        retrieval_steps = self._calculate_optimal_retrieval_steps(best_item)
        
        return True, item_data, retrieval_steps
    
    def _calculate_retrieval_score(self, item: Item) -> float:
        """
        Calculate a score for retrieving an item based on multiple factors:
        1. Ease of retrieval (fewer steps is better)
        2. Proximity to expiry (closer to expiry is better)
        3. Priority (higher priority is better)
        
        Returns a score where higher is better.
        """
        # Calculate retrieval steps
        retrieval_steps = self._calculate_optimal_retrieval_steps(item)
        steps_count = len(retrieval_steps)
        
        # Normalize steps count (fewer steps is better)
        # Assume max steps is 20
        steps_score = 1.0 - (steps_count / 20.0)
        
        # Calculate expiry score
        expiry_score = 0.0
        if item.expiry_date:
            days_until_expiry = (item.expiry_date - datetime.utcnow()).days
            # Normalize days until expiry (closer to expiry is better)
            # Assume max days is 365
            expiry_score = 1.0 - (max(0, min(days_until_expiry, 365)) / 365.0)
        
        # Normalize priority (higher priority is better)
        priority_score = item.priority / 100.0
        
        # Combine scores with weights
        return 0.5 * steps_score + 0.3 * expiry_score + 0.2 * priority_score
    
    def _calculate_optimal_retrieval_steps(self, item: Item) -> List[RetrievalStep]:
        """
        Calculate the optimal steps needed to retrieve an item.
        Uses a sophisticated algorithm that considers physical constraints:
        1. Gravity - items cannot float
        2. Support - items must have adequate support
        3. Accessibility - physical path for removal
        4. Stability - arrangement must remain stable during retrieval
        
        Returns a list of retrieval steps.
        """
        # Get all items in the same container
        items_in_container = self.db.query(Item).filter(
            Item.container_id == item.container_id,
            Item.id != item.id
        ).all()
        
        # Check if item is directly accessible (at the front of the container)
        if item.position_depth == 0:
            # Item is at the front, no steps needed
            return [
                RetrievalStep(
                    step=1,
                    action="retrieve",
                    itemId=item.id,
                    itemName=item.name
                )
            ]
        
        # Build a 3D grid representation of the container
        container = self.db.query(Container).filter(Container.id == item.container_id).first()
        if not container:
            return []
        
        # Create a grid for the container
        grid = np.zeros((int(container.width), int(container.depth), int(container.height)), dtype=int)
        
        # Map of item IDs to their index in the grid +1 (0 means empty)
        item_id_to_index = {}
        
        # Mark target item in the grid
        target_x1, target_y1, target_z1 = int(item.position_width), int(item.position_depth), int(item.position_height)
        target_x2, target_y2, target_z2 = (target_x1 + int(item.width), target_y1 + int(item.depth), target_z1 + int(item.height))
        
        # Assign an index to the target item
        item_id_to_index[item.id] = 1
        grid[target_x1:target_x2, target_y1:target_y2, target_z1:target_z2] = 1
        
        # Mark all other items in the grid with unique indices
        for idx, other_item in enumerate(items_in_container, start=2):
            x1, y1, z1 = int(other_item.position_width), int(other_item.position_depth), int(other_item.position_height)
            x2, y2, z2 = x1 + int(other_item.width), y1 + int(other_item.depth), z1 + int(other_item.height)
            item_id_to_index[other_item.id] = idx
            grid[x1:x2, y1:y2, z1:z2] = idx
        
        # Index to item ID mapping
        index_to_item = {v: k for k, v in item_id_to_index.items()}
        
        # Function to check if an item is directly blocking the target
        def is_blocking_direct_access(idx):
            # Get the item
            other_item = next((i for i in items_in_container if i.id == index_to_item.get(idx)), None)
            if not other_item:
                return False
                
            # Check if this item is in front of the target item (lower y value)
            if not (other_item.position_depth < item.position_depth):
                return False
                
            # Check for overlap in the x-z plane
            x_overlap = max(0, min(other_item.position_width + other_item.width, item.position_width + item.width) - 
                             max(other_item.position_width, item.position_width))
            z_overlap = max(0, min(other_item.position_height + other_item.height, item.position_height + item.height) - 
                             max(other_item.position_height, item.position_height))
                             
            return x_overlap > 0 and z_overlap > 0
        
        # Function to check which items are supported by an item
        def get_supported_items(idx):
            if idx == 0:  # Empty space doesn't support anything
                return []
                
            supported = []
            # Get the item
            supporting_item = next((i for i in [item] + items_in_container if i.id == index_to_item.get(idx)), None)
            if not supporting_item:
                return []
                
            # Get its position
            x1, y1, z1 = int(supporting_item.position_width), int(supporting_item.position_depth), int(supporting_item.position_height)
            x2, y2, z2 = x1 + int(supporting_item.width), y1 + int(supporting_item.depth), z1 + int(supporting_item.height)
            
            # Check items that might be supported by this one (items directly above)
            for i in range(2, len(item_id_to_index) + 2):  # Skip 0 (empty) and 1 (target)
                if i == idx:  # Skip self
                    continue
                    
                other_item = next((i for i in items_in_container if i.id == index_to_item.get(i)), None)
                if not other_item:
                    continue
                    
                # Check if this item is directly above the supporting item
                if other_item.position_height != z2:
                    continue
                    
                # Check for overlap in the x-y plane
                x_overlap = max(0, min(other_item.position_width + other_item.width, x2) - 
                                 max(other_item.position_width, x1))
                y_overlap = max(0, min(other_item.position_depth + other_item.depth, y2) - 
                                 max(other_item.position_depth, y1))
                                 
                # If there's significant overlap, consider it supported
                if x_overlap * y_overlap > 0.5 * other_item.width * other_item.depth:
                    supported.append(i)
                    
            return supported
        
        # Identify items that directly block access to the target
        direct_blockers = [idx for idx in range(2, len(item_id_to_index) + 2) if is_blocking_direct_access(idx)]
        
        # Identify items that need to be moved to maintain stability
        to_remove = set(direct_blockers)
        
        # Check for stability issues - items that would lose support
        for idx in direct_blockers:
            supported_items = get_supported_items(idx)
            to_remove.update(supported_items)
            
            # Recursively check items that depend on the supported items
            for supported_idx in supported_items:
                to_remove.update(get_supported_items(supported_idx))
        
        # Convert indices back to items
        to_remove_items = [next(i for i in items_in_container if i.id == index_to_item.get(idx)) for idx in to_remove if idx in index_to_item]
        
        # Sort by accessibility (depth and height) - remove items from front to back, top to bottom
        to_remove_items.sort(key=lambda x: (x.position_depth, -x.position_height))
        
        # Create retrieval steps
        steps = []
        step_counter = 1
        
        # First, remove blocking items
        for blocking_item in to_remove_items:
            steps.append(
                RetrievalStep(
                    step=step_counter,
                    action="remove",
                    itemId=blocking_item.id,
                    itemName=blocking_item.name
                )
            )
            step_counter += 1
            
            steps.append(
                RetrievalStep(
                    step=step_counter,
                    action="setAside",
                    itemId=blocking_item.id,
                    itemName=blocking_item.name
                )
            )
            step_counter += 1
        
        # Then retrieve the target item
        steps.append(
            RetrievalStep(
                step=step_counter,
                action="retrieve",
                itemId=item.id,
                itemName=item.name
            )
        )
        step_counter += 1
        
        # Finally, place back the blocking items in reverse order (from bottom to top, back to front)
        for blocking_item in reversed(to_remove_items):
            steps.append(
                RetrievalStep(
                    step=step_counter,
                    action="placeBack",
                    itemId=blocking_item.id,
                    itemName=blocking_item.name
                )
            )
            step_counter += 1
        
        return steps
    
    def _is_blocking(self, item: Item, target_item: Item, grid: np.ndarray, target_grid: np.ndarray) -> bool:
        """
        Determine if an item is blocking the path to the target item.
        Uses a more sophisticated algorithm that considers the 3D space.
        """
        # If the item is behind the target, it's not blocking
        if item.position_depth >= target_item.position_depth + target_item.depth:
            return False
        
        # If the item is in front of the target, check if it's in the way
        if item.position_depth < target_item.position_depth:
            # Check if there's any overlap in the x-z plane
            x1, z1 = int(item.position_width), int(item.position_height)
            x2, z2 = x1 + int(item.width), z1 + int(item.height)
            
            tx1, tz1 = int(target_item.position_width), int(target_item.position_height)
            tx2, tz2 = tx1 + int(target_item.width), tz1 + int(target_item.height)
            
            # Check for overlap in x dimension
            x_overlap = max(0, min(x2, tx2) - max(x1, tx1))
            # Check for overlap in z dimension
            z_overlap = max(0, min(z2, tz2) - max(z1, tz1))
            
            # If there's overlap in both dimensions, the item is blocking
            if x_overlap > 0 and z_overlap > 0:
                return True
        
        # If we get here, the item is not blocking
        return False
    
    def retrieve_item(self, item_id: str, user_id: str, timestamp: str) -> bool:
        """
        Mark an item as retrieved and update its usage count.
        Returns True if successful, False otherwise.
        """
        # Parse timestamp
        try:
            timestamp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return False
        
        # Find the item
        item = self.db.query(Item).filter(Item.id == item_id).first()
        
        if not item:
            return False
        
        # Update remaining uses
        if item.remaining_uses > 0:
            item.remaining_uses -= 1
        
        # Check if item is now waste
        if item.remaining_uses == 0:
            item.is_waste = True
        
        # Log the retrieval
        log = Log(
            timestamp=timestamp_dt,
            user_id=user_id,
            action_type="retrieval",
            item_id=item_id,
            from_container=item.container_id,
            to_container=None,
            reason=None,
            details=f"Retrieved item {item.name} from container {item.container_id}"
        )
        
        self.db.add(log)
        self.db.commit()
        
        return True
    
    def place_item(self, item_id: str, user_id: str, timestamp: str, container_id: str, position: Position) -> bool:
        """
        Place an item in a container.
        Returns True if successful, False otherwise.
        """
        # Parse timestamp
        try:
            timestamp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return False
        
        # Find the item
        item = self.db.query(Item).filter(Item.id == item_id).first()
        
        if not item:
            return False
        
        # Find the container
        container = self.db.query(Container).filter(Container.id == container_id).first()
        
        if not container:
            return False
        
        # Check if position is valid
        if (position.startCoordinates.width < 0 or 
            position.startCoordinates.depth < 0 or 
            position.startCoordinates.height < 0 or
            position.endCoordinates.width > container.width or
            position.endCoordinates.depth > container.depth or
            position.endCoordinates.height > container.height):
            return False
        
        # Check if position overlaps with other items
        overlapping_items = self.db.query(Item).filter(
            Item.container_id == container_id,
            Item.id != item_id,
            Item.position_width < position.endCoordinates.width,
            Item.position_width + Item.width > position.startCoordinates.width,
            Item.position_depth < position.endCoordinates.depth,
            Item.position_depth + Item.depth > position.startCoordinates.depth,
            Item.position_height < position.endCoordinates.height,
            Item.position_height + Item.height > position.startCoordinates.height
        ).all()
        
        if overlapping_items:
            return False
        
        # Get previous container
        from_container = item.container_id
        
        # Update item position
        item.container_id = container_id
        item.position_width = position.startCoordinates.width
        item.position_depth = position.startCoordinates.depth
        item.position_height = position.startCoordinates.height
        
        # Calculate new dimensions based on position
        item.width = position.endCoordinates.width - position.startCoordinates.width
        item.depth = position.endCoordinates.depth - position.startCoordinates.depth
        item.height = position.endCoordinates.height - position.startCoordinates.height
        
        # Log the placement
        log = Log(
            timestamp=timestamp_dt,
            user_id=user_id,
            action_type="placement",
            item_id=item_id,
            from_container=from_container,
            to_container=container_id,
            reason=None,
            details=f"Placed item {item.name} in container {container_id}"
        )
        
        self.db.add(log)
        self.db.commit()
        
        return True
