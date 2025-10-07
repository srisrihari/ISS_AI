import axios from 'axios'

const rawBase = (import.meta as any).env?.VITE_API_BASE || ''
const base = rawBase.endsWith('/') ? rawBase.slice(0, -1) : rawBase
const API_URL = `${base}/api`

// Types
export interface Coordinates {
  width: number
  depth: number
  height: number
}

export interface Position {
  startCoordinates: Coordinates
  endCoordinates: Coordinates
}

export interface Item {
  itemId: string
  name: string
  width: number
  depth: number
  height: number
  priority: number
  expiryDate?: string
  usageLimit: number
  preferredZone: string
  mass?: number
  remainingUses?: number
  isWaste?: boolean
}

export interface Container {
  containerId: string
  zone: string
  width: number
  depth: number
  height: number
}

export interface PlacementItem {
  itemId: string
  containerId: string
  position: Position
}

export interface RearrangementStep {
  step: number
  action: string
  itemId: string
  fromContainer: string
  fromPosition: Position
  toContainer: string
  toPosition: Position
}

export interface PlacementResponse {
  success: boolean
  placements: PlacementItem[]
  rearrangements: RearrangementStep[]
}

export interface SearchItem {
  itemId: string
  name: string
  containerId: string
  zone: string
  position: Position
}

export interface RetrievalStep {
  step: number
  action: string
  itemId: string
  itemName: string
}

export interface SearchResponse {
  success: boolean
  found: boolean
  item?: SearchItem
  retrievalSteps: RetrievalStep[]
}

export interface WasteItem {
  itemId: string
  name: string
  reason: string
  containerId: string
  position: Position
}

export interface WasteIdentifyResponse {
  success: boolean
  wasteItems: WasteItem[]
}

export interface ReturnPlanStep {
  step: number
  itemId: string
  itemName: string
  fromContainer: string
  toContainer: string
}

export interface ReturnManifestItem {
  itemId: string
  name: string
  reason: string
}

export interface ReturnManifest {
  undockingContainerId: string
  undockingDate: string
  returnItems: ReturnManifestItem[]
  totalVolume: number
  totalWeight: number
}

export interface ReturnPlanResponse {
  success: boolean
  returnPlan: ReturnPlanStep[]
  retrievalSteps: RetrievalStep[]
  returnManifest: ReturnManifest
}

export interface SimulationItemStatus {
  itemId: string
  name: string
  remainingUses?: number
}

export interface SimulationChanges {
  itemsUsed: SimulationItemStatus[]
  itemsExpired: SimulationItemStatus[]
  itemsDepletedToday: SimulationItemStatus[]
}

export interface SimulationResponse {
  success: boolean
  newDate: string
  changes: SimulationChanges
}

export interface LogEntry {
  timestamp: string
  userId: string
  actionType: string
  itemId: string
  details: {
    fromContainer?: string
    toContainer?: string
    reason?: string
    [key: string]: any
  }
}

export interface LogResponse {
  logs: LogEntry[]
}

// API functions
export const api = {
  // Placement
  placement: async (items: Item[], containers: Container[]): Promise<PlacementResponse> => {
    const response = await axios.post(`${API_URL}/placement`, { items, containers })
    return response.data
  },

  // Search and Retrieval
  search: async (itemId?: string, itemName?: string, userId?: string): Promise<SearchResponse> => {
    const params = new URLSearchParams()
    if (itemId) params.append('itemId', itemId)
    if (itemName) params.append('itemName', itemName)
    if (userId) params.append('userId', userId)

    const response = await axios.get(`${API_URL}/search?${params.toString()}`)
    return response.data
  },

  retrieve: async (itemId: string, userId: string): Promise<{ success: boolean }> => {
    const response = await axios.post(`${API_URL}/retrieve`, {
      itemId,
      userId,
      timestamp: new Date().toISOString(),
    })
    return response.data
  },

  place: async (
    itemId: string,
    userId: string,
    containerId: string,
    position: Position
  ): Promise<{ success: boolean }> => {
    const response = await axios.post(`${API_URL}/place`, {
      itemId,
      userId,
      timestamp: new Date().toISOString(),
      containerId,
      position,
    })
    return response.data
  },

  // Waste Management
  identifyWaste: async (): Promise<WasteIdentifyResponse> => {
    const response = await axios.get(`${API_URL}/waste/identify`)
    return response.data
  },

  createReturnPlan: async (
    undockingContainerId: string,
    maxWeight: number
  ): Promise<ReturnPlanResponse> => {
    const response = await axios.post(`${API_URL}/waste/return-plan`, {
      undockingContainerId,
      undockingDate: new Date().toISOString(),
      maxWeight,
    })
    return response.data
  },

  completeUndocking: async (
    undockingContainerId: string
  ): Promise<{ success: boolean; itemsRemoved: number }> => {
    const response = await axios.post(`${API_URL}/waste/complete-undocking`, {
      undockingContainerId,
      timestamp: new Date().toISOString(),
    })
    return response.data
  },

  // Time Simulation
  simulateDay: async (
    numOfDays: number,
    itemsToBeUsedPerDay: { itemId: string; name?: string }[]
  ): Promise<SimulationResponse> => {
    const response = await axios.post(`${API_URL}/simulate/day`, {
      numOfDays,
      itemsToBeUsedPerDay,
    })
    return response.data
  },

  // Import/Export
  importItems: async (file: File, autoPlace: boolean = true): Promise<{ success: boolean; itemsImported: number; errors: any[]; placements?: PlacementItem[] }> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('auto_place', autoPlace ? 'true' : 'false')

    const response = await axios.post(`${API_URL}/import/items`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  importContainers: async (
    file: File
  ): Promise<{ success: boolean; containersImported: number; errors: any[] }> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(`${API_URL}/import/containers`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  exportArrangement: async (): Promise<string> => {
    const response = await axios.get(`${API_URL}/export/arrangement`, {
      responseType: 'blob',
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'arrangement.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()

    return 'Downloaded arrangement.csv'
  },

  // Logs
  getLogs: async (
    startDate: string,
    endDate: string,
    itemId?: string,
    userId?: string,
    actionType?: string
  ): Promise<LogResponse> => {
    const params = new URLSearchParams()
    params.append('startDate', startDate)
    params.append('endDate', endDate)
    if (itemId) params.append('itemId', itemId)
    if (userId) params.append('userId', userId)
    if (actionType) params.append('actionType', actionType)

    const response = await axios.get(`${API_URL}/logs?${params.toString()}`)
    return response.data
  },
}
