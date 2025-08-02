import React, { useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Alert,
  AlertTitle,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Storage as StorageIcon,
  Cloud as CloudIcon,
} from '@mui/icons-material';
import { useAppStore } from '@/stores/appStore';
import { formatDateTime } from '@/utils/formatters';

export const Health: React.FC = () => {
  const { health, healthLoading, healthError, fetchHealth } = useAppStore();

  useEffect(() => {
    fetchHealth();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
      case 'unhealthy':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return <CheckCircleIcon color="success" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
      case 'unhealthy':
        return <ErrorIcon color="error" />;
      default:
        return <CheckCircleIcon />;
    }
  };

  if (healthLoading && !health) {
    return (
      <Container maxWidth="xl">
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: 400,
          }}
        >
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          System Health
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor the status of system components and services
        </Typography>
      </Box>

      {healthError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <AlertTitle>Health Check Error</AlertTitle>
          {healthError}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Overall Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 2,
                }}
              >
                <Typography variant="h6">Overall Status</Typography>
                {healthLoading && <CircularProgress size={20} />}
              </Box>
              
              {health && (
                <>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getStatusIcon(health.status)}
                    <Typography variant="h5" sx={{ ml: 1, fontWeight: 'bold' }}>
                      {health.status}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary">
                    Last updated: {formatDateTime(health.timestamp)}
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Service Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Service Status
              </Typography>
              
              {health && (
                <List dense>
                  {/* DuckDB Status */}
                  <ListItem>
                    <ListItemIcon>
                      <StorageIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="DuckDB"
                      secondary={health.services.duckdb.version || 'Database engine'}
                    />
                    <Chip
                      label={health.services.duckdb.status}
                      color={getStatusColor(health.services.duckdb.status)}
                      size="small"
                    />
                  </ListItem>

                  {/* S3/MinIO Status */}
                  <ListItem>
                    <ListItemIcon>
                      <CloudIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="S3 Storage"
                      secondary={
                        health.services.s3.bucket_accessible
                          ? 'Bucket accessible'
                          : 'Object storage service'
                      }
                    />
                    <Chip
                      label={health.services.s3.status}
                      color={getStatusColor(health.services.s3.status)}
                      size="small"
                    />
                  </ListItem>
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Health Metrics */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Health Metrics
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="primary.main">
                      99.9%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Uptime
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="success.main">
                      12ms
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg Response Time
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="info.main">
                      2.1GB
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Storage Used
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="warning.main">
                      45%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      CPU Usage
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};