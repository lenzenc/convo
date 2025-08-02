import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Avatar,
} from '@mui/material';
import { SvgIconComponent } from '@mui/icons-material';
import { formatNumber } from '@/utils/formatters';

interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon?: SvgIconComponent;
  loading?: boolean;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  loading = false,
  color = 'primary',
  trend,
}) => {
  const formatValue = (val: number | string): string => {
    if (typeof val === 'number') {
      return formatNumber(val);
    }
    return val;
  };

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'visible',
      }}
    >
      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            mb: 2,
          }}
        >
          <Typography variant="h6" component="div" color="text.secondary">
            {title}
          </Typography>
          {Icon && (
            <Avatar
              sx={{
                bgcolor: `${color}.main`,
                width: 40,
                height: 40,
              }}
            >
              <Icon />
            </Avatar>
          )}
        </Box>

        {loading ? (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 60,
            }}
          >
            <CircularProgress size={24} />
          </Box>
        ) : (
          <>
            <Typography
              variant="h3"
              component="div"
              sx={{
                fontWeight: 'bold',
                color: `${color}.main`,
                mb: 1,
              }}
            >
              {formatValue(value)}
            </Typography>

            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}

            {trend && (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  mt: 1,
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    color: trend.isPositive ? 'success.main' : 'error.main',
                    fontWeight: 'medium',
                  }}
                >
                  {trend.isPositive ? '+' : ''}
                  {trend.value}%
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                  vs last period
                </Typography>
              </Box>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};