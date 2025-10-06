import { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Paper,
  Typography,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  Alert,
} from '@mui/material'
import { api, Container, Item, Position } from '../services/api'
import ContainerVisualization from '../components/ContainerVisualization'

interface ContainerWithItems {
  container: Container
  items: {
    item: Item
    position: Position
  }[]
}

export default function Visualization() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [containersWithItems, setContainersWithItems] = useState<ContainerWithItems[]>([])
  const [selectedContainerIndex, setSelectedContainerIndex] = useState(0)
  const [highlightedItemId, setHighlightedItemId] = useState<string | undefined>(undefined)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError(null)

    try {
      // Fetch the current arrangement
      const response = await fetch('/api/export/arrangement')
      const csvData = await response.text()

      // Parse CSV data
      const lines = csvData.split('\n')
      const headers = lines[0].split(',')
      const arrangements: { itemId: string; containerId: string; coordinates: string }[] = []

      for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim() === '') continue

        const values = lines[i].split(',')
        // Check if we have at least 3 values and the third one is the coordinates
        if (values.length >= 3) {
          // The coordinates might be split across multiple values if they contain commas
          // So we need to reconstruct the coordinates string
          const itemId = values[0]
          const containerId = values[1]
          const coordinates = values.slice(2).join(',')

          console.log('Parsed arrangement:', { itemId, containerId, coordinates })

          arrangements.push({
            itemId,
            containerId,
            coordinates,
          })
        }
      }

      // Fetch all containers
      const containersResponse = await fetch('/api/containers')
      const containersData = await containersResponse.json()
      const containers: Container[] = containersData.containers

      // Fetch all items
      const itemsResponse = await fetch('/api/items')
      const itemsData = await itemsResponse.json()
      const items: Item[] = itemsData.items

      // Group items by container
      const containerMap = new Map<string, ContainerWithItems>()

      containers.forEach(container => {
        containerMap.set(container.containerId, {
          container,
          items: [],
        })
      })

      arrangements.forEach(arrangement => {
        const item = items.find(i => i.itemId === arrangement.itemId)
        if (!item || !containerMap.has(arrangement.containerId)) return

        // Parse coordinates
        const coordsMatch = arrangement.coordinates.match(/\(([^)]+)\),\(([^)]+)\)/)
        if (!coordsMatch) return

        const startCoords = coordsMatch[1].split(',').map(Number)
        const endCoords = coordsMatch[2].split(',').map(Number)

        const position: Position = {
          startCoordinates: {
            width: startCoords[0],
            depth: startCoords[1],
            height: startCoords[2],
          },
          endCoordinates: {
            width: endCoords[0],
            depth: endCoords[1],
            height: endCoords[2],
          },
        }

        const containerWithItems = containerMap.get(arrangement.containerId)!
        containerWithItems.items.push({
          item,
          position,
        })
      })

      // Convert map to array
      const containersWithItemsArray = Array.from(containerMap.values())
      setContainersWithItems(containersWithItemsArray)

      if (containersWithItemsArray.length > 0) {
        setSelectedContainerIndex(0)
      }
    } catch (err) {
      console.error('Error fetching visualization data:', err)
      setError('Failed to load visualization data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleContainerChange = (index: number) => {
    setSelectedContainerIndex(index)
    setHighlightedItemId(undefined)
  }

  const handleItemClick = (itemId: string) => {
    setHighlightedItemId(itemId === highlightedItemId ? undefined : itemId)
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ mt: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    )
  }

  if (containersWithItems.length === 0) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          3D Visualization
        </Typography>
        <Alert severity="info">
          No containers or items found. Please import containers and items first.
        </Alert>
      </Box>
    )
  }

  const selectedContainer = containersWithItems.length > 0 ? containersWithItems[selectedContainerIndex] : null

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        3D Visualization
      </Typography>

      {containersWithItems.length === 0 ? (
        <Alert severity="info" sx={{ mb: 2 }}>
          No items have been placed in containers yet. Use the Placement page to place items in containers.
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {/* Container Selection */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Containers with Items
                </Typography>
                <List>
                  {containersWithItems.map((containerWithItems, index) => (
                    <ListItem key={index} disablePadding>
                      <ListItemButton
                        selected={index === selectedContainerIndex}
                        onClick={() => handleContainerChange(index)}
                      >
                        <ListItemText
                          primary={`${containerWithItems.container.containerId} (${containerWithItems.container.zone})`}
                          secondary={`${containerWithItems.items.length} items`}
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* 3D Visualization */}
          <Grid item xs={12} md={9}>
            <ContainerVisualization
              container={selectedContainer.container}
              items={selectedContainer.items}
              highlightedItemId={highlightedItemId}
            />

            {/* Items in Container */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Items in Container ({selectedContainer.items.length})
                </Typography>
                {selectedContainer.items.length === 0 ? (
                  <Typography>No items in this container.</Typography>
                ) : (
                  <Grid container spacing={1}>
                    {selectedContainer.items.map((itemData, index) => (
                      <Grid item xs={12} sm={6} md={4} key={index}>
                        <Paper
                          sx={{
                            p: 1,
                            cursor: 'pointer',
                            bgcolor: itemData.item.itemId === highlightedItemId ? 'primary.dark' : 'background.paper',
                          }}
                          onClick={() => handleItemClick(itemData.item.itemId)}
                        >
                          <Typography variant="subtitle2">{itemData.item.name}</Typography>
                          <Typography variant="body2">ID: {itemData.item.itemId}</Typography>
                          <Typography variant="body2">
                            Priority: {itemData.item.priority} | Zone: {itemData.item.preferredZone}
                          </Typography>
                          <Typography variant="body2">
                            Position: ({itemData.position.startCoordinates.width}, {itemData.position.startCoordinates.depth}, {itemData.position.startCoordinates.height})
                          </Typography>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  )
}
