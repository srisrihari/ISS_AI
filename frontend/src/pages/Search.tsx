import { useState } from 'react'
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
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
} from '@mui/material'
import { api, SearchItem, RetrievalStep } from '../services/api'

export default function Search() {
  const [loading, setLoading] = useState(false)
  const [searchType, setSearchType] = useState<'id' | 'name'>('id')
  const [itemId, setItemId] = useState('')
  const [itemName, setItemName] = useState('')
  const [userId, setUserId] = useState('admin') // Default to 'admin' for simplicity
  const [found, setFound] = useState(false)
  const [item, setItem] = useState<SearchItem | null>(null)
  const [retrievalSteps, setRetrievalSteps] = useState<RetrievalStep[]>([])
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<boolean>(false)
  const [retrieveSuccess, setRetrieveSuccess] = useState<boolean>(false)

  const handleSearch = async () => {
    if (searchType === 'id' && !itemId) {
      setError('Please enter an Item ID')
      return
    }

    if (searchType === 'name' && !itemName) {
      setError('Please enter an Item Name')
      return
    }

    setLoading(true)
    setError(null)
    setFound(false)
    setItem(null)
    setRetrievalSteps([])
    setSuccess(false)
    setRetrieveSuccess(false)

    try {
      const response = await api.search(
        searchType === 'id' ? itemId : undefined,
        searchType === 'name' ? itemName : undefined,
        userId || undefined
      )

      setFound(response.found)

      if (response.found && response.item) {
        setItem(response.item)
        setRetrievalSteps(response.retrievalSteps)
        setSuccess(true)
      } else {
        setError('Item not found')
      }
    } catch (err) {
      console.error('Error searching for item:', err)
      setError('Failed to search for item. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleRetrieve = async () => {
    if (!item) {
      setError('No item to retrieve')
      return
    }

    if (!userId) {
      setError('Please enter a User ID to track who is retrieving the item')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await api.retrieve(item.itemId, userId)

      if (response.success) {
        setRetrieveSuccess(true)
        // Clear the item and retrieval steps since the item has been retrieved
        setItem(null)
        setRetrievalSteps([])
        setSuccess(false)
      } else {
        setError('Failed to retrieve item')
      }
    } catch (err) {
      console.error('Error retrieving item:', err)
      setError('Failed to retrieve item. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setItemId('')
    setItemName('')
    setFound(false)
    setItem(null)
    setRetrievalSteps([])
    setError(null)
    setSuccess(false)
    setRetrieveSuccess(false)
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Search & Retrieval
      </Typography>

      <Alert severity="info" sx={{ mb: 2 }}>
        Search for an item by ID or name, then follow the retrieval steps to locate and retrieve the item.
        After retrieving an item, it will be removed from its container and marked as retrieved.
      </Alert>

      {error && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.dark' }}>
          <Typography color="error.contrastText">{error}</Typography>
        </Paper>
      )}

      {retrieveSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Item retrieved successfully!
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Search Form */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Search for an Item
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Box sx={{ mb: 2 }}>
                    <Button
                      variant={searchType === 'id' ? 'contained' : 'outlined'}
                      onClick={() => setSearchType('id')}
                      sx={{ mr: 1 }}
                    >
                      Search by ID
                    </Button>
                    <Button
                      variant={searchType === 'name' ? 'contained' : 'outlined'}
                      onClick={() => setSearchType('name')}
                    >
                      Search by Name
                    </Button>
                  </Box>
                </Grid>

                {searchType === 'id' ? (
                  <Grid item xs={12}>
                    <TextField
                      label="Item ID"
                      fullWidth
                      value={itemId}
                      onChange={(e) => setItemId(e.target.value)}
                      margin="normal"
                      required
                    />
                  </Grid>
                ) : (
                  <Grid item xs={12}>
                    <TextField
                      label="Item Name"
                      fullWidth
                      value={itemName}
                      onChange={(e) => setItemName(e.target.value)}
                      margin="normal"
                      required
                    />
                  </Grid>
                )}

                <Grid item xs={12}>
                  <TextField
                    label="User ID (required for retrieval)"
                    fullWidth
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    margin="normal"
                    helperText="A user ID is required to track who retrieved the item"
                  />
                </Grid>

                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSearch}
                    disabled={loading}
                    fullWidth
                  >
                    {loading ? <CircularProgress size={24} /> : 'Search'}
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Search Results */}
        {success && item && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Item Found
                </Typography>
                <Paper sx={{ p: 2, mb: 2 }}>
                  <Typography variant="subtitle1">
                    {item.name} (ID: {item.itemId})
                  </Typography>
                  <Typography variant="body2">
                    Container: {item.containerId} (Zone: {item.zone})
                  </Typography>
                  <Typography variant="body2">
                    Position: ({item.position.startCoordinates.width}, {item.position.startCoordinates.depth}, {item.position.startCoordinates.height}) to ({item.position.endCoordinates.width}, {item.position.endCoordinates.depth}, {item.position.endCoordinates.height})
                  </Typography>
                </Paper>

                <Typography variant="h6" gutterBottom>
                  Retrieval Steps
                </Typography>
                <Stepper orientation="vertical">
                  {retrievalSteps.map((step, index) => (
                    <Step key={index} active={true}>
                      <StepLabel>Step {step.step}: {step.action}</StepLabel>
                      <StepContent>
                        <Typography>
                          {step.action === 'retrieve' && `Retrieve ${step.itemName}`}
                          {step.action === 'remove' && `Remove ${step.itemName}`}
                          {step.action === 'setAside' && `Set aside ${step.itemName}`}
                          {step.action === 'placeBack' && `Place back ${step.itemName}`}
                        </Typography>
                      </StepContent>
                    </Step>
                  ))}
                </Stepper>

                <Box sx={{ mt: 3 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleRetrieve}
                    disabled={loading || retrieveSuccess}
                    fullWidth
                  >
                    {loading ? <CircularProgress size={24} /> : 'Mark as Retrieved'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Retrieval Success Message */}
        {retrieveSuccess && (
          <Grid item xs={12}>
            <Alert severity="success" sx={{ mb: 2 }}>
              Item retrieved successfully! The item has been removed from its container and is now available for use.
            </Alert>
            <Button variant="outlined" onClick={handleReset} fullWidth>
              New Search
            </Button>
          </Grid>
        )}

        {/* Reset Button */}
        {success && !retrieveSuccess && (
          <Grid item xs={12}>
            <Button variant="outlined" onClick={handleReset} fullWidth>
              New Search
            </Button>
          </Grid>
        )}
      </Grid>
    </Box>
  )
}
