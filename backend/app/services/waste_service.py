from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone
from ..models.schemas import WasteItem, ReturnPlanStep, RetrievalStep, ReturnManifest, ReturnManifestItem, Position, Coordinates
from ..models.database import Item, Container, Log, SessionLocal

class WasteService:
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def identify_waste(self) -> List[WasteItem]:
        """
        Identify items that are waste (expired or out of uses).
        Returns a list of waste items.
        """
        # Get current date
        current_date = datetime.now(timezone.utc)

        # Find expired items that are not yet marked as waste
        expired_items = []
        potential_expired_items = self.db.query(Item).filter(
            Item.expiry_date.isnot(None),
            Item.is_waste == False
        ).all()

        # Filter items with expiry dates in the past
        for item in potential_expired_items:
            if item.expiry_date.replace(tzinfo=timezone.utc) < current_date:
                expired_items.append(item)

        # Find items out of uses that are not yet marked as waste
        depleted_items = self.db.query(Item).filter(
            Item.remaining_uses == 0,
            Item.is_waste == False
        ).all()

        # Find items already marked as waste
        existing_waste_items = self.db.query(Item).filter(
            Item.is_waste == True
        ).all()

        # Combine and deduplicate
        waste_items = []
        processed_ids = set()

        for item in expired_items:
            if item.id not in processed_ids and item.container_id:
                container = self.db.query(Container).filter(Container.id == item.container_id).first()

                if container:
                    waste_items.append(WasteItem(
                        itemId=item.id,
                        name=item.name,
                        reason="Expired",
                        containerId=item.container_id,
                        position=Position(
                            startCoordinates=Coordinates(
                                width=item.position_width,
                                depth=item.position_depth,
                                height=item.position_height
                            ),
                            endCoordinates=Coordinates(
                                width=item.position_width + item.width,
                                depth=item.position_depth + item.depth,
                                height=item.position_height + item.height
                            )
                        )
                    ))
                    processed_ids.add(item.id)

                    # Mark as waste in database
                    item.is_waste = True

        for item in depleted_items:
            if item.id not in processed_ids and item.container_id:
                container = self.db.query(Container).filter(Container.id == item.container_id).first()

                if container:
                    waste_items.append(WasteItem(
                        itemId=item.id,
                        name=item.name,
                        reason="Out of Uses",
                        containerId=item.container_id,
                        position=Position(
                            startCoordinates=Coordinates(
                                width=item.position_width,
                                depth=item.position_depth,
                                height=item.position_height
                            ),
                            endCoordinates=Coordinates(
                                width=item.position_width + item.width,
                                depth=item.position_depth + item.depth,
                                height=item.position_height + item.height
                            )
                        )
                    ))
                    processed_ids.add(item.id)

                    # Mark as waste in database
                    item.is_waste = True

        # Process existing waste items
        for item in existing_waste_items:
            if item.id not in processed_ids and item.container_id:
                container = self.db.query(Container).filter(Container.id == item.container_id).first()

                if container:
                    # Determine the reason for waste
                    reason = "Unknown"
                    if item.expiry_date and item.expiry_date.replace(tzinfo=timezone.utc) < current_date:
                        reason = "Expired"
                    elif item.remaining_uses == 0:
                        reason = "Out of Uses"

                    waste_items.append(WasteItem(
                        itemId=item.id,
                        name=item.name,
                        reason=reason,
                        containerId=item.container_id,
                        position=Position(
                            startCoordinates=Coordinates(
                                width=item.position_width,
                                depth=item.position_depth,
                                height=item.position_height
                            ),
                            endCoordinates=Coordinates(
                                width=item.position_width + item.width,
                                depth=item.position_depth + item.depth,
                                height=item.position_height + item.height
                            )
                        )
                    ))
                    processed_ids.add(item.id)

        self.db.commit()
        return waste_items

    def create_return_plan(self, undocking_container_id: str, undocking_date: str, max_weight: float) -> Tuple[List[ReturnPlanStep], List[RetrievalStep], ReturnManifest]:
        """
        Create a plan for returning waste items.
        Returns a tuple of (return_plan, retrieval_steps, return_manifest)
        """
        # Parse undocking date
        try:
            undocking_date_dt = datetime.fromisoformat(undocking_date.replace('Z', '+00:00'))
        except ValueError:
            return [], [], ReturnManifest(
                undockingContainerId=undocking_container_id,
                undockingDate=undocking_date,
                returnItems=[],
                totalVolume=0.0,
                totalWeight=0.0
            )

        # Find the undocking container
        undocking_container = self.db.query(Container).filter(Container.id == undocking_container_id).first()

        if not undocking_container:
            return [], [], ReturnManifest(
                undockingContainerId=undocking_container_id,
                undockingDate=undocking_date,
                returnItems=[],
                totalVolume=0.0,
                totalWeight=0.0
            )

        # Find all waste items
        waste_items = self.db.query(Item).filter(Item.is_waste == True).all()

        if not waste_items:
            return [], [], ReturnManifest(
                undockingContainerId=undocking_container_id,
                undockingDate=undocking_date,
                returnItems=[],
                totalVolume=0.0,
                totalWeight=0.0
            )

        # Sort waste items by mass (heaviest first)
        waste_items.sort(key=lambda x: x.mass, reverse=True)

        # Calculate available space in undocking container
        available_volume = undocking_container.width * undocking_container.depth * undocking_container.height

        # Create return plan
        return_plan = []
        retrieval_steps = []
        return_items = []
        total_volume = 0.0
        total_weight = 0.0
        step_counter = 1

        for item in waste_items:
            # Check if adding this item would exceed weight limit
            if total_weight + item.mass > max_weight:
                continue

            # Calculate item volume
            item_volume = item.width * item.depth * item.height

            # Check if adding this item would exceed volume limit
            if total_volume + item_volume > available_volume:
                continue

            # Add item to return plan
            return_plan.append(ReturnPlanStep(
                step=step_counter,
                itemId=item.id,
                itemName=item.name,
                fromContainer=item.container_id,
                toContainer=undocking_container_id
            ))
            step_counter += 1

            # Calculate retrieval steps for this item
            if item.container_id:
                from app.services.retrieval_service import RetrievalService
                retrieval_service = RetrievalService()
                _, _, item_retrieval_steps = retrieval_service.find_item(item_id=item.id)

                # Adjust step numbers
                for i, step in enumerate(item_retrieval_steps):
                    step.step = len(retrieval_steps) + i + 1

                retrieval_steps.extend(item_retrieval_steps)

            # Add item to return manifest
            return_items.append(ReturnManifestItem(
                itemId=item.id,
                name=item.name,
                reason="Waste"
            ))

            # Update totals
            total_volume += item_volume
            total_weight += item.mass

        # Create return manifest
        return_manifest = ReturnManifest(
            undockingContainerId=undocking_container_id,
            undockingDate=undocking_date,
            returnItems=return_items,
            totalVolume=total_volume,
            totalWeight=total_weight
        )

        return return_plan, retrieval_steps, return_manifest

    def complete_undocking(self, undocking_container_id: str, timestamp: str) -> int:
        """
        Complete the undocking process by removing waste items.
        Returns the number of items removed.
        """
        # Parse timestamp
        try:
            timestamp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return 0

        # Find all waste items in the undocking container
        waste_items = self.db.query(Item).filter(
            Item.container_id == undocking_container_id,
            Item.is_waste == True
        ).all()

        if not waste_items:
            return 0

        # Count items to be removed
        items_removed = len(waste_items)

        # Log the undocking
        for item in waste_items:
            log = Log(
                timestamp=timestamp_dt,
                user_id="system",
                action_type="disposal",
                item_id=item.id,
                from_container=undocking_container_id,
                to_container=None,
                reason="Undocking",
                details=f"Removed waste item {item.name} during undocking"
            )
            self.db.add(log)

            # Delete the item
            self.db.delete(item)

        self.db.commit()
        return items_removed
