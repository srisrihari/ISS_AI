import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Typography,
  Grid,
  Paper,
  CircularProgress,
  Divider,
  Chip,
  Fade,
  Tooltip,
  LinearProgress,
  alpha,
  useTheme,
  Zoom,
  Skeleton,
} from '@mui/material'
import {
  Add as AddIcon,
  Search as SearchIcon,
  Delete as DeleteIcon,
  Timer as TimerIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material'
import { api, WasteItem } from '../services/api'

export default function Dashboard() {
  const theme = useTheme()
  const [loading, setLoading] = useState(true)
  const [wasteItems, setWasteItems] = useState<WasteItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [systemStatus, setSystemStatus] = useState({
    cargoManagement: { status: 'operational', value: 100 },
    wasteTracking: { status: 'operational', value: 100 },
    timeSimulation: { status: 'operational', value: 100 },
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const wasteResponse = await api.identifyWaste()
        setWasteItems(wasteResponse.wasteItems)
      } catch (err) {
        console.error('Error fetching dashboard data:', err)
        setError('Failed to load dashboard data. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center', 
        mt: 8,
        height: '50vh'
      }}>
        <CircularProgress 
          size={60} 
          thickness={4} 
          sx={{ 
            color: theme => `${theme.palette.primary.main}`,
            animation: 'pulse 1.5s ease-in-out infinite',
            '@keyframes pulse': {
              '0%': {
                opacity: 1,
                transform: 'scale(1)'
              },
              '50%': {
                opacity: 0.7,
                transform: 'scale(1.05)'
              },
              '100%': {
                opacity: 1,
                transform: 'scale(1)'
              },
            }
          }}
        />
        <Typography 
          variant="h6" 
          sx={{ 
            mt: 2, 
            opacity: 0.8,
            fontWeight: 500,
            background: 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Loading dashboard data...
        </Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ mt: 2 }}>
        <Zoom in={true}>
          <Paper 
            elevation={4}
            sx={{ 
              p: 3, 
              bgcolor: alpha(theme.palette.error.main, 0.1),
              borderRadius: 2,
              border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              boxShadow: `0 4px 20px ${alpha(theme.palette.error.main, 0.25)}`,
              transition: 'all 0.3s ease-in-out',
            }}
          >
            <WarningIcon color="error" fontSize="large" sx={{ animation: 'pulse 2s infinite' }} />
            <Box>
              <Typography variant="h6" color="error.light" fontWeight={600} gutterBottom>
                Error Encountered
              </Typography>
              <Typography color="error.light" fontWeight={500}>{error}</Typography>
            </Box>
          </Paper>
        </Zoom>
      </Box>
    )
  }

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', flexDirection: 'column' }}>
        <Typography 
          variant="h4" 
          sx={{ 
            fontWeight: 600,
            background: 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1,
            letterSpacing: '0.5px',
            textShadow: '0 2px 10px rgba(0,0,0,0.2)',
            animation: 'fadeIn 0.8s ease-in-out',
            '@keyframes fadeIn': {
              '0%': {
                opacity: 0,
                transform: 'translateY(-10px)'
              },
              '100%': {
                opacity: 1,
                transform: 'translateY(0)'
              },
            }
          }}
        >
          Space Station Cargo Management
        </Typography>
        <Typography 
          variant="subtitle1" 
          color="text.secondary" 
          gutterBottom
          sx={{ 
            opacity: 0.9,
            animation: 'fadeIn 0.8s ease-in-out 0.2s both',
            '@keyframes fadeIn': {
              '0%': {
                opacity: 0,
                transform: 'translateY(-5px)'
              },
              '100%': {
                opacity: 0.9,
                transform: 'translateY(0)'
              },
            }
          }}
        >
          Monitor and manage cargo operations across the space station
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Zoom in={true} style={{ transitionDelay: '100ms' }}>
            <Card 
              sx={{ 
                height: '100%',
                borderRadius: 3,
                boxShadow: theme => `0 8px 24px ${alpha(theme.palette.primary.main, 0.15)}`,
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                '&:hover': {
                  boxShadow: theme => `0 12px 28px ${alpha(theme.palette.primary.main, 0.25)}`,
                }
              }}
            >
              <CardContent>
                <Typography 
                  variant="h5" 
                  gutterBottom 
                  fontWeight={600}
                  sx={{ 
                    position: 'relative',
                    '&:after': {
                      content: '""',
                      position: 'absolute',
                      bottom: -8,
                      left: 0,
                      width: 40,
                      height: 3,
                      borderRadius: 4,
                      backgroundColor: 'primary.main',
                    }
                  }}
                >
                  Quick Actions
                </Typography>
                <Divider sx={{ mb: 3, opacity: 0.6 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Tooltip 
                      title="Add new items to containers" 
                      arrow 
                      placement="top" 
                      TransitionComponent={Fade}
                      enterDelay={500}
                      leaveDelay={200}
                    >
                      <Button
                        component={Link}
                        to="/placement"
                        variant="contained"
                        fullWidth
                        sx={{ 
                          mb: 1,
                          py: 1.5,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'flex-start',
                          pl: 2,
                          borderRadius: 2,
                          boxShadow: '0 4px 10px rgba(0,0,0,0.15)',
                          transition: 'all 0.2s ease-in-out',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 6px 12px rgba(0,0,0,0.2)',
                          },
                          '&:active': {
                            transform: 'translateY(1px)',
                          }
                        }}
                        startIcon={<AddIcon />}
                      >
                        Place Items
                      </Button>
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6}>
                    <Tooltip 
                      title="Search and retrieve items" 
                      arrow 
                      placement="top" 
                      TransitionComponent={Fade}
                      enterDelay={500}
                      leaveDelay={200}
                    >
                      <Button
                        component={Link}
                        to="/search"
                        variant="contained"
                        color="info"
                        fullWidth
                        sx={{ 
                          mb: 1,
                          py: 1.5,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'flex-start',
                          pl: 2,
                          borderRadius: 2,
                          boxShadow: '0 4px 10px rgba(0,0,0,0.15)',
                          transition: 'all 0.2s ease-in-out',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 6px 12px rgba(0,0,0,0.2)',
                          },
                          '&:active': {
                            transform: 'translateY(1px)',
                          }
                        }}
                        startIcon={<SearchIcon />}
                      >
                        Find Item
                      </Button>
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6}>
                    <Tooltip 
                      title="Manage waste items" 
                      arrow 
                      placement="top" 
                      TransitionComponent={Fade}
                      enterDelay={500}
                      leaveDelay={200}
                    >
                      <Button
                        component={Link}
                        to="/waste"
                        variant="contained"
                        color="secondary"
                        fullWidth
                        sx={{ 
                          mb: 1,
                          py: 1.5,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'flex-start',
                          pl: 2,
                          borderRadius: 2,
                          boxShadow: '0 4px 10px rgba(0,0,0,0.15)',
                          transition: 'all 0.2s ease-in-out',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 6px 12px rgba(0,0,0,0.2)',
                          },
                          '&:active': {
                            transform: 'translateY(1px)',
                          }
                        }}
                        startIcon={<DeleteIcon />}
                      >
                        Manage Waste
                      </Button>
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6}>
                    <Tooltip 
                      title="Simulate passage of time" 
                      arrow 
                      placement="top" 
                      TransitionComponent={Fade}
                      enterDelay={500}
                      leaveDelay={200}
                    >
                      <Button
                        component={Link}
                        to="/simulation"
                        variant="contained"
                        color="warning"
                        fullWidth
                        sx={{ 
                          mb: 1,
                          py: 1.5,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'flex-start',
                          pl: 2,
                          borderRadius: 2,
                          boxShadow: '0 4px 10px rgba(0,0,0,0.15)',
                          transition: 'all 0.2s ease-in-out',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 6px 12px rgba(0,0,0,0.2)',
                          },
                          '&:active': {
                            transform: 'translateY(1px)',
                          }
                        }}
                        startIcon={<TimerIcon />}
                      >
                        Simulate Time
                      </Button>
                    </Tooltip>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Zoom>
        </Grid>

        {/* Waste Items */}
        <Grid item xs={12} md={6}>
          <Zoom in={true} style={{ transitionDelay: '200ms' }}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                borderRadius: 3,
                boxShadow: theme => `0 8px 24px ${alpha(theme.palette.primary.main, 0.15)}`,
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                '&:hover': {
                  boxShadow: theme => `0 12px 28px ${alpha(theme.palette.primary.main, 0.25)}`,
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography 
                    variant="h5" 
                    fontWeight={600}
                    sx={{ 
                      position: 'relative',
                      '&:after': {
                        content: '""',
                        position: 'absolute',
                        bottom: -8,
                        left: 0,
                        width: 40,
                        height: 3,
                        borderRadius: 4,
                        backgroundColor: wasteItems.length > 0 ? 'warning.main' : 'success.main',
                      }
                    }}
                  >
                    Waste Items
                  </Typography>
                  <Chip 
                    label={`${wasteItems.length} items`} 
                    color={wasteItems.length > 0 ? "warning" : "success"}
                    size="small"
                    sx={{ 
                      fontWeight: 600,
                      borderRadius: 1.5,
                      px: 1,
                      boxShadow: wasteItems.length > 0 ? '0 2px 8px rgba(255,152,0,0.3)' : '0 2px 8px rgba(102,187,106,0.3)',
                    }}
                  />
                </Box>
                <Divider sx={{ mb: 3, opacity: 0.6 }} />
                {wasteItems.length === 0 ? (
                  <Fade in={true} timeout={800}>
                    <Box sx={{ 
                      display: 'flex', 
                      flexDirection: 'column', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      py: 5,
                      bgcolor: alpha(theme.palette.success.main, 0.05),
                      borderRadius: 3,
                      border: `1px dashed ${alpha(theme.palette.success.main, 0.3)}`,
                      boxShadow: `inset 0 0 20px ${alpha(theme.palette.success.main, 0.1)}`,
                    }}>
                      <CheckCircleIcon 
                        color="success" 
                        sx={{ 
                          fontSize: 50, 
                          mb: 1,
                          animation: 'pulse 2s infinite',
                          '@keyframes pulse': {
                            '0%': {
                              transform: 'scale(1)',
                              opacity: 1
                            },
                            '50%': {
                              transform: 'scale(1.1)',
                              opacity: 0.8
                            },
                            '100%': {
                              transform: 'scale(1)',
                              opacity: 1
                            },
                          }
                        }} 
                      />
                      <Typography fontWeight={500}>No waste items detected</Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center', maxWidth: '80%' }}>
                        All items are properly stored and maintained
                      </Typography>
                    </Box>
                  </Fade>
                ) : (
                  <Box>
                    <Typography 
                      variant="body2" 
                      color="warning.light" 
                      sx={{ 
                        mb: 2, 
                        display: 'flex', 
                        alignItems: 'center',
                        gap: 1,
                        fontWeight: 500,
                        p: 1,
                        borderRadius: 1.5,
                        bgcolor: alpha(theme.palette.warning.main, 0.08),
                      }}
                    >
                      <WarningIcon 
                        fontSize="small" 
                        sx={{ 
                          animation: 'blink 1.5s infinite',
                          '@keyframes blink': {
                            '0%': { opacity: 1 },
                            '50%': { opacity: 0.5 },
                            '100%': { opacity: 1 },
                          }
                        }} 
                      />
                      {wasteItems.length} waste items require attention
                    </Typography>
                    {wasteItems.slice(0, 5).map((item, index) => (
                      <Fade key={item.itemId} in={true} timeout={500 + (index * 100)}>
                        <Paper 
                          elevation={3}
                          sx={{ 
                            p: 2, 
                            mb: 1.5, 
                            borderRadius: 2,
                            border: `1px solid ${alpha(theme.palette.warning.main, 0.3)}`,
                            bgcolor: alpha(theme.palette.warning.main, 0.05),
                            transition: 'all 0.3s ease-in-out',
                            '&:hover': {
                              transform: 'translateX(5px)',
                              boxShadow: `0 4px 12px ${alpha(theme.palette.warning.main, 0.3)}`,
                              bgcolor: alpha(theme.palette.warning.main, 0.08),
                            }
                          }}
                        >
                          <Typography variant="body1" fontWeight={600}>{item.name}</Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1.5, flexWrap: 'wrap', gap: 1 }}>
                            <Chip 
                              label={`Reason: ${item.reason}`} 
                              size="small" 
                              color="warning"
                              variant="outlined"
                              sx={{ 
                                fontSize: '0.75rem',
                                fontWeight: 500,
                                borderRadius: 1,
                              }}
                            />
                            <Chip 
                              label={`Container: ${item.containerId}`} 
                              size="small"
                              variant="outlined"
                              sx={{ 
                                fontSize: '0.75rem',
                                fontWeight: 500,
                                borderRadius: 1,
                              }}
                            />
                          </Box>
                        </Paper>
                      </Fade>
                    ))}
                    {wasteItems.length > 5 && (
                      <Typography 
                        variant="body2" 
                        color="text.secondary"
                        sx={{ 
                          mt: 2, 
                          textAlign: 'center',
                          fontStyle: 'italic',
                          p: 1,
                          borderRadius: 1,
                          bgcolor: alpha(theme.palette.background.paper, 0.3),
                        }}
                      >
                        And {wasteItems.length - 5} more items...
                      </Typography>
                    )}
                  </Box>
                )}
              </CardContent>
              <CardActions sx={{ justifyContent: 'flex-end', p: 2, pt: 0 }}>
                <Button 
                  component={Link} 
                  to="/waste" 
                  variant="outlined" 
                  color="warning"
                  endIcon={<DeleteIcon />}
                  disabled={wasteItems.length === 0}
                  sx={{
                    borderRadius: 2,
                    px: 2,
                    py: 0.8,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
                    },
                    '&:active': {
                      transform: 'translateY(1px)'
                    }
                  }}
                >
                  Manage All Waste
                </Button>
              </CardActions>
            </Card>
          </Zoom>
        </Grid>

        {/* System Status */}
        <Grid item xs={12}>
          <Zoom in={true} style={{ transitionDelay: '300ms' }}>
            <Card 
              sx={{ 
                borderRadius: 3,
                boxShadow: theme => `0 8px 24px ${alpha(theme.palette.primary.main, 0.15)}`,
                overflow: 'visible'
              }}
            >
              <CardContent>
                <Typography 
                  variant="h5" 
                  gutterBottom 
                  fontWeight={600}
                  sx={{ 
                    position: 'relative',
                    '&:after': {
                      content: '""',
                      position: 'absolute',
                      bottom: -8,
                      left: 0,
                      width: 40,
                      height: 3,
                      borderRadius: 4,
                      backgroundColor: 'primary.main',
                    }
                  }}
                >
                  System Status
                </Typography>
                <Divider sx={{ mb: 3, opacity: 0.6 }} />
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={4}>
                    <Fade in={true} timeout={800}>
                      <Paper 
                        elevation={0}
                        sx={{ 
                          p: 3, 
                          textAlign: 'center',
                          borderRadius: 3,
                          bgcolor: alpha(theme.palette.success.main, 0.05),
                          border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
                          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                          '&:hover': {
                            transform: 'translateY(-5px)',
                            boxShadow: `0 10px 20px ${alpha(theme.palette.success.main, 0.2)}`,
                          }
                        }}
                      >
                        <Typography variant="h6" fontWeight={600} gutterBottom>Cargo Management</Typography>
                        <Box sx={{ width: '100%', mb: 1, position: 'relative' }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={systemStatus.cargoManagement.value} 
                            color="success"
                            sx={{ 
                              height: 10, 
                              borderRadius: 5,
                              bgcolor: alpha(theme.palette.success.main, 0.1),
                              '& .MuiLinearProgress-bar': {
                                borderRadius: 5,
                                backgroundImage: 'linear-gradient(90deg, rgba(102,187,106,0.8) 0%, rgba(102,187,106,1) 100%)',
                                transition: 'transform 1s cubic-bezier(0.4, 0, 0.2, 1)'
                              }
                            }}
                          />
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              position: 'absolute', 
                              right: 0, 
                              top: -18, 
                              fontWeight: 'bold',
                              color: 'success.main'
                            }}
                          >
                            {systemStatus.cargoManagement.value}%
                          </Typography>
                        </Box>
                        <Typography
                          variant="body1"
                          sx={{ 
                            color: 'success.main', 
                            fontWeight: 'bold',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: 1,
                            mt: 1.5,
                            p: 1,
                            borderRadius: 2,
                            bgcolor: alpha(theme.palette.success.main, 0.1),
                          }}
                        >
                          <CheckCircleIcon 
                            fontSize="small" 
                            sx={{ 
                              animation: 'pulse 2s infinite',
                              '@keyframes pulse': {
                                '0%': { opacity: 0.7 },
                                '50%': { opacity: 1 },
                                '100%': { opacity: 0.7 },
                              }
                            }} 
                          />
                          Operational
                        </Typography>
                      </Paper>
                    </Fade>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Fade in={true} timeout={1000}>
                      <Paper 
                        elevation={0}
                        sx={{ 
                          p: 3, 
                          textAlign: 'center',
                          borderRadius: 3,
                          bgcolor: alpha(theme.palette.success.main, 0.05),
                          border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
                          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                          '&:hover': {
                            transform: 'translateY(-5px)',
                            boxShadow: `0 10px 20px ${alpha(theme.palette.success.main, 0.2)}`,
                          }
                        }}
                      >
                        <Typography variant="h6" fontWeight={600} gutterBottom>Waste Tracking</Typography>
                        <Box sx={{ width: '100%', mb: 1, position: 'relative' }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={systemStatus.wasteTracking.value} 
                            color="success"
                            sx={{ 
                              height: 10, 
                              borderRadius: 5,
                              bgcolor: alpha(theme.palette.success.main, 0.1),
                              '& .MuiLinearProgress-bar': {
                                borderRadius: 5,
                                backgroundImage: 'linear-gradient(90deg, rgba(102,187,106,0.8) 0%, rgba(102,187,106,1) 100%)',
                                transition: 'transform 1s cubic-bezier(0.4, 0, 0.2, 1)'
                              }
                            }}
                          />
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              position: 'absolute', 
                              right: 0, 
                              top: -18, 
                              fontWeight: 'bold',
                              color: 'success.main'
                            }}
                          >
                            {systemStatus.wasteTracking.value}%
                          </Typography>
                        </Box>
                        <Typography
                          variant="body1"
                          sx={{ 
                            color: 'success.main', 
                            fontWeight: 'bold',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: 1,
                            mt: 1.5,
                            p: 1,
                            borderRadius: 2,
                            bgcolor: alpha(theme.palette.success.main, 0.1),
                          }}
                        >
                          <CheckCircleIcon 
                            fontSize="small" 
                            sx={{ 
                              animation: 'pulse 2s infinite',
                              '@keyframes pulse': {
                                '0%': { opacity: 0.7 },
                                '50%': { opacity: 1 },
                                '100%': { opacity: 0.7 },
                              }
                            }} 
                          />
                          Operational
                        </Typography>
                      </Paper>
                    </Fade>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Fade in={true} timeout={1200}>
                      <Paper 
                        elevation={0}
                        sx={{ 
                          p: 3, 
                          textAlign: 'center',
                          borderRadius: 3,
                          bgcolor: alpha(theme.palette.success.main, 0.05),
                          border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
                          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                          '&:hover': {
                            transform: 'translateY(-5px)',
                            boxShadow: `0 10px 20px ${alpha(theme.palette.success.main, 0.2)}`,
                          }
                        }}
                      >
                        <Typography variant="h6" fontWeight={600} gutterBottom>Time Simulation</Typography>
                        <Box sx={{ width: '100%', mb: 1, position: 'relative' }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={systemStatus.timeSimulation.value} 
                            color="success"
                            sx={{ 
                              height: 10, 
                              borderRadius: 5,
                              bgcolor: alpha(theme.palette.success.main, 0.1),
                              '& .MuiLinearProgress-bar': {
                                borderRadius: 5,
                                backgroundImage: 'linear-gradient(90deg, rgba(102,187,106,0.8) 0%, rgba(102,187,106,1) 100%)',
                                transition: 'transform 1s cubic-bezier(0.4, 0, 0.2, 1)'
                              }
                            }}
                          />
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              position: 'absolute', 
                              right: 0, 
                              top: -18, 
                              fontWeight: 'bold',
                              color: 'success.main'
                            }}
                          >
                            {systemStatus.timeSimulation.value}%
                          </Typography>
                        </Box>
                        <Typography
                          variant="body1"
                          sx={{ 
                            color: 'success.main', 
                            fontWeight: 'bold',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: 1,
                            mt: 1.5,
                            p: 1,
                            borderRadius: 2,
                            bgcolor: alpha(theme.palette.success.main, 0.1),
                          }}
                        >
                          <CheckCircleIcon 
                            fontSize="small" 
                            sx={{ 
                              animation: 'pulse 2s infinite',
                              '@keyframes pulse': {
                                '0%': { opacity: 0.7 },
                                '50%': { opacity: 1 },
                                '100%': { opacity: 0.7 },
                              }
                            }} 
                          />
                          Operational
                        </Typography>
                      </Paper>
                    </Fade>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Zoom>
        </Grid>
        
        {/* Additional Information */}
        <Grid item xs={12}>
          <Zoom in={true} style={{ transitionDelay: '400ms' }}>
            <Card 
              sx={{ 
                mt: 2, 
                bgcolor: alpha(theme.palette.info.main, 0.05),
                borderRadius: 3,
                boxShadow: `0 8px 32px ${alpha(theme.palette.info.main, 0.15)}`,
                overflow: 'hidden',
                position: 'relative',
                '&:before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: `radial-gradient(circle at top right, ${alpha(theme.palette.info.main, 0.2)} 0%, transparent 70%)`,
                  zIndex: 0
                }
              }}
            >
              <CardContent sx={{ position: 'relative', zIndex: 1 }}>
                <Box 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 2,
                    flexWrap: { xs: 'wrap', sm: 'nowrap' }
                  }}
                >
                  <Box sx={{ 
                    p: 1.5, 
                    borderRadius: '50%', 
                    bgcolor: alpha(theme.palette.info.main, 0.15),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: `0 4px 12px ${alpha(theme.palette.info.main, 0.3)}`,
                    transform: 'scale(1.2)'
                  }}>
                    <SearchIcon 
                      color="info" 
                      sx={{ 
                        animation: 'pulse 2s infinite',
                        '@keyframes pulse': {
                          '0%': { transform: 'scale(1)' },
                          '50%': { transform: 'scale(1.1)' },
                          '100%': { transform: 'scale(1)' },
                        }
                      }} 
                    />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography 
                      variant="h6" 
                      color="info.main" 
                      fontWeight={600}
                      sx={{ 
                        textShadow: `0 2px 4px ${alpha(theme.palette.info.main, 0.3)}`,
                        mb: 0.5
                      }}
                    >
                      Need to find something quickly?
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ opacity: 0.9 }}>
                      Use the advanced search feature to locate any item in the space station
                    </Typography>
                  </Box>
                  <Box sx={{ ml: { xs: 0, sm: 'auto' }, mt: { xs: 2, sm: 0 }, width: { xs: '100%', sm: 'auto' } }}>
                    <Button 
                      component={Link} 
                      to="/search" 
                      variant="contained" 
                      color="info"
                      startIcon={<SearchIcon />}
                      sx={{ 
                        borderRadius: 2,
                        px: 3,
                        py: 1,
                        boxShadow: `0 4px 14px ${alpha(theme.palette.info.main, 0.4)}`,
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          transform: 'translateY(-3px)',
                          boxShadow: `0 6px 20px ${alpha(theme.palette.info.main, 0.6)}`,
                        },
                        '&:active': {
                          transform: 'translateY(1px)'
                        }
                      }}
                    >
                      Go to Search
                    </Button>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Zoom>
        </Grid>
      </Grid>
    </Box>
  )
}
