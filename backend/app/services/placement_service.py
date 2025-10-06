from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime
from ..models.schemas import ItemBase, ContainerBase, PlacementItem, RearrangementStep, Position, Coordinates
from ..models.database import Item, Container, Log, SessionLocal

class PlacementService:
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def place_items(self, items: List[ItemBase], containers: List[ContainerBase]) -> Tuple[List[PlacementItem], List[RearrangementStep]]:
        """
        Place items in containers optimally.
        Returns a tuple of (placements, rearrangements)
        """
        # Convert items and containers to internal format
        items_data = [self._convert_item_to_internal(item) for item in items]
        containers_data = {container.containerId: self._convert_container_to_internal(container) for container in containers}

        # Sort items by priority (highest first)
        items_data.sort(key=lambda x: x["priority"], reverse=True)

        placements = []
        rearrangements = []

        # Try to place each item
        for item in items_data:
            # First try to place in preferred zone
            preferred_zone = item["preferredZone"]
            preferred_containers = [c for c_id, c in containers_data.items() if c["zone"] == preferred_zone]

            # If no containers in preferred zone, try any container
            if not preferred_containers:
                preferred_containers = list(containers_data.values())

            # Sort containers by available space (most space first)
            preferred_containers.sort(key=lambda c: c["width"] * c["depth"] * c["height"], reverse=True)

            placed = False

            # Try each container
            for container in preferred_containers:
                # Try to place item in this container
                position = self._find_position_in_container(item, container)

                if position:
                    # Item can be placed in this container
                    placement = PlacementItem(
                        itemId=item["itemId"],
                        containerId=container["containerId"],
                        position=Position(
                            startCoordinates=Coordinates(
                                width=position[0],
                                depth=position[1],
                                height=position[2]
                            ),
                            endCoordinates=Coordinates(
                                width=position[0] + item["width"],
                                depth=position[1] + item["depth"],
                                height=position[2] + item["height"]
                            )
                        )
                    )
                    placements.append(placement)
                    placed = True

                    # Update container space
                    self._update_container_space(container, position, item)

                    # Save to database
                    self._save_placement_to_db(item, container["containerId"], position)

                    break

            # If item couldn't be placed, try rearrangement
            if not placed:
                # For simplicity, we'll just try to move one lower priority item
                # In a real implementation, this would be more sophisticated
                rearrangement_result = self._try_rearrangement(item, containers_data, items_data)

                if rearrangement_result:
                    rearrangements.extend(rearrangement_result[0])
                    placements.append(rearrangement_result[1])

        return placements, rearrangements

    def _convert_item_to_internal(self, item: ItemBase) -> Dict:
        """Convert Pydantic item model to internal dictionary format"""
        return {
            "itemId": item.itemId,
            "name": item.name,
            "width": item.width,
            "depth": item.depth,
            "height": item.height,
            "priority": item.priority,
            "expiryDate": item.expiryDate,
            "usageLimit": item.usageLimit,
            "preferredZone": item.preferredZone,
            "placed": False
        }

    def _convert_container_to_internal(self, container: ContainerBase) -> Dict:
        """Convert Pydantic container model to internal dictionary format"""
        return {
            "containerId": container.containerId,
            "zone": container.zone,
            "width": container.width,
            "depth": container.depth,
            "height": container.height,
            "space": np.zeros((int(container.width), int(container.depth), int(container.height)), dtype=bool),
            "items": []
        }

    def _find_position_in_container(self, item: Dict, container: Dict) -> Optional[Tuple[float, float, float]]:
        """
        Find a position for the item in the container.
        Returns (width, depth, height) coordinates or None if no position found.
        """
        # For simplicity, we'll use a first-fit approach
        # In a real implementation, this would be more sophisticated

        # Try different orientations of the item
        orientations = [
            (item["width"], item["depth"], item["height"]),
            (item["depth"], item["width"], item["height"]),
            (item["width"], item["height"], item["depth"]),
            (item["height"], item["width"], item["depth"]),
            (item["depth"], item["height"], item["width"]),
            (item["height"], item["depth"], item["width"])
        ]

        for w, d, h in orientations:
            # Check if item fits in container
            if w > container["width"] or d > container["depth"] or h > container["height"]:
                continue

            # Try to find a position
            for i in range(int(container["width"] - w + 1)):
                for j in range(int(container["depth"] - d + 1)):
                    for k in range(int(container["height"] - h + 1)):
                        # Check if space is available
                        if not np.any(container["space"][i:i+int(w), j:j+int(d), k:k+int(h)]):
                            return (float(i), float(j), float(k))

        return None

    def _update_container_space(self, container: Dict, position: Tuple[float, float, float], item: Dict):
        """Update the container space after placing an item"""
        i, j, k = int(position[0]), int(position[1]), int(position[2])
        w, d, h = int(item["width"]), int(item["depth"]), int(item["height"])

        # Mark space as occupied
        container["space"][i:i+w, j:j+d, k:k+h] = True

        # Add item to container's items
        container["items"].append({
            "itemId": item["itemId"],
            "position": position,
            "width": item["width"],
            "depth": item["depth"],
            "height": item["height"]
        })

    def _try_rearrangement(self, item: Dict, containers: Dict[str, Dict], items: List[Dict]) -> Optional[Tuple[List[RearrangementStep], PlacementItem]]:
        """
        Try to rearrange items to make space for the new item.
        Returns a tuple of (rearrangement_steps, placement) or None if not possible.
        """
        # This is a simplified implementation
        # In a real system, this would be more sophisticated

        # For now, we'll just try to find a lower priority item that can be moved
        lower_priority_items = [i for i in items if i["priority"] < item["priority"] and i["placed"]]

        if not lower_priority_items:
            return None

        # Sort by priority (lowest first)
        lower_priority_items.sort(key=lambda x: x["priority"])

        for lower_item in lower_priority_items:
            # Find where this item is currently placed
            for container_id, container in containers.items():
                for container_item in container["items"]:
                    if container_item["itemId"] == lower_item["itemId"]:
                        # Found the item, try to remove it
                        current_container = container
                        current_position = container_item["position"]

                        # Remove item from current container
                        i, j, k = int(current_position[0]), int(current_position[1]), int(current_position[2])
                        w, d, h = int(container_item["width"]), int(container_item["depth"]), int(container_item["height"])
                        current_container["space"][i:i+w, j:j+d, k:k+h] = False
                        current_container["items"].remove(container_item)

                        # Try to place the new item
                        new_position = self._find_position_in_container(item, current_container)

                        if new_position:
                            # New item can be placed here
                            placement = PlacementItem(
                                itemId=item["itemId"],
                                containerId=container_id,
                                position=Position(
                                    startCoordinates=Coordinates(
                                        width=new_position[0],
                                        depth=new_position[1],
                                        height=new_position[2]
                                    ),
                                    endCoordinates=Coordinates(
                                        width=new_position[0] + item["width"],
                                        depth=new_position[1] + item["depth"],
                                        height=new_position[2] + item["height"]
                                    )
                                )
                            )

                            # Update container space
                            self._update_container_space(current_container, new_position, item)

                            # Try to find a new place for the removed item
                            for alt_container_id, alt_container in containers.items():
                                if alt_container_id != container_id:  # Try a different container
                                    alt_position = self._find_position_in_container(lower_item, alt_container)

                                    if alt_position:
                                        # Lower priority item can be placed in another container
                                        rearrangement_steps = [
                                            RearrangementStep(
                                                step=1,
                                                action="remove",
                                                itemId=lower_item["itemId"],
                                                fromContainer=container_id,
                                                fromPosition=Position(
                                                    startCoordinates=Coordinates(
                                                        width=current_position[0],
                                                        depth=current_position[1],
                                                        height=current_position[2]
                                                    ),
                                                    endCoordinates=Coordinates(
                                                        width=current_position[0] + container_item["width"],
                                                        depth=current_position[1] + container_item["depth"],
                                                        height=current_position[2] + container_item["height"]
                                                    )
                                                ),
                                                toContainer="",
                                                toPosition=Position(
                                                    startCoordinates=Coordinates(width=0, depth=0, height=0),
                                                    endCoordinates=Coordinates(width=0, depth=0, height=0)
                                                )
                                            ),
                                            RearrangementStep(
                                                step=2,
                                                action="place",
                                                itemId=item["itemId"],
                                                fromContainer="",
                                                fromPosition=Position(
                                                    startCoordinates=Coordinates(width=0, depth=0, height=0),
                                                    endCoordinates=Coordinates(width=0, depth=0, height=0)
                                                ),
                                                toContainer=container_id,
                                                toPosition=Position(
                                                    startCoordinates=Coordinates(
                                                        width=new_position[0],
                                                        depth=new_position[1],
                                                        height=new_position[2]
                                                    ),
                                                    endCoordinates=Coordinates(
                                                        width=new_position[0] + item["width"],
                                                        depth=new_position[1] + item["depth"],
                                                        height=new_position[2] + item["height"]
                                                    )
                                                )
                                            ),
                                            RearrangementStep(
                                                step=3,
                                                action="place",
                                                itemId=lower_item["itemId"],
                                                fromContainer="",
                                                fromPosition=Position(
                                                    startCoordinates=Coordinates(width=0, depth=0, height=0),
                                                    endCoordinates=Coordinates(width=0, depth=0, height=0)
                                                ),
                                                toContainer=alt_container_id,
                                                toPosition=Position(
                                                    startCoordinates=Coordinates(
                                                        width=alt_position[0],
                                                        depth=alt_position[1],
                                                        height=alt_position[2]
                                                    ),
                                                    endCoordinates=Coordinates(
                                                        width=alt_position[0] + lower_item["width"],
                                                        depth=alt_position[1] + lower_item["depth"],
                                                        height=alt_position[2] + lower_item["height"]
                                                    )
                                                )
                                            )
                                        ]

                                        # Update alt_container space
                                        self._update_container_space(alt_container, alt_position, lower_item)

                                        return rearrangement_steps, placement

                        # If we couldn't place the new item or find a new place for the lower priority item,
                        # put the lower priority item back
                        self._update_container_space(current_container, current_position, container_item)

        return None

    def _save_placement_to_db(self, item, container_id, position):
        """Save the placement to the database"""
        try:
            # Find the item in the database
            db_item = self.db.query(Item).filter(Item.id == item["itemId"]).first()

            if db_item:
                # Update the item with the new container and position
                db_item.container_id = container_id
                db_item.position_width = position[0]
                db_item.position_depth = position[1]
                db_item.position_height = position[2]

                # Save to database
                self.db.commit()

                print(f"Saved placement of item {item['itemId']} to container {container_id}")
            else:
                print(f"Item {item['itemId']} not found in database")
        except Exception as e:
            self.db.rollback()
            print(f"Error saving placement to database: {str(e)}")
