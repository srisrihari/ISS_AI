import { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Checkbox,
} from '@mui/material'
import { api } from '../services/api'
import { useNavigate } from 'react-router-dom'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`inventory-tabpanel-${index}`}
      aria-labelledby={`inventory-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

export default function Inventory() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [items, setItems] = useState<any[]>([])
  const [containers, setContainers] = useState<any[]>([])
  const [tabValue, setTabValue] = useState(0)

  // Placement dialog state
  const [placementDialogOpen, setPlacementDialogOpen] = useState(false)
  const [selectedItemId, setSelectedItemId] = useState('')
  const [selectedContainerId, setSelectedContainerId] = useState('')

  const [selectedItems, setSelectedItems] = useState<string[]>([])

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError(null)

    try {
      // Fetch items
      const itemsResponse = await fetch('/api/items')
      const itemsData = await itemsResponse.json()
      setItems(itemsData.items || [])

      // Fetch containers
      const containersResponse = await fetch('/api/containers')
      const containersData = await containersResponse.json()
      setContainers(containersData.containers || [])
    } catch (err) {
      console.error('Error fetching inventory data:', err)
      setError('Failed to load inventory data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const handleOpenPlacementDialog = (itemId: string) => {
    setSelectedItemId(itemId)
    setSelectedContainerId(containers.length > 0 ? containers[0].containerId : '')
    setPlacementDialogOpen(true)
  }

  const handleClosePlacementDialog = () => {
    setPlacementDialogOpen(false)
  }

  const handlePlaceItem = async () => {
    if (!selectedItemId || !selectedContainerId) {
      return
    }

    try {
      // Navigate to the placement page with the selected item and container
      navigate(`/placement?itemId=${selectedItemId}&containerId=${selectedContainerId}`)
    } catch (err) {
      console.error('Error placing item:', err)
      setError('Failed to place item. Please try again.')
    } finally {
      setPlacementDialogOpen(false)
    }
  }

  const handleRemoveItem = async (itemId: string) => {
    if (!confirm(`Are you sure you want to remove this item from its container?`)) {
      return
    }

    try {
      const response = await fetch(`/api/items/${itemId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        // Refresh the data
        fetchData()
      } else {
        const errorData = await response.json()
        setError(`Failed to remove item: ${errorData.detail || 'Unknown error'}`)
      }
    } catch (err) {
      console.error('Error removing item:', err)
      setError('Failed to remove item. Please try again.')
    }
  }

  const handleDeleteItem = async (itemId: string) => {
    if (!confirm(`Are you sure you want to DELETE this item from the database? This action cannot be undone.`)) {
      return
    }

    try {
      const response = await fetch(`/api/items/${itemId}/delete`, {
        method: 'DELETE',
      })

      if (response.ok) {
        // Refresh the data
        fetchData()
      } else {
        const errorData = await response.json()
        setError(`Failed to delete item: ${errorData.detail || 'Unknown error'}`)
      }
    } catch (err) {
      console.error('Error deleting item:', err)
      setError('Failed to delete item. Please try again.')
    }
  }

  const handleSelectItem = (itemId: string) => {
    setSelectedItems((prevSelected) =>
      prevSelected.includes(itemId)
        ? prevSelected.filter((id) => id !== itemId)
        : [...prevSelected, itemId]
    )
  }

  const handleSelectAllItems = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedItems(items.map((item) => item.itemId))
    } else {
      setSelectedItems([])
    }
  }

  const handleBulkDelete = async () => {
    if (!confirm(`Are you sure you want to DELETE selected items? This action cannot be undone.`)) {
      return
    }

    try {
      await Promise.all(
        selectedItems.map((itemId) =>
          fetch(`/api/items/${itemId}/delete`, {
            method: 'DELETE',
          })
        )
      )
      fetchData()
      setSelectedItems([])
    } catch (err) {
      console.error('Error deleting items:', err)
      setError('Failed to delete items. Please try again.')
    }
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
        <Button
          variant="contained"
          sx={{ mt: 2 }}
          onClick={fetchData}
        >
          Retry
        </Button>
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Inventory Management
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="inventory tabs">
          <Tab label="Items" id="inventory-tab-0" aria-controls="inventory-tabpanel-0" />
          <Tab label="Containers" id="inventory-tab-1" aria-controls="inventory-tabpanel-1" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              All Items ({items.length})
            </Typography>
            {items.length === 0 ? (
              <Typography>No items found. Import items or add them manually.</Typography>
            ) : (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell padding="checkbox">
                        <Checkbox
                          indeterminate={selectedItems.length > 0 && selectedItems.length < items.length}
                          checked={items.length > 0 && selectedItems.length === items.length}
                          onChange={handleSelectAllItems}
                        />
                      </TableCell>
                      <TableCell>ID</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Dimensions (W×D×H cm)</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Preferred Zone</TableCell>
                      <TableCell>Container</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {items.map((item) => (
                      <TableRow key={item.itemId} selected={selectedItems.includes(item.itemId)}>
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={selectedItems.includes(item.itemId)}
                            onChange={() => handleSelectItem(item.itemId)}
                          />
                        </TableCell>
                        <TableCell>{item.itemId}</TableCell>
                        <TableCell>{item.name}</TableCell>
                        <TableCell>{`${item.width}×${item.depth}×${item.height}`}</TableCell>
                        <TableCell>{item.priority}</TableCell>
                        <TableCell>{item.preferredZone}</TableCell>
                        <TableCell>{item.containerId || 'Not placed'}</TableCell>
                        <TableCell>
                          {item.isWaste ? (
                            <Typography color="error">Waste</Typography>
                          ) : (
                            <Typography color="success.main">Active</Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          {!item.containerId && !item.isWaste && (
                            <Button
                              variant="contained"
                              size="small"
                              onClick={() => handleOpenPlacementDialog(item.itemId)}
                            >
                              Place
                            </Button>
                          )}
                          {item.containerId && (
                            <Button
                              variant="outlined"
                              color="error"
                              size="small"
                              onClick={() => handleRemoveItem(item.itemId)}
                              sx={{ ml: 1 }}
                            >
                              Remove
                            </Button>
                          )}
                          <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            onClick={() => handleDeleteItem(item.itemId)}
                            sx={{ ml: 1 }}
                          >
                            Delete
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
            <Button
              variant="contained"
              color="error"
              onClick={handleBulkDelete}
              disabled={selectedItems.length === 0}
              sx={{ mt: 2 }}
            >
              Delete Selected
            </Button>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              All Containers ({containers.length})
            </Typography>
            {containers.length === 0 ? (
              <Typography>No containers found. Import containers or add them manually.</Typography>
            ) : (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Zone</TableCell>
                      <TableCell>Dimensions (W×D×H cm)</TableCell>
                      <TableCell>Volume (cm³)</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {containers.map((container) => (
                      <TableRow key={container.containerId}>
                        <TableCell>{container.containerId}</TableCell>
                        <TableCell>{container.zone}</TableCell>
                        <TableCell>{`${container.width}×${container.depth}×${container.height}`}</TableCell>
                        <TableCell>{container.width * container.depth * container.height}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Placement Dialog */}
      <Dialog open={placementDialogOpen} onClose={handleClosePlacementDialog}>
        <DialogTitle>Place Item in Container</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel id="container-select-label">Container</InputLabel>
            <Select
              labelId="container-select-label"
              value={selectedContainerId}
              label="Container"
              onChange={(e) => setSelectedContainerId(e.target.value)}
            >
              {containers.map((container) => (
                <MenuItem key={container.containerId} value={container.containerId}>
                  {container.containerId} ({container.zone})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePlacementDialog}>Cancel</Button>
          <Button onClick={handlePlaceItem} variant="contained">
            Continue to Placement
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
