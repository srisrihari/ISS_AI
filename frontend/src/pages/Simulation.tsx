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
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  FormControlLabel,
  Switch,
  Chip,
} from '@mui/material'
import { api, SimulationItemStatus } from '../services/api'

export default function Simulation() {
  const [loading, setLoading] = useState(false)
  const [numOfDays, setNumOfDays] = useState<number>(1)
  const [useSpecificItems, setUseSpecificItems] = useState(false)
  const [itemId, setItemId] = useState('')
  const [itemsToUse, setItemsToUse] = useState<{ itemId: string; name?: string }[]>([])
  const [currentDate, setCurrentDate] = useState<string>(new Date().toISOString())
  const [simulationResults, setSimulationResults] = useState<{
    newDate: string;
    itemsUsed: SimulationItemStatus[];
    itemsExpired: SimulationItemStatus[];
    itemsDepletedToday: SimulationItemStatus[];
  } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  
  const handleAddItem = () => {
    if (!itemId) {
      setError('Please enter an Item ID')
      return
    }
    
    setItemsToUse([...itemsToUse, { itemId }])
    setItemId('')
    setError(null)
  }
  
  const handleRemoveItem = (index: number) => {
    const updatedItems = [...itemsToUse]
    updatedItems.splice(index, 1)
    setItemsToUse(updatedItems)
  }
  
  const handleSimulate = async () => {
    if (numOfDays <= 0) {
      setError('Please enter a valid number of days')
      return
    }
    
    setLoading(true)
    setError(null)
    setSuccess(false)
    
    try {
      const response = await api.simulateDay(
        numOfDays,
        useSpecificItems ? itemsToUse : []
      )
      
      setCurrentDate(response.newDate)
      setSimulationResults({
        newDate: response.newDate,
        itemsUsed: response.changes.itemsUsed,
        itemsExpired: response.changes.itemsExpired,
        itemsDepletedToday: response.changes.itemsDepletedToday,
      })
      setSuccess(true)
    } catch (err) {
      console.error('Error simulating time:', err)
      setError('Failed to simulate time. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Time Simulation
      </Typography>
      
      {error && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.dark' }}>
          <Typography color="error.contrastText">{error}</Typography>
        </Paper>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Time simulation completed successfully!
        </Alert>
      )}
      
      <Grid container spacing={3}>
        {/* Current Date */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Date
              </Typography>
              <Typography variant="h4">
                {new Date(currentDate).toLocaleDateString()} {new Date(currentDate).toLocaleTimeString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Simulation Form */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Simulate Time
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    label="Number of Days"
                    type="number"
                    fullWidth
                    value={numOfDays}
                    onChange={(e) => setNumOfDays(parseInt(e.target.value))}
                    margin="normal"
                    required
                    inputProps={{ min: 1 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={useSpecificItems}
                        onChange={(e) => setUseSpecificItems(e.target.checked)}
                      />
                    }
                    label="Specify items to be used each day"
                  />
                </Grid>
                
                {useSpecificItems && (
                  <>
                    <Grid item xs={12}>
                      <TextField
                        label="Item ID"
                        fullWidth
                        value={itemId}
                        onChange={(e) => setItemId(e.target.value)}
                        margin="normal"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Button
                        variant="outlined"
                        onClick={handleAddItem}
                        disabled={!itemId}
                        fullWidth
                      >
                        Add Item
                      </Button>
                    </Grid>
                    
                    {itemsToUse.length > 0 && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle1" gutterBottom>
                          Items to Use Each Day:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {itemsToUse.map((item, index) => (
                            <Chip
                              key={index}
                              label={item.itemId}
                              onDelete={() => handleRemoveItem(index)}
                            />
                          ))}
                        </Box>
                      </Grid>
                    )}
                  </>
                )}
                
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSimulate}
                    disabled={loading}
                    fullWidth
                  >
                    {loading ? <CircularProgress size={24} /> : 'Simulate Time'}
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Simulation Results */}
        {success && simulationResults && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Simulation Results
                </Typography>
                <Typography variant="body1" gutterBottom>
                  New Date: {new Date(simulationResults.newDate).toLocaleDateString()} {new Date(simulationResults.newDate).toLocaleTimeString()}
                </Typography>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle1" gutterBottom>
                  Items Used: {simulationResults.itemsUsed.length}
                </Typography>
                {simulationResults.itemsUsed.length > 0 ? (
                  <TableContainer component={Paper} sx={{ mb: 2 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Item ID</TableCell>
                          <TableCell>Name</TableCell>
                          <TableCell>Remaining Uses</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {simulationResults.itemsUsed.map((item, index) => (
                          <TableRow key={index}>
                            <TableCell>{item.itemId}</TableCell>
                            <TableCell>{item.name}</TableCell>
                            <TableCell>{item.remainingUses}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Typography variant="body2" sx={{ mb: 2 }}>No items used during simulation.</Typography>
                )}
                
                <Typography variant="subtitle1" gutterBottom>
                  Items Expired: {simulationResults.itemsExpired.length}
                </Typography>
                {simulationResults.itemsExpired.length > 0 ? (
                  <TableContainer component={Paper} sx={{ mb: 2 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Item ID</TableCell>
                          <TableCell>Name</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {simulationResults.itemsExpired.map((item, index) => (
                          <TableRow key={index}>
                            <TableCell>{item.itemId}</TableCell>
                            <TableCell>{item.name}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Typography variant="body2" sx={{ mb: 2 }}>No items expired during simulation.</Typography>
                )}
                
                <Typography variant="subtitle1" gutterBottom>
                  Items Depleted: {simulationResults.itemsDepletedToday.length}
                </Typography>
                {simulationResults.itemsDepletedToday.length > 0 ? (
                  <TableContainer component={Paper}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Item ID</TableCell>
                          <TableCell>Name</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {simulationResults.itemsDepletedToday.map((item, index) => (
                          <TableRow key={index}>
                            <TableCell>{item.itemId}</TableCell>
                            <TableCell>{item.name}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Typography variant="body2">No items depleted during simulation.</Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  )
}
