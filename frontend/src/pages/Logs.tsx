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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  MenuItem,
  Chip,
} from '@mui/material'
import { api, LogEntry } from '../services/api'

export default function Logs() {
  const [loading, setLoading] = useState(false)
  const [startDate, setStartDate] = useState<string>(
    new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [endDate, setEndDate] = useState<string>(new Date().toISOString().split('T')[0])
  const [itemId, setItemId] = useState('')
  const [userId, setUserId] = useState('')
  const [actionType, setActionType] = useState('')
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [error, setError] = useState<string | null>(null)
  
  const actionTypes = [
    { value: '', label: 'All Actions' },
    { value: 'placement', label: 'Placement' },
    { value: 'retrieval', label: 'Retrieval' },
    { value: 'rearrangement', label: 'Rearrangement' },
    { value: 'disposal', label: 'Disposal' },
    { value: 'simulation', label: 'Simulation' },
  ]
  
  const handleFetchLogs = async () => {
    if (!startDate || !endDate) {
      setError('Please select both start and end dates')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await api.getLogs(
        `${startDate}T00:00:00Z`,
        `${endDate}T23:59:59Z`,
        itemId || undefined,
        userId || undefined,
        actionType || undefined
      )
      
      setLogs(response.logs)
    } catch (err) {
      console.error('Error fetching logs:', err)
      setError('Failed to fetch logs. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  const getActionColor = (action: string) => {
    switch (action) {
      case 'placement':
        return 'primary'
      case 'retrieval':
        return 'secondary'
      case 'rearrangement':
        return 'info'
      case 'disposal':
        return 'error'
      case 'simulation':
        return 'warning'
      default:
        return 'default'
    }
  }
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        System Logs
      </Typography>
      
      {error && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.dark' }}>
          <Typography color="error.contrastText">{error}</Typography>
        </Paper>
      )}
      
      <Grid container spacing={3}>
        {/* Log Filters */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Filter Logs
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <TextField
                    label="Start Date"
                    type="date"
                    fullWidth
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <TextField
                    label="End Date"
                    type="date"
                    fullWidth
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    label="Item ID"
                    fullWidth
                    value={itemId}
                    onChange={(e) => setItemId(e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    label="User ID"
                    fullWidth
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    select
                    label="Action Type"
                    fullWidth
                    value={actionType}
                    onChange={(e) => setActionType(e.target.value)}
                    margin="normal"
                  >
                    {actionTypes.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleFetchLogs}
                    disabled={loading}
                    fullWidth
                  >
                    {loading ? <CircularProgress size={24} /> : 'Fetch Logs'}
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Log Results */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Log Entries ({logs.length})
              </Typography>
              
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
                  <CircularProgress />
                </Box>
              ) : logs.length === 0 ? (
                <Typography>No logs found for the selected criteria.</Typography>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>User</TableCell>
                        <TableCell>Action</TableCell>
                        <TableCell>Item ID</TableCell>
                        <TableCell>Details</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {logs.map((log, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            {new Date(log.timestamp).toLocaleString()}
                          </TableCell>
                          <TableCell>{log.userId}</TableCell>
                          <TableCell>
                            <Chip
                              label={log.actionType}
                              color={getActionColor(log.actionType)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{log.itemId}</TableCell>
                          <TableCell>
                            {log.details.fromContainer && (
                              <Typography variant="body2">
                                From: {log.details.fromContainer}
                              </Typography>
                            )}
                            {log.details.toContainer && (
                              <Typography variant="body2">
                                To: {log.details.toContainer}
                              </Typography>
                            )}
                            {log.details.reason && (
                              <Typography variant="body2">
                                Reason: {log.details.reason}
                              </Typography>
                            )}
                            {log.details.description && (
                              <Typography variant="body2">
                                {log.details.description}
                              </Typography>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
