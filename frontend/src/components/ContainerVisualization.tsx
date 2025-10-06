import React, { useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Text, TransformControls, Html } from '@react-three/drei'
import { Box, Typography, Paper, Chip, IconButton, Tooltip } from '@mui/material'
import ZoomInIcon from '@mui/icons-material/ZoomIn'
import ZoomOutIcon from '@mui/icons-material/ZoomOut'
import CenterFocusStrongIcon from '@mui/icons-material/CenterFocusStrong'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import { Container, Item, Position } from '../services/api'

interface ContainerVisualizationProps {
  container: Container
  items: {
    item: Item
    position: Position
  }[]
  highlightedItemId?: string
}

// Color palette for items based on priority
const getPriorityColor = (priority: number) => {
  if (priority >= 90) return 'red'
  if (priority >= 70) return 'orange'
  if (priority >= 50) return 'yellow'
  if (priority >= 30) return 'green'
  return 'blue'
}

// Container mesh component
const ContainerMesh: React.FC<{ 
  container: Container, 
  showWireframe: boolean 
}> = ({ container, showWireframe }) => {
  return (
    <mesh position={[0, 0, 0]}>
      <boxGeometry args={[container.width, container.height, container.depth]} />
      <meshStandardMaterial 
        color="#444444" 
        transparent 
        opacity={showWireframe ? 0.1 : 0.3} 
        wireframe={showWireframe} 
      />
    </mesh>
  )
}

// Item mesh component
const ItemMesh: React.FC<{
  item: Item
  position: Position
  isHighlighted: boolean
  showLabels: boolean
  onClick: () => void
}> = ({ item, position, isHighlighted, showLabels, onClick }) => {
  // Calculate center position
  const width = position.endCoordinates.width - position.startCoordinates.width
  const height = position.endCoordinates.height - position.startCoordinates.height
  const depth = position.endCoordinates.depth - position.startCoordinates.depth
  
  const posX = position.startCoordinates.width + width / 2
  const posY = position.startCoordinates.height + height / 2
  const posZ = position.startCoordinates.depth + depth / 2
  
  // Get color based on priority
  const color = getPriorityColor(item.priority)
  
  // Pulse effect for highlighted items
  const meshRef = useRef<THREE.Mesh>(null)
  
  useFrame(({ clock }) => {
    if (isHighlighted && meshRef.current) {
      meshRef.current.scale.x = 1 + Math.sin(clock.getElapsedTime() * 3) * 0.05
      meshRef.current.scale.y = 1 + Math.sin(clock.getElapsedTime() * 3) * 0.05
      meshRef.current.scale.z = 1 + Math.sin(clock.getElapsedTime() * 3) * 0.05
    }
  })
  
  return (
    <mesh 
      ref={meshRef} 
      position={[posX, posY, posZ]} 
      onClick={(e) => {
        e.stopPropagation()
        onClick()
      }}
    >
      <boxGeometry args={[width, height, depth]} />
      <meshStandardMaterial 
        color={color} 
        transparent 
        opacity={isHighlighted ? 0.9 : 0.7} 
        emissive={isHighlighted ? color : undefined}
        emissiveIntensity={isHighlighted ? 0.5 : 0}
      />
      {(isHighlighted || showLabels) && (
        <Html position={[0, height / 2 + 2, 0]} center>
          <div style={{ 
            backgroundColor: 'rgba(0,0,0,0.7)', 
            color: 'white', 
            padding: '4px 8px', 
            borderRadius: '4px',
            fontSize: isHighlighted ? '14px' : '10px',
            fontWeight: isHighlighted ? 'bold' : 'normal',
            pointerEvents: 'none',
            whiteSpace: 'nowrap'
          }}>
            {item.name} ({item.priority})
            {isHighlighted && (
              <div style={{ fontSize: '10px' }}>
                {item.mass}kg | {item.preferredZone}
              </div>
            )}
          </div>
        </Html>
      )}
    </mesh>
  )
}

