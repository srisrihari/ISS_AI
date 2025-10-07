import { useState, useEffect } from 'react'
const API_BASE = (import.meta as any).env?.VITE_API_BASE || ''
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Grid,
  Typography,
  Paper,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemText,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  TextField,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormGroup,
  FormControlLabel,
  LinearProgress,
  SelectChangeEvent,
} from '@mui/material'
import WarningIcon from '@mui/icons-material/Warning'
import MedicalServicesIcon from '@mui/icons-material/MedicalServices'
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment'
import ElectricBoltIcon from '@mui/icons-material/ElectricBolt'
import SettingsIcon from '@mui/icons-material/Settings'

interface CriticalItem {
  itemId: string
  name: string
  priority: number
  containerId: string | null
  zone: string | null
  accessibilityScore: number
  isAccessible: boolean
  retrievalSteps: number
}

interface RetrievalStep {
  step: number
  action: string
  itemId: string
  itemName: string
  description: string
}

interface AccessPlan {
  itemId: string
  name: string
  priority: number
  containerId: string
  zone: string
  isAccessible: boolean
  retrievalSteps: RetrievalStep[]
}

interface EmergencyResponse {
  success: boolean
  emergencyType: string
  affectedZones: string[] | null
  timestamp: string
  criticalItems: number
  accessPlans: AccessPlan[]
}

