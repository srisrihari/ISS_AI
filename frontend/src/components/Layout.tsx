import { useState, ReactNode, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  AppBar,
  Box,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
  Avatar,
  Tooltip,
  Fade,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  AddBox as PlacementIcon,
  Search as SearchIcon,
  Delete as WasteIcon,
  Timer as SimulationIcon,
  ImportExport as ImportExportIcon,
  History as LogsIcon,
  ViewInAr as VisualizationIcon,
  Inventory as InventoryIcon,
  Warning as EmergencyIcon,
  RocketLaunch as RocketIcon,
} from '@mui/icons-material'

const drawerWidth = 260

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  
  // Close mobile drawer when route changes
  useEffect(() => {
    if (mobileOpen && isMobile) {
      setMobileOpen(false)
    }
  }, [location.pathname, isMobile])

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Placement', icon: <PlacementIcon />, path: '/placement' },
    { text: 'Search & Retrieval', icon: <SearchIcon />, path: '/search' },
    { text: 'Waste Management', icon: <WasteIcon />, path: '/waste' },
    { text: 'Time Simulation', icon: <SimulationIcon />, path: '/simulation' },
    { text: '3D Visualization', icon: <VisualizationIcon />, path: '/visualization' },
    { text: 'Inventory', icon: <InventoryIcon />, path: '/inventory' },
    { text: 'Emergency Protocols', icon: <EmergencyIcon color="error" />, path: '/emergency' },
    { text: 'Import/Export', icon: <ImportExportIcon />, path: '/import-export' },
    { text: 'Logs', icon: <LogsIcon />, path: '/logs' },
  ]

  const drawer = (
    <div>
      <Toolbar sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'flex-start',
        py: 1.5,
      }}>
        <Avatar 
          sx={{ 
            mr: 2, 
            bgcolor: 'primary.main',
            boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
          }}
        >
          <RocketIcon />
        </Avatar>
        <Typography variant="h6" noWrap component="div" fontWeight="bold">
          Space Station Cargo
        </Typography>
      </Toolbar>
      <Divider sx={{ opacity: 0.6 }} />
      <List sx={{ px: 1, py: 1.5 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <Tooltip 
              title={item.text} 
              placement="right" 
              arrow 
              TransitionComponent={Fade}
              TransitionProps={{ timeout: 600 }}
              enterDelay={500}
              enterNextDelay={500}
            >
              <ListItemButton
                component={Link}
                to={item.path}
                selected={location.pathname === item.path}
                sx={{
                  borderRadius: 2,
                  py: 1.2,
                  transition: 'all 0.2s',
                }}
              >
                <ListItemIcon sx={{ 
                  minWidth: 40, 
                  color: location.pathname === item.path ? 'primary.main' : 'inherit',
                  transition: 'all 0.2s',
                }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text} 
                  primaryTypographyProps={{ 
                    fontSize: '0.95rem',
                    fontWeight: location.pathname === item.path ? 500 : 400,
                  }}
                />
              </ListItemButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>
    </div>
  )

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        elevation={3}
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          backdropFilter: 'blur(8px)',
          background: 'linear-gradient(90deg, rgba(26,35,126,0.95) 0%, rgba(40,53,147,0.95) 100%)',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div" fontWeight="500">
              {menuItems.find(item => item.path === location.pathname)?.text || 'Space Station Cargo Management'}
            </Typography>
          </Box>
          
          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary" sx={{ mr: 2 }}>
              ISS Mission Control
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{ 
          flexGrow: 1, 
          p: { xs: 2, sm: 3 }, 
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          transition: 'all 0.3s ease',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Toolbar />
        <Box sx={{ 
          flexGrow: 1, 
          borderRadius: 3,
          overflow: 'hidden',
          animation: 'fadeIn 0.5s ease-in-out',
          '@keyframes fadeIn': {
            '0%': {
              opacity: 0,
              transform: 'translateY(10px)'
            },
            '100%': {
              opacity: 1,
              transform: 'translateY(0)'
            },
          },
        }}>
          {children}
        </Box>
      </Box>
    </Box>
  )
}
