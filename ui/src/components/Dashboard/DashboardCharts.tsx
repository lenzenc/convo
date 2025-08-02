import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  CircularProgress,
  Grid,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts';
import { DashboardMetrics } from '@/types';
import { formatNumber, formatDate } from '@/utils/formatters';

interface DashboardChartsProps {
  metrics: DashboardMetrics | null;
  loading: boolean;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export const DashboardCharts: React.FC<DashboardChartsProps> = ({
  metrics,
  loading,
}) => {
  if (loading) {
    return (
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
    );
  }

  if (!metrics) {
    return (
      <Typography variant="body1" color="text.secondary" align="center">
        No data available
      </Typography>
    );
  }

  const formatTooltipValue = (value: number, name: string) => {
    return [formatNumber(value), name];
  };

  const formatTooltipLabel = (label: string) => {
    return formatDate(label);
  };

  return (
    <Grid container spacing={3}>
      {/* Daily Conversations Trend */}
      <Grid item xs={12} lg={8}>
        <Card>
          <CardHeader title="Daily Conversation Trends" />
          <CardContent>
            <Box sx={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <LineChart data={metrics.dailyStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(value) => formatDate(value)}
                  />
                  <YAxis tickFormatter={(value) => formatNumber(value)} />
                  <Tooltip
                    formatter={formatTooltipValue}
                    labelFormatter={formatTooltipLabel}
                  />
                  <Line
                    type="monotone"
                    dataKey="conversation_count"
                    stroke="#1976d2"
                    strokeWidth={2}
                    dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
                    name="Conversations"
                  />
                  <Line
                    type="monotone"
                    dataKey="session_count"
                    stroke="#dc004e"
                    strokeWidth={2}
                    dot={{ fill: '#dc004e', strokeWidth: 2, r: 4 }}
                    name="Sessions"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Popular Actions Pie Chart */}
      <Grid item xs={12} lg={4}>
        <Card>
          <CardHeader title="Popular Actions" />
          <CardContent>
            <Box sx={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={metrics.topActions}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ action_type, percentage }) =>
                      `${action_type}: ${percentage.toFixed(1)}%`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {metrics.topActions.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number, _name, props) => [
                      formatNumber(value),
                      props.payload.action_type,
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Location Activity (if data available) */}
      {metrics.locationStats.length > 0 && (
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Activity by Location" />
            <CardContent>
              <Box sx={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                  <BarChart data={metrics.locationStats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="location_id" />
                    <YAxis tickFormatter={(value) => formatNumber(value)} />
                    <Tooltip formatter={formatTooltipValue} />
                    <Bar
                      dataKey="conversation_count"
                      fill="#1976d2"
                      name="Conversations"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );
};