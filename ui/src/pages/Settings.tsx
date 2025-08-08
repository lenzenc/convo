import React from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Switch,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

export const Settings: React.FC = () => {
  const [autoRefresh, setAutoRefresh] = React.useState(true);
  const [refreshInterval, setRefreshInterval] = React.useState(30);
  const [debugMode, setDebugMode] = React.useState(false);

  const handleSave = () => {
    // Save settings logic here
    console.log('Settings saved');
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure application preferences and system settings
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* General Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                General Settings
              </Typography>
              
              <List>
                <ListItem>
                  <ListItemText
                    primary="Auto Refresh Dashboard"
                    secondary="Automatically refresh dashboard data"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      edge="end"
                      checked={autoRefresh}
                      onChange={(e) => setAutoRefresh(e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem>
                  <ListItemText
                    primary="Debug Mode"
                    secondary="Show SQL queries and additional debug information"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      edge="end"
                      checked={debugMode}
                      onChange={(e) => setDebugMode(e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              <TextField
                fullWidth
                label="Refresh Interval (seconds)"
                type="number"
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                sx={{ mb: 2 }}
                inputProps={{ min: 5, max: 300 }}
              />

              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                fullWidth
              >
                Save Settings
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* API Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Configuration
              </Typography>
              
              <TextField
                fullWidth
                label="API Base URL"
                value="http://localhost:8000"
                sx={{ mb: 2 }}
                disabled
              />

              <TextField
                fullWidth
                label="Request Timeout (ms)"
                type="number"
                value={30000}
                sx={{ mb: 2 }}
                inputProps={{ min: 1000, max: 60000 }}
              />

              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  sx={{ flex: 1 }}
                >
                  Test Connection
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DeleteIcon />}
                  color="error"
                  sx={{ flex: 1 }}
                >
                  Clear Cache
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Display Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Display Settings
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Rows per page"
                    type="number"
                    value={25}
                    inputProps={{ min: 10, max: 1000 }}
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Date format"
                    value="MMM dd, yyyy HH:mm:ss"
                    helperText="Format for displaying dates and times"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Number format"
                    value="en-US"
                    helperText="Locale for number formatting"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Chart height (px)"
                    type="number"
                    value={300}
                    inputProps={{ min: 200, max: 800 }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};