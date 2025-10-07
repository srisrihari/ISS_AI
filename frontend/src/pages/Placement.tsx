import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
const API_BASE = (import.meta as any).env?.VITE_API_BASE || ''
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Grid,
  Paper,
  TextField,
  Typography,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  Alert,
} from '@mui/material'
import { api, Item, Container, PlacementItem, RearrangementStep } from '../services/api'

export default function Placement() {
  const location = useLocation()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [items, setItems] = useState<Item[]>([])
  const [containers, setContainers] = useState<Container[]>([])
  const [placements, setPlacements] = useState<PlacementItem[]>([])
  const [rearrangements, setRearrangements] = useState<RearrangementStep[]>([])
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<boolean>(false)
  const [preselectedItemId, setPreselectedItemId] = useState<string | null>(null)
  const [preselectedContainerId, setPreselectedContainerId] = useState<string | null>(null)

  // Parse query parameters
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search)
    const itemId = searchParams.get('itemId')
    const containerId = searchParams.get('containerId')

    if (itemId) {
      setPreselectedItemId(itemId)
      // Fetch the item details
      fetchItemDetails(itemId)
    }

    if (containerId) {
      setPreselectedContainerId(containerId)
      // Fetch the container details
      fetchContainerDetails(containerId)
    }
  }, [location.search])

  const fetchItemDetails = async (itemId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/search?itemId=${itemId}`)
      const data = await response.json()

      if (data.found) {
        // Get the item details from the response
        const itemData = data.item;

        // Create an item object with the correct dimensions
        const item: Item = {
          itemId: itemData.itemId,
          name: itemData.name,
          width: itemData.width || 10, // Use the width from the response or default to 10
          depth: itemData.depth || 10, // Use the depth from the response or default to 10
          height: itemData.height || 10, // Use the height from the response or default to 10
          priority: itemData.priority || 80, // Use the priority from the response or default to 80
          preferredZone: itemData.preferredZone || '',
          usageLimit: itemData.usageLimit || 10, // Use the usage limit from the response or default to 10
        }

        console.log('Fetched item details:', item);

        // Update the form state with the item details
        setNewItem(item)

        // Add the item to the list if it's not already there
        if (!items.some(i => i.itemId === item.itemId)) {
          setItems(prevItems => [...prevItems, item])
        }
      }
    } catch (err) {
      console.error('Error fetching item details:', err)
    }
  }

  const fetchContainerDetails = async (containerId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/containers`)
      const data = await response.json()

      const container = data.containers.find((c: any) => c.containerId === containerId)

      if (container) {
        const containerObj: Container = {
          containerId: container.containerId,
          zone: container.zone,
          width: container.width,
          depth: container.depth,
          height: container.height,
        }

        console.log('Fetched container details:', containerObj);

        // Update the form state with the container details
        setNewContainer(containerObj)

        // Add the container to the list if it's not already there
        if (!containers.some(c => c.containerId === containerObj.containerId)) {
          setContainers(prevContainers => [...prevContainers, containerObj])
        }
      }
    } catch (err) {
      console.error('Error fetching container details:', err)
    }
  }

  // Form state for adding items
  const [newItem, setNewItem] = useState<Item>({
    itemId: '',
    name: '',
    width: 0,
    depth: 0,
    height: 0,
    priority: 50,
    usageLimit: 1,
    preferredZone: '',
    mass: 0,
  })

  // Form state for adding containers
  const [newContainer, setNewContainer] = useState<Container>({
    containerId: '',
    zone: '',
    width: 0,
    depth: 0,
    height: 0,
  })

  const zones = ['Crew Quarters', 'Airlock', 'Laboratory', 'Medical Bay']

  const handleAddItem = () => {
    if (!newItem.itemId || !newItem.name || newItem.width <= 0 || newItem.depth <= 0 || newItem.height <= 0) {
      setError('Please fill in all required item fields with valid values')
      return
    }

    setItems([...items, { ...newItem }])
    setNewItem({
      itemId: '',
      name: '',
      width: 0,
      depth: 0,
      height: 0,
      priority: 50,
      usageLimit: 1,
      preferredZone: '',
    })
    setError(null)
  }

  const handleAddContainer = () => {
    if (!newContainer.containerId || !newContainer.zone || newContainer.width <= 0 || newContainer.depth <= 0 || newContainer.height <= 0) {
      setError('Please fill in all required container fields with valid values')
      return
    }

    setContainers([...containers, { ...newContainer }])
    setNewContainer({
      containerId: '',
      zone: '',
      width: 0,
      depth: 0,
      height: 0,
    })
    setError(null)
  }

  const handleRemoveItem = (index: number) => {
    const updatedItems = [...items]
    updatedItems.splice(index, 1)
    setItems(updatedItems)
  }

  const handleRemoveContainer = (index: number) => {
    const updatedContainers = [...containers]
    updatedContainers.splice(index, 1)
    setContainers(updatedContainers)
  }

  const handleSubmit = async () => {
    if (items.length === 0) {
      setError('Please add at least one item')
      return
    }

    if (containers.length === 0) {
      setError('Please add at least one container')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await api.placement(items, containers)
      setPlacements(response.placements)
      setRearrangements(response.rearrangements)
      setSuccess(true)

      // Show a success message
      alert('Placement successful! Items have been placed in containers.')

      // If we came from the inventory page with a specific item, navigate back to inventory
      if (preselectedItemId) {
        // Wait a moment to ensure the database is updated
        setTimeout(() => {
          navigate('/inventory')
        }, 1500)
      }
    } catch (err) {
      console.error('Error submitting placement request:', err)
      setError('Failed to process placement request. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setItems([])
    setContainers([])
    setPlacements([])
    setRearrangements([])
    setError(null)
    setSuccess(false)
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Placement Recommendations
      </Typography>

      {error && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.dark' }}>
          <Typography color="error.contrastText">{error}</Typography>
        </Paper>
      )}

      {!success ? (
        <Grid container spacing={3}>
          {/* Add Items */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Add Items
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Item ID"
                      fullWidth
                      value={newItem.itemId}
                      onChange={(e) => setNewItem({ ...newItem, itemId: e.target.value })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Name"
                      fullWidth
                      value={newItem.name}
                      onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Width (cm)"
                      type="number"
                      fullWidth
                      value={newItem.width || ''}
                      onChange={(e) => setNewItem({ ...newItem, width: parseFloat(e.target.value) })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Depth (cm)"
                      type="number"
                      fullWidth
                      value={newItem.depth || ''}
                      onChange={(e) => setNewItem({ ...newItem, depth: parseFloat(e.target.value) })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Height (cm)"
                      type="number"
                      fullWidth
                      value={newItem.height || ''}
                      onChange={(e) => setNewItem({ ...newItem, height: parseFloat(e.target.value) })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Priority (1-100)"
                      type="number"
                      fullWidth
                      value={newItem.priority || ''}
                      onChange={(e) => setNewItem({ ...newItem, priority: parseInt(e.target.value) })}
                      margin="normal"
                      inputProps={{ min: 1, max: 100 }}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Usage Limit"
                      type="number"
                      fullWidth
                      value={newItem.usageLimit || ''}
                      onChange={(e) => setNewItem({ ...newItem, usageLimit: parseInt(e.target.value) })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Expiry Date"
                      type="date"
                      fullWidth
                      value={newItem.expiryDate?.split('T')[0] || ''}
                      onChange={(e) => setNewItem({ ...newItem, expiryDate: e.target.value })}
                      margin="normal"
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      select
                      label="Preferred Zone"
                      fullWidth
                      value={newItem.preferredZone}
                      onChange={(e) => setNewItem({ ...newItem, preferredZone: e.target.value })}
                      margin="normal"
                      required
                    >
                      {zones.map((zone) => (
                        <MenuItem key={zone} value={zone}>
                          {zone}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  <Grid item xs={12}>
                    <Button variant="contained" onClick={handleAddItem} fullWidth>
                      Add Item
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Item List */}
            {items.length > 0 && (
              <Card sx={{ mt: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Items ({items.length})
                  </Typography>
                  {items.map((item, index) => (
                    <Paper key={index} sx={{ p: 2, mb: 1 }}>
                      <Grid container spacing={1}>
                        <Grid item xs={8}>
                          <Typography variant="subtitle1">
                            {item.name} (ID: {item.itemId})
                          </Typography>
                          <Typography variant="body2">
                            Dimensions: {item.width}x{item.depth}x{item.height} cm
                          </Typography>
                          <Typography variant="body2">
                            Priority: {item.priority} | Zone: {item.preferredZone}
                          </Typography>
                        </Grid>
                        <Grid item xs={4} sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                          <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            onClick={() => handleRemoveItem(index)}
                          >
                            Remove
                          </Button>
                        </Grid>
                      </Grid>
                    </Paper>
                  ))}
                </CardContent>
              </Card>
            )}
          </Grid>

          {/* Add Containers */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Add Containers
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Container ID"
                      fullWidth
                      value={newContainer.containerId}
                      onChange={(e) => setNewContainer({ ...newContainer, containerId: e.target.value })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      select
                      label="Zone"
                      fullWidth
                      value={newContainer.zone}
                      onChange={(e) => setNewContainer({ ...newContainer, zone: e.target.value })}
                      margin="normal"
                      required
                    >
                      {zones.map((zone) => (
                        <MenuItem key={zone} value={zone}>
                          {zone}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Width (cm)"
                      type="number"
                      fullWidth
                      value={newContainer.width || ''}
                      onChange={(e) => setNewContainer({ ...newContainer, width: parseFloat(e.target.value) })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Depth (cm)"
                      type="number"
                      fullWidth
                      value={newContainer.depth || ''}
                      onChange={(e) => setNewContainer({ ...newContainer, depth: parseFloat(e.target.value) })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Height (cm)"
                      type="number"
                      fullWidth
                      value={newContainer.height || ''}
                      onChange={(e) => setNewContainer({ ...newContainer, height: parseFloat(e.target.value) })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button variant="contained" onClick={handleAddContainer} fullWidth>
                      Add Container
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Container List */}
            {containers.length > 0 && (
              <Card sx={{ mt: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Containers ({containers.length})
                  </Typography>
                  {containers.map((container, index) => (
                    <Paper key={index} sx={{ p: 2, mb: 1 }}>
                      <Grid container spacing={1}>
                        <Grid item xs={8}>
                          <Typography variant="subtitle1">
                            {container.containerId} ({container.zone})
                          </Typography>
                          <Typography variant="body2">
                            Dimensions: {container.width}x{container.depth}x{container.height} cm
                          </Typography>
                        </Grid>
                        <Grid item xs={4} sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                          <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            onClick={() => handleRemoveContainer(index)}
                          >
                            Remove
                          </Button>
                        </Grid>
                      </Grid>
                    </Paper>
                  ))}
                </CardContent>
              </Card>
            )}
          </Grid>

          {/* Submit Button */}
          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleSubmit}
              disabled={loading || items.length === 0 || containers.length === 0}
              fullWidth
            >
              {loading ? <CircularProgress size={24} /> : 'Generate Placement Recommendations'}
            </Button>
          </Grid>
        </Grid>
      ) : (
        <Box>
          <Paper sx={{ p: 3, mb: 3, bgcolor: 'success.dark' }}>
            <Typography variant="h6" color="success.contrastText">
              Placement Recommendations Generated Successfully!
            </Typography>
          </Paper>

          <Grid container spacing={3}>
            {/* Placements */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Placements ({placements.length})
                  </Typography>
                  {placements.map((placement, index) => (
                    <Paper key={index} sx={{ p: 2, mb: 1 }}>
                      <Typography variant="subtitle1">
                        Item: {items.find(i => i.itemId === placement.itemId)?.name || placement.itemId}
                      </Typography>
                      <Typography variant="body2">
                        Container: {placement.containerId}
                      </Typography>
                      <Typography variant="body2">
                        Position: ({placement.position.startCoordinates.width}, {placement.position.startCoordinates.depth}, {placement.position.startCoordinates.height}) to ({placement.position.endCoordinates.width}, {placement.position.endCoordinates.depth}, {placement.position.endCoordinates.height})
                      </Typography>
                    </Paper>
                  ))}
                </CardContent>
              </Card>
            </Grid>

            {/* Rearrangements */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Rearrangements ({rearrangements.length})
                  </Typography>
                  {rearrangements.length === 0 ? (
                    <Typography>No rearrangements needed.</Typography>
                  ) : (
                    <Stepper orientation="vertical">
                      {rearrangements.map((step, index) => (
                        <Step key={index} active={true}>
                          <StepLabel>Step {step.step}: {step.action}</StepLabel>
                          <Box sx={{ ml: 3, mt: 1, mb: 2 }}>
                            <Typography variant="body1">
                              Item: {items.find(i => i.itemId === step.itemId)?.name || step.itemId}
                            </Typography>
                            {step.action === 'remove' && (
                              <Typography variant="body2">
                                Remove from container {step.fromContainer}
                              </Typography>
                            )}
                            {step.action === 'place' && (
                              <Typography variant="body2">
                                Place in container {step.toContainer}
                              </Typography>
                            )}
                            {step.action === 'move' && (
                              <Typography variant="body2">
                                Move from container {step.fromContainer} to {step.toContainer}
                              </Typography>
                            )}
                          </Box>
                        </Step>
                      ))}
                    </Stepper>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Reset Button */}
            <Grid item xs={12}>
              <Button variant="outlined" onClick={handleReset} fullWidth>
                Start New Placement
              </Button>
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  )
}