export default function Emergency() {
  const [loading, setLoading] = useState(false)
  const [optimizing, setOptimizing] = useState(false)
  const [criticalItems, setCriticalItems] = useState<CriticalItem[]>([])
  const [emergencyResponse, setEmergencyResponse] = useState<EmergencyResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  // Emergency declaration dialog
  const [open, setOpen] = useState(false)
  const [emergencyType, setEmergencyType] = useState('medical')
  const [selectedZones, setSelectedZones] = useState<string[]>([])
  const [availableZones, setAvailableZones] = useState<string[]>([])
  
  useEffect(() => {
    fetchCriticalItems()
    fetchAvailableZones()
  }, [])
  
  const fetchCriticalItems = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${API_BASE}/api/emergency/critical-items`)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch critical items: ${response.statusText}`)
      }
      
      const data = await response.json()
      setCriticalItems(data)
    } catch (err) {
      console.error('Error fetching critical items:', err)
      setError('Failed to load critical items')
    } finally {
      setLoading(false)
    }
  }
  
  const fetchAvailableZones = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/containers`)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch containers: ${response.statusText}`)
      }
      
      const data = await response.json()
      const zones = Array.from(new Set(data.containers.map((container: any) => container.zone)))
      setAvailableZones(zones as string[])
    } catch (err) {
      console.error('Error fetching zones:', err)
    }
  }
  
  const handleOptimizeAccess = async () => {
    setOptimizing(true)
    setError(null)
    setSuccess(null)
    
    try {
      const response = await fetch(`${API_BASE}/api/emergency/optimize-access`, {
        method: 'POST',
      })
      
      if (!response.ok) {
        throw new Error(`Failed to optimize emergency access: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      // Update critical items with the optimized ones
      if (data.items) {
        setCriticalItems(data.items)
      }
      
      setSuccess(`Optimized ${data.optimizedItems} critical items for emergency access`)
    } catch (err) {
      console.error('Error optimizing emergency access:', err)
      setError('Failed to optimize emergency access')
    } finally {
      setOptimizing(false)
    }
  }
  
  const handleDeclareEmergency = () => {
    setOpen(true)
  }
  
  const handleClose = () => {
    setOpen(false)
  }
  
  const handleEmergencyTypeChange = (event: SelectChangeEvent) => {
    setEmergencyType(event.target.value as string)
  }
  
  const handleZoneToggle = (zone: string) => {
    setSelectedZones(
      selectedZones.includes(zone)
        ? selectedZones.filter(z => z !== zone)
        : [...selectedZones, zone]
    )
  }
  
  const handleSubmitEmergency = async () => {
    setLoading(true)
    setError(null)
    setSuccess(null)
    
    try {
      // Prepare URL and parameters
      const url = `${API_BASE}/api/emergency/declare`
      const params = new URLSearchParams()
      params.append('emergency_type', getEmergencyTypeLabel(emergencyType))
      
      if (selectedZones.length > 0) {
        selectedZones.forEach(zone => {
          params.append('affected_zones', zone)
        })
      }
      
      const response = await fetch(`${url}?${params.toString()}`, {
        method: 'POST',
      })
      
      if (!response.ok) {
        throw new Error(`Failed to declare emergency: ${response.statusText}`)
      }
      
      const data = await response.json()
      setEmergencyResponse(data)
      setSuccess(`Emergency declared: ${getEmergencyTypeLabel(emergencyType)}`)
    } catch (err) {
      console.error('Error declaring emergency:', err)
      setError('Failed to declare emergency')
    } finally {
      setLoading(false)
      setOpen(false)
    }
  }
  
  const getEmergencyTypeLabel = (type: string): string => {
    switch (type) {
      case 'medical':
        return 'Medical Emergency'
      case 'fire':
        return 'Fire Emergency'
      case 'electrical':
        return 'Electrical System Failure'
      case 'mechanical':
        return 'Mechanical System Failure'
      default:
        return type
    }
  }
  
  const getEmergencyIcon = (type: string) => {
    switch (type) {
      case 'medical':
        return <MedicalServicesIcon fontSize="large" />
      case 'fire':
        return <LocalFireDepartmentIcon fontSize="large" />
      case 'electrical':
        return <ElectricBoltIcon fontSize="large" />
      case 'mechanical':
        return <SettingsIcon fontSize="large" />
      default:
        return <WarningIcon fontSize="large" />
    }
  }
  
  const getAccessibilityColor = (score: number) => {
    if (score >= 0.8) return 'success.main'
    if (score >= 0.5) return 'warning.main'
    return 'error.main'
  }
  
  const getAccessibilityLabel = (score: number) => {
    if (score >= 0.8) return 'Easily Accessible'
    if (score >= 0.5) return 'Moderately Accessible'
    return 'Difficult to Access'
  }
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Emergency Protocols
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}
      
      {/* Emergency Actions */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper 
            sx={{ 
              p: 3, 
              backgroundImage: 'linear-gradient(to right, rgba(255,0,0,0.05), rgba(255,0,0,0.2))',
              borderLeft: '4px solid #f44336'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <WarningIcon color="error" sx={{ mr: 2, fontSize: 40 }} />
              <Typography variant="h5">Emergency Response Controls</Typography>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                color="error"
                size="large"
                startIcon={<WarningIcon />}
                onClick={handleDeclareEmergency}
              >
                Declare Emergency
              </Button>
              
              <Button
                variant="outlined"
                color="primary"
                size="large"
                onClick={handleOptimizeAccess}
                disabled={optimizing}
              >
                {optimizing ? <CircularProgress size={24} /> : 'Optimize Critical Items Access'}
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Emergency Response Plan */}
      {emergencyResponse && (
        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {getEmergencyIcon(emergencyType)}
                  <Box sx={{ ml: 2 }}>
                    <Typography variant="h5">
                      {emergencyResponse.emergencyType} Response Plan
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Declared at: {new Date(emergencyResponse.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
                
                <Typography variant="body1" sx={{ mb: 2 }}>
                  Critical items requiring immediate access: {emergencyResponse.criticalItems}
                </Typography>
                
                {emergencyResponse.affectedZones && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1">Affected Zones:</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                      {emergencyResponse.affectedZones.map(zone => (
                        <Chip key={zone} label={zone} color="error" />
                      ))}
                    </Box>
                  </Box>
                )}
                
                <Divider sx={{ mb: 3 }} />
                
                <Typography variant="h6" gutterBottom>
                  Critical Items Access Plans:
                </Typography>
                
                {emergencyResponse.accessPlans.map((plan, index) => (
                  <Card key={index} sx={{ mb: 2, border: '1px solid #e0e0e0' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="h6">
                          {plan.name}
                        </Typography>
                        <Chip
                          label={plan.isAccessible ? 'Easily Accessible' : 'Requires Retrieval Steps'}
                          color={plan.isAccessible ? 'success' : 'warning'}
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Priority: {plan.priority} | Container: {plan.containerId} | Zone: {plan.zone}
                      </Typography>
                      
                      {plan.retrievalSteps.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Retrieval Instructions:
                          </Typography>
                          <Stepper orientation="vertical">
                            {plan.retrievalSteps.map((step) => (
                              <Step key={step.step} active={true}>
                                <StepLabel>{step.action.toUpperCase()}: {step.itemName}</StepLabel>
                                <StepContent>
                                  <Typography>{step.description}</Typography>
                                </StepContent>
                              </Step>
                            ))}
                          </Stepper>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      
      {/* Critical Items List */}
      {!emergencyResponse && (
        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              Critical Items Status
            </Typography>
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : criticalItems.length === 0 ? (
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography>No critical items found</Typography>
              </Paper>
            ) : (
              <Grid container spacing={2}>
                {criticalItems.map((item) => (
                  <Grid item xs={12} md={6} lg={4} key={item.itemId}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="h6">{item.name}</Typography>
                          <Chip
                            label={`Priority: ${item.priority}`}
                            color="primary"
                            variant="outlined"
                            size="small"
                          />
                        </Box>
                        
                        <Divider sx={{ mb: 2 }} />
                        
                        <Typography variant="body2" gutterBottom>
                          <strong>Location:</strong> {item.containerId ? `Container ${item.containerId}` : 'Not stored'} 
                          {item.zone && ` (${item.zone})`}
                        </Typography>
                        
                        <Typography variant="body2" gutterBottom>
                          <strong>Accessibility:</strong>{' '}
                          <span style={{ color: getAccessibilityColor(item.accessibilityScore) }}>
                            {getAccessibilityLabel(item.accessibilityScore)}
                          </span>
                        </Typography>
                        
                        <Typography variant="body2" gutterBottom>
                          <strong>Retrieval Complexity:</strong> {item.retrievalSteps} steps
                        </Typography>
                        
                        <LinearProgress
                          variant="determinate"
                          value={item.accessibilityScore * 100}
                          color={
                            item.accessibilityScore >= 0.8
                              ? 'success'
                              : item.accessibilityScore >= 0.5
                              ? 'warning'
                              : 'error'
                          }
                          sx={{ mt: 1, height: 6, borderRadius: 3 }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Grid>
        </Grid>
      )}
      
      {/* Emergency Declaration Dialog */}
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Declare Emergency</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Declaring an emergency will identify critical items and provide quick access plans.
          </DialogContentText>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Emergency Type</InputLabel>
            <Select
              value={emergencyType}
              onChange={handleEmergencyTypeChange}
              label="Emergency Type"
            >
              <MenuItem value="medical">Medical Emergency</MenuItem>
              <MenuItem value="fire">Fire Emergency</MenuItem>
              <MenuItem value="electrical">Electrical System Failure</MenuItem>
              <MenuItem value="mechanical">Mechanical System Failure</MenuItem>
            </Select>
          </FormControl>
          
          <Typography variant="subtitle1" gutterBottom>
            Affected Zones
          </Typography>
          <FormGroup>
            {availableZones.map((zone) => (
              <FormControlLabel
                key={zone}
                control={
                  <Checkbox
                    checked={selectedZones.includes(zone)}
                    onChange={() => handleZoneToggle(zone)}
                  />
                }
                label={zone}
              />
            ))}
          </FormGroup>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmitEmergency} variant="contained" color="error">
            Declare Emergency
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
} 