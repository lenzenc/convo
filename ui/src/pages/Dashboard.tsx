import React, { useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Box,
  Alert,
  AlertTitle,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Group as GroupIcon,
  TrendingUp as TrendingUpIcon,
  AccessTime as AccessTimeIcon,
} from '@mui/icons-material';
import { useAppStore } from '@/stores/appStore';
import { MetricCard } from '@/components/Dashboard/MetricCard';
import { DashboardCharts } from '@/components/Dashboard/DashboardCharts';

export const Dashboard: React.FC = () => {
  const {
    dashboardMetrics,
    dashboardLoading,
    dashboardError,
    fetchDashboardMetrics,
  } = useAppStore();

  useEffect(() => {
    fetchDashboardMetrics();
  }, [fetchDashboardMetrics]);

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Overview of conversation analytics and system metrics
        </Typography>
      </Box>

      {dashboardError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <AlertTitle>Error</AlertTitle>
          {dashboardError}
        </Alert>
      )}

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Total Conversations"
            value={dashboardMetrics?.totalConversations || 0}
            subtitle="All time"
            icon={ChatIcon}
            loading={dashboardLoading}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Active Sessions"
            value={dashboardMetrics?.totalSessions || 0}
            subtitle="Unique sessions"
            icon={GroupIcon}
            loading={dashboardLoading}
            color="success"
          />
        </Grid>

        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Avg. Interactions"
            value={dashboardMetrics?.avgInteractionsPerSession || 0}
            subtitle="Per session"
            icon={TrendingUpIcon}
            loading={dashboardLoading}
            color="info"
          />
        </Grid>

        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Response Time"
            value="1.2s"
            subtitle="Average"
            icon={AccessTimeIcon}
            loading={dashboardLoading}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Charts Section */}
      <DashboardCharts metrics={dashboardMetrics} loading={dashboardLoading} />
    </Container>
  );
};