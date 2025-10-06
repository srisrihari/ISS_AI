import { useState, useEffect } from 'react'
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material'
import { api, WasteItem, ReturnPlanStep, RetrievalStep, ReturnManifest } from '../services/api'

export default function Waste() {
  const [loading, setLoading] = useState(true)
  const [wasteItems, setWasteItems] = useState<WasteItem[]>([])
  const [undockingContainerId, setUndockingContainerId] = useState('')
  const [maxWeight, setMaxWeight] = useState<number>(100)
  const [returnPlan, setReturnPlan] = useState<ReturnPlanStep[]>([])
  const [retrievalSteps, setRetrievalSteps] = useState<RetrievalStep[]>([])
  const [returnManifest, setReturnManifest] = useState<ReturnManifest | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [planSuccess, setPlanSuccess] = useState(false)
  const [undockingSuccess, setUndockingSuccess] = useState(false)
  
  useEffect(() => {
    fetchWasteItems()
  }, [])
  
  const fetchWasteItems = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await api.identifyWaste()
      setWasteItems(response.wasteItems)
    } catch (err) {
      console.error('Error fetching waste items:', err)
      setError('Failed to fetch waste items. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  const handleCreateReturnPlan = async () => {
    if (!undockingContainerId) {
      setError('Please enter an undocking container ID')
      return
    }
    
    if (maxWeight <= 0) {
      setError('Please enter a valid maximum weight')
      return
    }
    
    setLoading(true)
    setError(null)
    setPlanSuccess(false)
    
    try {
      const response = await api.createReturnPlan(undockingContainerId, maxWeight)
      
      setReturnPlan(response.returnPlan)
      setRetrievalSteps(response.retrievalSteps)
      setReturnManifest(response.returnManifest)
      setPlanSuccess(true)
    } catch (err) {
      console.error('Error creating return plan:', err)
      setError('Failed to create return plan. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  const handleCompleteUndocking = async () => {
    if (!undockingContainerId) {
      setError('Please enter an undocking container ID')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await api.completeUndocking(undockingContainerId)
      
      if (response.success) {
        setUndockingSuccess(true)
        // Refresh waste items
        await fetchWasteItems()
      } else {
        setError('Failed to complete undocking')
      }
    } catch (err) {
      console.error('Error completing undocking:', err)
      setError('Failed to complete undocking. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Waste Management
      </Typography>
      
      {error && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.dark' }}>
          <Typography color="error.contrastText">{error}</Typography>
        </Paper>
      )}
      
      {undockingSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Undocking completed successfully!
        </Alert>
      )}
      
      <Grid container spacing={3}>
        {/* Waste Items */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Waste Items ({wasteItems.length})
                </Typography>
                <Button
                  variant="outlined"
                  onClick={fetchWasteItems}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Box>
              
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
                  <CircularProgress />
                </Box>
              ) : wasteItems.length === 0 ? (
                <Typography>No waste items detected.</Typography>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Item ID</TableCell>
                        <TableCell>Name</TableCell>
                        <TableCell>Reason</TableCell>
                        <TableCell>Container</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {wasteItems.map((item) => (
                        <TableRow key={item.itemId}>
                          <TableCell>{item.itemId}</TableCell>
                          <TableCell>{item.name}</TableCell>
                          <TableCell>{item.reason}</TableCell>
                          <TableCell>{item.containerId}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Return Plan Form */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Create Return Plan
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    label="Undocking Container ID"
                    fullWidth
                    value={undockingContainerId}
                    onChange={(e) => setUndockingContainerId(e.target.value)}
                    margin="normal"
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Maximum Weight (kg)"
                    type="number"
                    fullWidth
                    value={maxWeight}
                    onChange={(e) => setMaxWeight(parseFloat(e.target.value))}
                    margin="normal"
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleCreateReturnPlan}
                    disabled={loading || wasteItems.length === 0}
                    fullWidth
                  >
                    {loading ? <CircularProgress size={24} /> : 'Create Return Plan'}
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Return Plan Results */}
        {planSuccess && returnManifest && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Return Manifest
                </Typography>
                <Paper sx={{ p: 2, mb: 2 }}>
                  <Typography variant="body1">
                    Undocking Container: {returnManifest.undockingContainerId}
                  </Typography>
                  <Typography variant="body1">
                    Undocking Date: {new Date(returnManifest.undockingDate).toLocaleString()}
                  </Typography>
                  <Typography variant="body1">
                    Total Items: {returnManifest.returnItems.length}
                  </Typography>
                  <Typography variant="body1">
                    Total Volume: {returnManifest.totalVolume.toFixed(2)} cm³
                  </Typography>
                  <Typography variant="body1">
                    Total Weight: {returnManifest.totalWeight.toFixed(2)} kg
                  </Typography>
                </Paper>
                
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleCompleteUndocking}
                  disabled={loading || undockingSuccess}
                  fullWidth
                >
                  {loading ? <CircularProgress size={24} /> : 'Complete Undocking'}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        )}
        
        {/* Return Plan Steps */}
        {planSuccess && returnPlan.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Return Plan Steps
                </Typography>
                <Stepper orientation="vertical">
                  {returnPlan.map((step, index) => (
                    <Step key={index} active={true}>
                      <StepLabel>Step {step.step}</StepLabel>
                      <StepContent>
                        <Typography>
                          Move {step.itemName} (ID: {step.itemId}) from container {step.fromContainer} to {step.toContainer}
                        </Typography>
                      </StepContent>
                    </Step>
                  ))}
                </Stepper>
              </CardContent>
            </Card>
          </Grid>
        )}
        
        {/* Retrieval Steps */}
        {planSuccess && retrievalSteps.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Detailed Retrieval Steps
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
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  )
}
