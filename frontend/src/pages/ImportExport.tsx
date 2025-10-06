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
  Typography,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  CloudDownload as DownloadIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
} from '@mui/icons-material'
import { api } from '../services/api'

export default function ImportExport() {
  const [loading, setLoading] = useState(false)
  const [itemsFile, setItemsFile] = useState<File | null>(null)
  const [containersFile, setContainersFile] = useState<File | null>(null)
  const [importResults, setImportResults] = useState<{
    type: 'items' | 'containers';
    success: boolean;
    count: number;
    errors: { row: number; message: string }[];
    placements?: any[];
  } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [exportSuccess, setExportSuccess] = useState(false)

  const handleItemsFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setItemsFile(event.target.files[0])
    }
  }

  const handleContainersFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setContainersFile(event.target.files[0])
    }
  }

  const handleImportItems = async () => {
    if (!itemsFile) {
      setError('Please select an items CSV file')
      return
    }

    if (!itemsFile.name.endsWith('.csv')) {
      setError('File must be a CSV')
      return
    }

    setLoading(true)
    setError(null)
    setImportResults(null)

    try {
      const response = await api.importItems(itemsFile)

      setImportResults({
        type: 'items',
        success: response.success,
        count: response.itemsImported,
        errors: response.errors,
        placements: response.placements || [],
      })
    } catch (err) {
      console.error('Error importing items:', err)
      setError('Failed to import items. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleImportContainers = async () => {
    if (!containersFile) {
      setError('Please select a containers CSV file')
      return
    }

    if (!containersFile.name.endsWith('.csv')) {
      setError('File must be a CSV')
      return
    }

    setLoading(true)
    setError(null)
    setImportResults(null)

    try {
      const response = await api.importContainers(containersFile)

      setImportResults({
        type: 'containers',
        success: response.success,
        count: response.containersImported,
        errors: response.errors,
      })
    } catch (err) {
      console.error('Error importing containers:', err)
      setError('Failed to import containers. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleExportArrangement = async () => {
    setLoading(true)
    setError(null)
    setExportSuccess(false)

    try {
      await api.exportArrangement()
      setExportSuccess(true)
    } catch (err) {
      console.error('Error exporting arrangement:', err)
      setError('Failed to export arrangement. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Import & Export
      </Typography>

      {error && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.dark' }}>
          <Typography color="error.contrastText">{error}</Typography>
        </Paper>
      )}

      {exportSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Arrangement exported successfully! Check your downloads folder.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Import Items */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Import Items
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Upload a CSV file with item data. The file should have the following columns:
                Item ID, Name, Width (cm), Depth (cm), Height (cm), Mass (kg), Priority (1-100), Expiry Date (ISO Format), Usage Limit, Preferred Zone
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 2 }}>
                <input
                  accept=".csv"
                  style={{ display: 'none' }}
                  id="items-file-upload"
                  type="file"
                  onChange={handleItemsFileChange}
                />
                <label htmlFor="items-file-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<UploadIcon />}
                    sx={{ mb: 2 }}
                  >
                    Select Items CSV
                  </Button>
                </label>
                {itemsFile && (
                  <Typography variant="body2">
                    Selected file: {itemsFile.name}
                  </Typography>
                )}
              </Box>

              <Button
                variant="contained"
                color="primary"
                onClick={handleImportItems}
                disabled={loading || !itemsFile}
                fullWidth
              >
                {loading ? <CircularProgress size={24} /> : 'Import Items'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Import Containers */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Import Containers
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Upload a CSV file with container data. The file should have the following columns:
                Container ID, Zone, Width (cm), Depth (cm), Height (cm)
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 2 }}>
                <input
                  accept=".csv"
                  style={{ display: 'none' }}
                  id="containers-file-upload"
                  type="file"
                  onChange={handleContainersFileChange}
                />
                <label htmlFor="containers-file-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<UploadIcon />}
                    sx={{ mb: 2 }}
                  >
                    Select Containers CSV
                  </Button>
                </label>
                {containersFile && (
                  <Typography variant="body2">
                    Selected file: {containersFile.name}
                  </Typography>
                )}
              </Box>

              <Button
                variant="contained"
                color="primary"
                onClick={handleImportContainers}
                disabled={loading || !containersFile}
                fullWidth
              >
                {loading ? <CircularProgress size={24} /> : 'Import Containers'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Export Arrangement */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Export Current Arrangement
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Export the current arrangement of items in containers to a CSV file.
              </Typography>

              <Button
                variant="contained"
                color="secondary"
                onClick={handleExportArrangement}
                disabled={loading}
                startIcon={<DownloadIcon />}
                fullWidth
              >
                {loading ? <CircularProgress size={24} /> : 'Export Arrangement'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Import Results */}
        {importResults && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Import Results
                </Typography>

                <Alert severity={importResults.success ? 'success' : 'warning'} sx={{ mb: 2 }}>
                  {importResults.success
                    ? `Successfully imported ${importResults.count} ${importResults.type}.`
                    : `Imported ${importResults.count} ${importResults.type} with some errors.`}
                </Alert>

                {importResults.errors.length > 0 && (
                  <>
                    <Typography variant="subtitle1" gutterBottom>
                      Errors:
                    </Typography>
                    <List>
                      {importResults.errors.map((error, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <ErrorIcon color="error" />
                          </ListItemIcon>
                          <ListItemText
                            primary={`Row ${error.row}: ${error.message}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}

                {importResults.type === 'items' && importResults.placements && importResults.placements.length > 0 && (
                  <>
                    <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                      Automatic Placements:
                    </Typography>
                    <Alert severity="success" sx={{ mb: 2 }}>
                      Successfully placed {importResults.placements.length} items in containers.
                    </Alert>
                    <List>
                      {importResults.placements.map((placement, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <SuccessIcon color="success" />
                          </ListItemIcon>
                          <ListItemText
                            primary={`Item ${placement.itemId} placed in container ${placement.containerId}`}
                            secondary={`Position: (${placement.position.startCoordinates.width}, ${placement.position.startCoordinates.depth}, ${placement.position.startCoordinates.height})`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  )
}
