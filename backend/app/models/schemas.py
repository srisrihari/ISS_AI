from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Coordinate models
class Coordinates(BaseModel):
    width: float
    depth: float
    height: float

class Position(BaseModel):
    startCoordinates: Coordinates
    endCoordinates: Coordinates

class Dimensions(BaseModel):
    width: float
    depth: float
    height: float

class Container(BaseModel):
    containerId: str
    name: str
    dimensions: Dimensions
    zone: Optional[str] = None

# Item models
class ItemBase(BaseModel):
    itemId: str
    name: str
    width: float
    depth: float
    height: float
    priority: int = Field(..., ge=0, le=100)
    expiryDate: Optional[str] = None  # ISO format
    usageLimit: int
    preferredZone: str

class ItemCreate(ItemBase):
    mass: float

class ItemDB(ItemBase):
    mass: float
    remainingUses: int
    isWaste: bool = False
    containerId: Optional[str] = None
    position: Optional[Position] = None

    class Config:
        from_attributes = True

# Container models
class ContainerBase(BaseModel):
    containerId: str
    zone: str
    width: float
    depth: float
    height: float

class ContainerCreate(ContainerBase):
    pass

class ContainerDB(ContainerBase):
    class Config:
        from_attributes = True

# Placement models
class PlacementRequest(BaseModel):
    items: List[ItemBase]
    containers: List[ContainerBase]

class PlacementItem(BaseModel):
    itemId: str
    containerId: str
    position: Position

class RearrangementStep(BaseModel):
    step: int
    action: str  # "move", "remove", "place"
    itemId: str
    fromContainer: str
    fromPosition: Position
    toContainer: str
    toPosition: Position

class PlacementResponse(BaseModel):
    success: bool
    placements: List[PlacementItem]
    rearrangements: List[RearrangementStep]

# Search and Retrieval models
class SearchItem(BaseModel):
    itemId: str
    name: str
    containerId: str
    zone: str
    position: Position

class RetrievalStep(BaseModel):
    step: int
    action: str  # "remove", "setAside", "retrieve", "placeBack"
    itemId: str
    itemName: str

class SearchResponse(BaseModel):
    success: bool
    found: bool
    item: Optional[SearchItem] = None
    retrievalSteps: List[RetrievalStep]

class RetrieveRequest(BaseModel):
    itemId: str
    userId: str
    timestamp: str  # ISO format

class RetrieveResponse(BaseModel):
    success: bool

class PlaceRequest(BaseModel):
    itemId: str
    userId: str
    timestamp: str  # ISO format
    containerId: str
    position: Position

class PlaceResponse(BaseModel):
    success: bool

# Waste Management models
class WasteItem(BaseModel):
    itemId: str
    name: str
    reason: str  # "Expired", "Out of Uses"
    containerId: str
    position: Position

class WasteIdentifyResponse(BaseModel):
    success: bool
    wasteItems: List[WasteItem]

class ReturnPlanRequest(BaseModel):
    undockingContainerId: str
    undockingDate: str  # ISO format
    maxWeight: float

class ReturnPlanStep(BaseModel):
    step: int
    itemId: str
    itemName: str
    fromContainer: str
    toContainer: str

class ReturnManifestItem(BaseModel):
    itemId: str
    name: str
    reason: str

class ReturnManifest(BaseModel):
    undockingContainerId: str
    undockingDate: str
    returnItems: List[ReturnManifestItem]
    totalVolume: float
    totalWeight: float

class ReturnPlanResponse(BaseModel):
    success: bool
    returnPlan: List[ReturnPlanStep]
    retrievalSteps: List[RetrievalStep]
    returnManifest: ReturnManifest

class UndockingRequest(BaseModel):
    undockingContainerId: str
    timestamp: str  # ISO format

class UndockingResponse(BaseModel):
    success: bool
    itemsRemoved: int

# Time Simulation models
class SimulationItem(BaseModel):
    itemId: str
    name: Optional[str] = None

class SimulationRequest(BaseModel):
    numOfDays: Optional[int] = None
    toTimestamp: Optional[str] = None  # ISO format
    itemsToBeUsedPerDay: List[SimulationItem]

class SimulationItemStatus(BaseModel):
    itemId: str
    name: str
    remainingUses: Optional[int] = None

class SimulationChanges(BaseModel):
    itemsUsed: List[SimulationItemStatus]
    itemsExpired: List[SimulationItemStatus]
    itemsDepletedToday: List[SimulationItemStatus]

class SimulationResponse(BaseModel):
    success: bool
    newDate: str  # ISO format
    changes: SimulationChanges

# Import/Export models
class ImportError(BaseModel):
    row: int
    message: str

class ImportResponse(BaseModel):
    success: bool
    itemsImported: Optional[int] = None
    containersImported: Optional[int] = None
    errors: List[ImportError]
    placements: Optional[List[PlacementItem]] = []

# Logging models
class LogEntry(BaseModel):
    timestamp: str
    userId: str
    actionType: str
    itemId: str
    details: Dict[str, Any]

class LogResponse(BaseModel):
    logs: List[LogEntry]

# Move OptimizationRequest after Container definition
class OptimizationRequest(BaseModel):
    container: Container
    items: List[PlacementItem]

class OptimizationResponse(BaseModel):
    rearrangementSteps: List[RearrangementStep]
    spaceUtilization: float
    accessibilityScore: float
    stabilityScore: float
    priorityDistribution: float
    movementCount: int
    totalDistance: float

class SearchFilter(BaseModel):
    priority: Optional[int] = None
    category: Optional[str] = None
    container_id: Optional[str] = None
    expiry_before: Optional[datetime] = None
    expiry_after: Optional[datetime] = None
    mass_min: Optional[float] = None
    mass_max: Optional[float] = None
    is_waste: Optional[bool] = None
