import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CardHeader,
  Grid,
  Alert,
  AlertTitle,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  ViewList as ViewListIcon,
  PlayArrow as PlayArrowIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { useAppStore } from '@/stores/appStore';
import { ViewInfo, QueryResponse } from '@/types';
import ApiService from '@/utils/api';
import { formatDateTime, formatNumber } from '@/utils/formatters';

export const Views: React.FC = () => {
  const { views, viewsLoading, viewsError, fetchViews } = useAppStore();
  const [selectedView, setSelectedView] = useState<ViewInfo | null>(null);
  const [viewData, setViewData] = useState<QueryResponse | null>(null);
  const [viewDataLoading, setViewDataLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    fetchViews();
  }, [fetchViews]);

  const handleViewDetails = async (view: ViewInfo) => {
    setSelectedView(view);
    setDialogOpen(true);
    setViewDataLoading(true);
    setViewData(null);

    try {
      const data = await ApiService.executeView(view.view_name, { limit: 100 });
      setViewData(data);
    } catch (error) {
      console.error('Error fetching view data:', error);
    } finally {
      setViewDataLoading(false);
    }
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedView(null);
    setViewData(null);
  };

  const renderViewCard = (view: ViewInfo) => (
    <Card key={view.view_name} sx={{ height: '100%' }}>
      <CardHeader
        avatar={<ViewListIcon color="primary" />}
        title={view.view_name}
        subheader={formatDateTime(view.created_at)}
      />
      <CardContent>
        <Typography variant="body2" color="text.secondary" paragraph>
          {view.description}
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Columns ({view.columns.length}):
          </Typography>
          <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {view.columns.slice(0, 3).map((column) => (
              <Chip
                key={column}
                label={column}
                size="small"
                variant="outlined"
              />
            ))}
            {view.columns.length > 3 && (
              <Chip
                label={`+${view.columns.length - 3} more`}
                size="small"
                variant="outlined"
                color="secondary"
              />
            )}
          </Box>
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            startIcon={<VisibilityIcon />}
            variant="outlined"
            size="small"
            onClick={() => handleViewDetails(view)}
          >
            View Data
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Database Views
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Pre-built views for common analytics queries
        </Typography>
      </Box>

      {viewsError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <AlertTitle>Error</AlertTitle>
          {viewsError}
        </Alert>
      )}

      {viewsLoading ? (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: 200,
          }}
        >
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {views.map((view) => (
            <Grid item xs={12} md={6} lg={4} key={view.view_name}>
              {renderViewCard(view)}
            </Grid>
          ))}
        </Grid>
      )}

      {/* View Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {selectedView?.view_name}
          {viewData && (
            <Typography variant="body2" color="text.secondary">
              {formatNumber(viewData.row_count)} rows • {viewData.execution_time_ms}ms
            </Typography>
          )}
        </DialogTitle>
        
        <DialogContent>
          {viewDataLoading ? (
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: 200,
              }}
            >
              <CircularProgress />
            </Box>
          ) : viewData && viewData.data.length > 0 ? (
            <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    {selectedView?.columns.map((column) => (
                      <TableCell key={column}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {column}
                        </Typography>
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {viewData.data.map((row, index) => (
                    <TableRow key={index} hover>
                      {selectedView?.columns.map((column) => (
                        <TableCell key={column}>
                          {typeof row[column] === 'number'
                            ? formatNumber(row[column])
                            : String(row[column] || '')}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Typography>No data available</Typography>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};