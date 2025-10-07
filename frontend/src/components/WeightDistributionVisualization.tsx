import React, { useRef, useState, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Text, Sphere } from '@react-three/drei'
import { Box, Typography, Paper, LinearProgress, CircularProgress } from '@mui/material'
import { Container, Item, Position } from '../services/api'

interface WeightDistributionVisualizationProps {
  containerId: string
  centerOfMass: {
    x: number
    y: number
    z: number
  }
  stabilityScore: number
}

// Color palette for stability score
const getStabilityColor = (score: number) => {
  if (score >= 0.85) return 'green'
  if (score >= 0.7) return 'orange'
  return 'red'
}

// Container mesh component
const ContainerMesh: React.FC<{ container: Container }> = ({ container }) => {
  return (
    <mesh position={[0, 0, 0]}>
      <boxGeometry args={[container.width, container.height, container.depth]} />
      <meshStandardMaterial color="#444444" transparent opacity={0.2} wireframe />
    </mesh>
  )
}

// Item mesh component with weight visualization
const ItemMesh: React.FC<{
  item: Item
  position: Position
}> = ({ item, position }) => {
  // Calculate center position
  const width = position.endCoordinates.width - position.startCoordinates.width
  const height = position.endCoordinates.height - position.startCoordinates.height
  const depth = position.endCoordinates.depth - position.startCoordinates.depth
  
  const posX = position.startCoordinates.width + width / 2
  const posY = position.startCoordinates.height + height / 2
  const posZ = position.startCoordinates.depth + depth / 2
  
  // Color based on mass (darker = heavier)
  const massColor = `hsl(220, 70%, ${Math.max(30, 80 - (item.mass / 30) * 50)}%)`
  
  return (
    <mesh position={[posX, posY, posZ]}>
      <boxGeometry args={[width, height, depth]} />
      <meshStandardMaterial 
        color={massColor} 
        transparent 
        opacity={0.8} 
      />
      <Text
        position={[0, height / 2 + 2, 0]}
        color="white"
        fontSize={1.5}
        anchorX="center"
        anchorY="middle"
        scale={[0.5, 0.5, 0.5]}
      >
        {item.mass.toFixed(1)}kg
      </Text>
    </mesh>
  )
}

// Center of mass visualization
const CenterOfMassMesh: React.FC<{
  position: [number, number, number]
  stabilityScore: number
}> = ({ position, stabilityScore }) => {
  const sphereRef = useRef<THREE.Mesh>(null)
  const color = getStabilityColor(stabilityScore)
  
  useFrame(({ clock }) => {
    if (sphereRef.current) {
      // Pulsating effect
      sphereRef.current.scale.setScalar(1 + Math.sin(clock.getElapsedTime() * 2) * 0.1)
    }
  })
  
  return (
    <group position={position}>
      <Sphere ref={sphereRef} args={[3, 32, 32]}>
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
      </Sphere>
      <Text
        position={[0, 5, 0]}
        color="white"
        fontSize={2}
        anchorX="center"
        anchorY="middle"
        scale={[0.5, 0.5, 0.5]}
      >
        Center of Mass
      </Text>
    </group>
  )
}

// Camera controller
const CameraController = () => {
  const { camera, gl } = useThree()
  const controlsRef = useRef<any>()
  
  useFrame(() => {
    controlsRef.current.update()
  })
  
  return <OrbitControls ref={controlsRef} args={[camera, gl.domElement]} />
}

const WeightDistributionVisualization: React.FC<WeightDistributionVisualizationProps> = ({
  containerId,
  centerOfMass,
  stabilityScore,
}) => {
  const [loading, setLoading] = useState(true)
  const [container, setContainer] = useState<Container | null>(null)
  const [items, setItems] = useState<{ item: Item; position: Position }[]>([])
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      
      try {
        // Fetch container data
        const API_BASE = (import.meta as any).env?.VITE_API_BASE || ''
        const containerResponse = await fetch(`${API_BASE}/api/containers/${containerId}`)
        if (!containerResponse.ok) {
          throw new Error('Failed to fetch container data')
        }
        const containerData = await containerResponse.json()
        setContainer(containerData)
        
        // Fetch items in this container
        const itemsResponse = await fetch(`${API_BASE}/api/containers/${containerId}/items`)
        if (!itemsResponse.ok) {
          throw new Error('Failed to fetch items data')
        }
        const itemsData = await itemsResponse.json()
        
        // Map items to include position
        const itemsWithPosition = itemsData.items.map((item: any) => ({
          item,
          position: {
            startCoordinates: {
              width: item.position_width,
              depth: item.position_depth,
              height: item.position_height,
            },
            endCoordinates: {
              width: item.position_width + item.width,
              depth: item.position_depth + item.depth,
              height: item.position_height + item.height,
            },
          },
        }))
        
        setItems(itemsWithPosition)
      } catch (err) {
        console.error('Error fetching data for visualization:', err)
        setError('Failed to load container visualization data')
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
  }, [containerId])
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    )
  }
  
  if (error || !container) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="error">
          {error || 'Failed to load container data'}
        </Typography>
      </Paper>
    )
  }
  
  // Calculate camera position based on container size
  const cameraDistance = Math.max(container.width, container.height, container.depth) * 1.5
  
  return (
    <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Weight Distribution Visualization - {container.containerId}
      </Typography>
      <Typography variant="body2" gutterBottom>
        Container Zone: {container.zone} | 
        Dimensions: {container.width}x{container.depth}x{container.height} cm
      </Typography>
      
      <Box sx={{ height: 500, width: '100%' }}>
        <Canvas camera={{ position: [cameraDistance, cameraDistance, cameraDistance], fov: 50 }}>
          <CameraController />
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          
          {/* Container */}
          <ContainerMesh container={container} />
          
          {/* Items */}
          {items.map((itemData, index) => (
            <ItemMesh
              key={index}
              item={itemData.item}
              position={itemData.position}
            />
          ))}
          
          {/* Center of Mass */}
          <CenterOfMassMesh 
            position={[centerOfMass.x, centerOfMass.z, centerOfMass.y]} 
            stabilityScore={stabilityScore} 
          />
          
          {/* Helpers */}
          <gridHelper args={[container.width * 2, 10]} />
          <axesHelper args={[Math.max(container.width, container.height, container.depth)]} />
        </Canvas>
      </Box>
      
      <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
        <Typography variant="body2" sx={{ mr: 2 }}>
          Stability:
        </Typography>
        <LinearProgress
          variant="determinate"
          value={stabilityScore * 100}
          color={
            stabilityScore >= 0.85
              ? 'success'
              : stabilityScore >= 0.7
              ? 'warning'
              : 'error'
          }
          sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
        />
      </Box>
      
      <Typography variant="body2" sx={{ mt: 1, textAlign: 'center', fontStyle: 'italic' }}>
        Darker items have higher mass. The colored sphere shows the center of mass.
      </Typography>
    </Paper>
  )
}

export default WeightDistributionVisualization 