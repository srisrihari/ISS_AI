from typing import List, Dict, Optional
from ..models.schemas import SearchResult, SearchFilter, ItemDetails
from ..models.database import Item, Container, SessionLocal
from sqlalchemy import or_, desc
from ..utils.caching import cached
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class EnhancedSearchService:
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    @cached(expire_seconds=1800)
    def search_items(self, query: str, filters: SearchFilter = None) -> List[SearchResult]:
        """
        Search for items with advanced filtering and priority-based sorting
        """
        logger.info(f"Searching for items with query: {query}")
        
        # Base query
        base_query = self.db.query(Item)
        
        # Apply text search
        if query:
            base_query = base_query.filter(
                or_(
                    Item.name.ilike(f"%{query}%"),
                    Item.description.ilike(f"%{query}%"),
                    Item.category.ilike(f"%{query}%"),
                    Item.tags.any(lambda tag: tag.ilike(f"%{query}%"))
                )
            )
        
        # Apply filters
        if filters:
            if filters.priority:
                base_query = base_query.filter(Item.priority >= filters.priority)
            
            if filters.category:
                base_query = base_query.filter(Item.category == filters.category)
            
            if filters.container_id:
                base_query = base_query.filter(Item.container_id == filters.container_id)
            
            if filters.expiry_before:
                base_query = base_query.filter(Item.expiry_date <= filters.expiry_before)
            
            if filters.expiry_after:
                base_query = base_query.filter(Item.expiry_date >= filters.expiry_after)
            
            if filters.mass_min is not None:
                base_query = base_query.filter(Item.mass >= filters.mass_min)
            
            if filters.mass_max is not None:
                base_query = base_query.filter(Item.mass <= filters.mass_max)
            
            if filters.is_waste is not None:
                base_query = base_query.filter(Item.is_waste == filters.is_waste)

        # Get results
        items = base_query.all()
        
        # Calculate relevance scores and sort
        scored_results = []
        current_time = datetime.now(timezone.utc)
        
        for item in items:
            # Base relevance score from text match
            relevance = self._calculate_text_relevance(item, query) if query else 1.0
            
            # Priority factor (0.1 to 1.0)
            priority_factor = item.priority / 10 if item.priority else 0.5
            
            # Expiry factor (items closer to expiry get higher priority)
            expiry_factor = 1.0
            if item.expiry_date:
                days_until_expiry = (item.expiry_date - current_time).days
                if days_until_expiry > 0:
                    expiry_factor = max(0.1, min(1.0, 10 / days_until_expiry))
                else:
                    expiry_factor = 1.0  # Already expired
            
            # Access frequency factor
            access_factor = self._calculate_access_frequency(item)
            
            # Combine factors with weights
            final_score = (
                relevance * 0.3 +
                priority_factor * 0.3 +
                expiry_factor * 0.2 +
                access_factor * 0.2
            )
            
            container = self.db.query(Container).filter(
                Container.id == item.container_id
            ).first() if item.container_id else None
            
            result = SearchResult(
                itemId=item.id,
                name=item.name,
                description=item.description,
                priority=item.priority,
                category=item.category,
                containerId=item.container_id,
                containerName=container.name if container else None,
                position=self._get_position_details(item),
                expiryDate=item.expiry_date.isoformat() if item.expiry_date else None,
                mass=item.mass,
                isWaste=item.is_waste,
                relevanceScore=final_score
            )
            
            scored_results.append((result, final_score))
        
        # Sort by final score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return only the results, without scores
        return [result for result, _ in scored_results]

    def _calculate_text_relevance(self, item: Item, query: str) -> float:
        """Calculate text match relevance score"""
        query = query.lower()
        relevance = 0.0
        
        # Exact name match
        if query == item.name.lower():
            relevance += 1.0
        # Partial name match
        elif query in item.name.lower():
            relevance += 0.6
        
        # Description match
        if item.description and query in item.description.lower():
            relevance += 0.3
        
        # Category match
        if item.category and query in item.category.lower():
            relevance += 0.2
        
        # Tag matches
        if item.tags:
            tag_matches = sum(1 for tag in item.tags if query in tag.lower())
            relevance += 0.1 * tag_matches
        
        return min(1.0, relevance)

    def _calculate_access_frequency(self, item: Item) -> float:
        """Calculate normalized access frequency score"""
        # This would typically use actual access logs
        # For now, return a default value
        return 0.5

    def _get_position_details(self, item: Item) -> Dict:
        """Get formatted position details for an item"""
        if not all([item.position_width, item.position_depth, item.position_height]):
            return None
            
        return {
            "startCoordinates": {
                "width": item.position_width,
                "depth": item.position_depth,
                "height": item.position_height
            },
            "endCoordinates": {
                "width": item.position_width + item.width,
                "depth": item.position_depth + item.depth,
                "height": item.position_height + item.height
            }
        }

    def get_item_details(self, item_id: str) -> Optional[ItemDetails]:
        """Get detailed information about a specific item"""
        item = self.db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return None
            
        container = self.db.query(Container).filter(
            Container.id == item.container_id
        ).first() if item.container_id else None
        
        return ItemDetails(
            itemId=item.id,
            name=item.name,
            description=item.description,
            priority=item.priority,
            category=item.category,
            containerId=item.container_id,
            containerName=container.name if container else None,
            position=self._get_position_details(item),
            expiryDate=item.expiry_date.isoformat() if item.expiry_date else None,
            mass=item.mass,
            volume=item.width * item.depth * item.height,
            dimensions={
                "width": item.width,
                "depth": item.depth,
                "height": item.height
            },
            isWaste=item.is_waste,
            tags=item.tags,
            remainingUses=item.remaining_uses,
            lastAccessed=item.last_accessed.isoformat() if item.last_accessed else None,
            accessCount=item.access_count or 0
        ) 