// Camera controller
const CameraController: React.FC<{
  resetView: boolean
  onResetComplete: () => void
}> = ({ resetView, onResetComplete }) => {
  const { camera, gl } = useThree()
  const controlsRef = useRef<any>()
  
  useFrame(() => {
    controlsRef.current.update()
    
    if (resetView) {
      controlsRef.current.reset()
      onResetComplete()
    }
  })
  
  return <OrbitControls ref={controlsRef} args={[camera, gl.domElement]} />
}

const ContainerVisualization: React.FC<ContainerVisualizationProps> = ({
  container,
  items,
  highlightedItemId,
}) => {
  // State for visualization controls
  const [showWireframe, setShowWireframe] = useState(false)
  const [showLabels, setShowLabels] = useState(false)
  const [resetView, setResetView] = useState(false)
  const [selectedItemId, setSelectedItemId] = useState<string | undefined>(highlightedItemId)
  
  // Calculate camera position based on container size
  const cameraDistance = Math.max(container.width, container.height, container.depth) * 1.5
  
  const handleItemClick = (itemId: string) => {
    setSelectedItemId(itemId === selectedItemId ? undefined : itemId)
  }
  
  const handleResetView = () => {
    setResetView(true)
  }
  
  const handleResetComplete = () => {
    setResetView(false)
  }
  
  return (
    <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Container: {container.containerId} ({container.zone})
        </Typography>
        <Box>
          <Tooltip title="Toggle wireframe">
            <IconButton onClick={() => setShowWireframe(!showWireframe)} size="small">
              {showWireframe ? <VisibilityOffIcon /> : <VisibilityIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Toggle labels">
            <IconButton onClick={() => setShowLabels(!showLabels)} size="small">
              {showLabels ? <VisibilityOffIcon /> : <VisibilityIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Reset view">
            <IconButton onClick={handleResetView} size="small">
              <CenterFocusStrongIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      <Typography variant="body2" gutterBottom>
        Dimensions: {container.width}x{container.depth}x{container.height} cm | Items: {items.length}
      </Typography>
      
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
        {Array.from(new Set(items.map(i => i.item.preferredZone))).map(zone => (
          <Chip 
            key={zone} 
            label={zone} 
            color="primary" 
            variant="outlined" 
            size="small" 
          />
        ))}
      </Box>
      
      <Box sx={{ height: 400, width: '100%', position: 'relative' }}>
        <Canvas camera={{ position: [cameraDistance, cameraDistance, cameraDistance], fov: 50 }}>
          <CameraController resetView={resetView} onResetComplete={handleResetComplete} />
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <ContainerMesh container={container} showWireframe={showWireframe} />
          {items.map((itemData, index) => (
            <ItemMesh
              key={index}
              item={itemData.item}
              position={itemData.position}
              isHighlighted={itemData.item.itemId === (selectedItemId || highlightedItemId)}
              showLabels={showLabels}
              onClick={() => handleItemClick(itemData.item.itemId)}
            />
          ))}
          <gridHelper args={[container.width * 2, 10]} />
          <axesHelper args={[Math.max(container.width, container.height, container.depth)]} />
        </Canvas>
        
        <Box sx={{ 
          position: 'absolute', 
          bottom: 10, 
          right: 10, 
          bgcolor: 'rgba(255,255,255,0.7)', 
          p: 1, 
          borderRadius: 1 
        }}>
          <Tooltip title="Zoom in">
            <IconButton 
              onClick={() => {
                const canvas = document.querySelector('canvas')
                if (canvas) {
                  const event = new WheelEvent('wheel', { deltaY: -100 })
                  canvas.dispatchEvent(event)
                }
              }} 
              size="small"
            >
              <ZoomInIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Zoom out">
            <IconButton 
              onClick={() => {
                const canvas = document.querySelector('canvas')
                if (canvas) {
                  const event = new WheelEvent('wheel', { deltaY: 100 })
                  canvas.dispatchEvent(event)
                }
              }} 
              size="small"
            >
              <ZoomOutIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic', textAlign: 'center' }}>
        Click and drag to rotate, scroll to zoom, click on items to select
      </Typography>
    </Paper>
  )
}

export default ContainerVisualization
