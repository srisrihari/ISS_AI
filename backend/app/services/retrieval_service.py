from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime
from ..models.schemas import SearchItem, RetrievalStep, Position, Coordinates
from ..models.database import Item, Container, Log, SessionLocal

class RetrievalService:
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def find_item(self, item_id: Optional[str] = None, item_name: Optional[str] = None) -> Tuple[bool, Optional[SearchItem], List[RetrievalStep]]:
        """
        Find an item by ID or name.
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

        # If multiple items match, choose the one that's easiest to retrieve
        # and closest to expiry
        best_item = None
        min_steps = float('inf')

        for item in items:
            if not item.container_id:
                continue  # Skip items not in a container

            # Calculate retrieval steps
            steps = self._calculate_retrieval_steps(item)

            # Check if this item is easier to retrieve or closer to expiry
            if len(steps) < min_steps:
                min_steps = len(steps)
                best_item = item
            elif len(steps) == min_steps and item.expiry_date:
                # If same number of steps, prefer the one closer to expiry
                if not best_item.expiry_date or item.expiry_date < best_item.expiry_date:
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

        # Calculate retrieval steps
        retrieval_steps = self._calculate_retrieval_steps(best_item)

        return True, item_data, retrieval_steps

    def retrieve_item(self, item_id: str, user_id: str, timestamp: str) -> bool:
        """
        Mark an item as retrieved and update its usage count.
        Returns True if successful, False otherwise.
        """
        # Parse timestamp
        try:
            print(f"Parsing timestamp: {timestamp}")
            timestamp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            print(f"Parsed timestamp: {timestamp_dt}")
        except ValueError as e:
            print(f"Error parsing timestamp: {str(e)}")
            return False

        # Find the item
        print(f"Finding item with ID: {item_id}")
        item = self.db.query(Item).filter(Item.id == item_id).first()

        if not item:
            print(f"Item not found: {item_id}")
            return False

        print(f"Found item: {item.id}, {item.name}, container: {item.container_id}")

        # Store the container ID before removing it
        original_container_id = item.container_id

        # Update remaining uses
        if item.remaining_uses > 0:
            item.remaining_uses -= 1

        # Check if item is now waste
        if item.remaining_uses == 0:
            item.is_waste = True

        # Mark the item as no longer in a container (retrieved)
        item.container_id = None
        item.position_width = None
        item.position_depth = None
        item.position_height = None

        # Log the retrieval
        log = Log(
            timestamp=timestamp_dt,
            user_id=user_id,
            action_type="retrieval",
            item_id=item_id,
            from_container=original_container_id,
            to_container=None,
            reason=None,
            details=f"Retrieved item {item.name} from container {original_container_id}"
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

    def _calculate_retrieval_steps(self, item: Item) -> List[RetrievalStep]:
        """
        Calculate steps needed to retrieve an item.
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

        # Find items that block access to this item
        blocking_items = []

        for other_item in items_in_container:
            # Check if other_item is in front of our item
            if (other_item.position_depth < item.position_depth and
                other_item.position_width < item.position_width + item.width and
                other_item.position_width + other_item.width > item.position_width and
                other_item.position_height < item.position_height + item.height and
                other_item.position_height + other_item.height > item.position_height):
                blocking_items.append(other_item)

        # Sort blocking items by depth (items at the front first)
        blocking_items.sort(key=lambda x: x.position_depth)

        # Create retrieval steps
        steps = []

        # First, remove blocking items
        for i, blocking_item in enumerate(blocking_items):
            steps.append(
                RetrievalStep(
                    step=i+1,
                    action="remove",
                    itemId=blocking_item.id,
                    itemName=blocking_item.name
                )
            )

            steps.append(
                RetrievalStep(
                    step=i+2,
                    action="setAside",
                    itemId=blocking_item.id,
                    itemName=blocking_item.name
                )
            )

        # Then retrieve the target item
        steps.append(
            RetrievalStep(
                step=len(steps)+1,
                action="retrieve",
                itemId=item.id,
                itemName=item.name
            )
        )

        # Finally, place back the blocking items in reverse order
        for i, blocking_item in enumerate(reversed(blocking_items)):
            steps.append(
                RetrievalStep(
                    step=len(steps)+1,
                    action="placeBack",
                    itemId=blocking_item.id,
                    itemName=blocking_item.name
                )
            )

        return steps
