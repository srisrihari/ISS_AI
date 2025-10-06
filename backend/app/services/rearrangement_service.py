from typing import List, Dict, Tuple, Optional
from ..models.schemas import Position, Coordinates, RearrangementStep, PlacementItem
from ..utils.caching import cached
from ..utils.parallel_processing import parallel_execution
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class RearrangementScore:
    movement_count: int
    distance_moved: float
    stability_score: float
    accessibility_score: float
    priority_score: float

class EnhancedRearrangementService:
    def __init__(self):
        self.movement_weight = 0.3
        self.distance_weight = 0.2
        self.stability_weight = 0.2
        self.accessibility_weight = 0.2
        self.priority_weight = 0.1

    def calculate_rearrangement_score(self, items: List[PlacementItem], 
                                    moves: List[RearrangementStep]) -> RearrangementScore:
        """Calculate the overall score for a rearrangement plan"""
        movement_count = len(moves)
        distance_moved = sum(self._calculate_move_distance(move) for move in moves)
        stability_score = self._calculate_stability_score(items)
        accessibility_score = self._calculate_accessibility_score(items)
        priority_score = self._calculate_priority_score(items)
        
        return RearrangementScore(
            movement_count=movement_count,
            distance_moved=distance_moved,
            stability_score=stability_score,
            accessibility_score=accessibility_score,
            priority_score=priority_score
        )

    def _calculate_move_distance(self, move: RearrangementStep) -> float:
        """Calculate the 3D distance of a move"""
        start = move.fromPosition.startCoordinates
        end = move.toPosition.startCoordinates
        return np.sqrt(
            (end.width - start.width) ** 2 +
            (end.depth - start.depth) ** 2 +
            (end.height - start.height) ** 2
        )

    def _calculate_stability_score(self, items: List[PlacementItem]) -> float:
        """Calculate stability score based on support and center of mass"""
        total_score = 0
        for item in items:
            # Check if item has support below
            has_support = any(
                self._is_supporting(other, item)
                for other in items if other != item
            )
            # Calculate distance from center of mass to support
            com_distance = self._calculate_com_distance(item, items)
            item_score = 1.0 if has_support else 0.5
            item_score *= max(0, 1 - (com_distance / 10))  # Normalize by max expected distance
            total_score += item_score
        return total_score / len(items) if items else 0

    def _calculate_accessibility_score(self, items: List[PlacementItem]) -> float:
        """Calculate how accessible items are based on blocking"""
        total_score = 0
        for item in items:
            blocking_items = sum(
                1 for other in items
                if self._is_blocking(other, item)
            )
            item_score = 1.0 / (1 + blocking_items)  # Higher score for fewer blocking items
            total_score += item_score
        return total_score / len(items) if items else 0

    def _calculate_priority_score(self, items: List[PlacementItem]) -> float:
        """Calculate score based on item priorities and their accessibility"""
        total_score = 0
        for item in items:
            blocking_items = sum(
                1 for other in items
                if self._is_blocking(other, item)
            )
            priority_factor = item.priority / 10  # Normalize priority to 0-1
            item_score = priority_factor * (1.0 / (1 + blocking_items))
            total_score += item_score
        return total_score / len(items) if items else 0

    @staticmethod
    def _is_supporting(item1: PlacementItem, item2: PlacementItem) -> bool:
        """Check if item1 is supporting item2"""
        return (
            item1.position.endCoordinates.height == item2.position.startCoordinates.height and
            item1.position.startCoordinates.width <= item2.position.endCoordinates.width and
            item2.position.startCoordinates.width <= item1.position.endCoordinates.width and
            item1.position.startCoordinates.depth <= item2.position.endCoordinates.depth and
            item2.position.startCoordinates.depth <= item1.position.endCoordinates.depth
        )

    @staticmethod
    def _is_blocking(item1: PlacementItem, item2: PlacementItem) -> bool:
        """Check if item1 is blocking access to item2"""
        return (
            item1.position.startCoordinates.width < item2.position.endCoordinates.width and
            item2.position.startCoordinates.width < item1.position.endCoordinates.width and
            item1.position.startCoordinates.depth < item2.position.endCoordinates.depth and
            item2.position.startCoordinates.depth < item1.position.endCoordinates.depth and
            item1.position.startCoordinates.height < item2.position.startCoordinates.height
        )

    def _calculate_com_distance(self, item: PlacementItem, all_items: List[PlacementItem]) -> float:
        """Calculate distance from item's center of mass to nearest support"""
        item_com = (
            (item.position.startCoordinates.width + item.position.endCoordinates.width) / 2,
            (item.position.startCoordinates.depth + item.position.endCoordinates.depth) / 2
        )
        
        supporting_items = [
            other for other in all_items
            if self._is_supporting(other, item)
        ]
        
        if not supporting_items:
            return float('inf')
            
        min_distance = float('inf')
        for support in supporting_items:
            support_com = (
                (support.position.startCoordinates.width + support.position.endCoordinates.width) / 2,
                (support.position.startCoordinates.depth + support.position.endCoordinates.depth) / 2
            )
            distance = np.sqrt(
                (item_com[0] - support_com[0]) ** 2 +
                (item_com[1] - support_com[1]) ** 2
            )
            min_distance = min(min_distance, distance)
        
        return min_distance

    @cached(expire_seconds=3600)
    def optimize_rearrangement(self, items: List[PlacementItem], 
                             target_item: PlacementItem,
                             target_position: Position) -> List[RearrangementStep]:
        """
        Optimize the rearrangement of items to place target_item at target_position
        Uses a combination of strategies to minimize movements while maintaining stability
        """
        logger.info(f"Optimizing rearrangement for item {target_item.itemId}")
        
        # Find blocking items that need to be moved
        blocking_items = [
            item for item in items
            if self._is_blocking(item, target_item)
        ]
        
        # Sort blocking items by how many other items they're supporting
        blocking_items.sort(key=lambda x: sum(
            1 for item in items if self._is_supporting(x, item)
        ))
        
        # Generate possible moves for each blocking item
        moves = []
        for item in blocking_items:
            # Find potential positions that don't block other items
            potential_positions = self._find_potential_positions(item, items)
            
            # Score each potential position
            scored_positions = []
            for pos in potential_positions:
                # Create temporary arrangement with this move
                temp_items = [i for i in items if i != item]
                temp_item = PlacementItem(
                    itemId=item.itemId,
                    containerId=item.containerId,
                    position=pos,
                    priority=item.priority
                )
                temp_items.append(temp_item)
                
                # Calculate score for this arrangement
                score = self.calculate_rearrangement_score(temp_items, moves + [
                    RearrangementStep(
                        itemId=item.itemId,
                        fromPosition=item.position,
                        toPosition=pos
                    )
                ])
                
                total_score = (
                    self.movement_weight * (1 / (1 + score.movement_count)) +
                    self.distance_weight * (1 / (1 + score.distance_moved)) +
                    self.stability_weight * score.stability_score +
                    self.accessibility_weight * score.accessibility_score +
                    self.priority_weight * score.priority_score
                )
                
                scored_positions.append((pos, total_score))
            
            # Choose the best position
            if scored_positions:
                best_position = max(scored_positions, key=lambda x: x[1])[0]
                moves.append(RearrangementStep(
                    itemId=item.itemId,
                    fromPosition=item.position,
                    toPosition=best_position
                ))
                
                # Update item's position for subsequent calculations
                item.position = best_position
        
        logger.info(f"Generated {len(moves)} rearrangement steps")
        return moves

    def _find_potential_positions(self, item: PlacementItem, 
                                all_items: List[PlacementItem]) -> List[Position]:
        """Find potential positions for an item that maintain stability"""
        # Implementation would find valid positions in the container
        # This is a placeholder that would need to be implemented based on
        # your specific container and space management logic
        pass 