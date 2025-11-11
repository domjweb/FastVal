import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material';
import {
  Assessment,
  AttachMoney,
  CheckCircle,
  Cancel,
} from '@mui/icons-material';
import { claimService } from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState({
    total: 0,
    adjudicated: 0,
    paid: 0,
    denied: 0,
    totalCharges: 0,
    totalPaid: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await claimService.getClaims({ limit: 1000 });
      const claims = response.claims || [];

      const stats = {
        total: claims.length,
        adjudicated: claims.filter((c) => c.status === 'ADJUDICATED').length,
        paid: claims.filter((c) => c.status === 'PAID').length,
        denied: claims.filter((c) => c.status === 'DENIED').length,
        totalCharges: claims.reduce((sum, c) => sum + (c.total_charges || 0), 0),
        totalPaid: claims.reduce((sum, c) => sum + (c.paid_amount || 0), 0),
      };

      setStats(stats);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Total Claims */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Total Claims
                  </Typography>
                  <Typography variant="h4">{stats.total}</Typography>
                </Box>
                <Assessment fontSize="large" color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Adjudicated Claims */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Adjudicated
                  </Typography>
                  <Typography variant="h4">{stats.adjudicated}</Typography>
                </Box>
                <CheckCircle fontSize="large" color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Paid Claims */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Paid Claims
                  </Typography>
                  <Typography variant="h4">{stats.paid}</Typography>
                </Box>
                <AttachMoney fontSize="large" color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Denied Claims */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Denied Claims
                  </Typography>
                  <Typography variant="h4">{stats.denied}</Typography>
                </Box>
                <Cancel fontSize="large" color="error" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Financial Summary */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Financial Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography color="textSecondary">Total Charges</Typography>
                <Typography variant="h5">
                  ${stats.totalCharges.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography color="textSecondary">Total Paid</Typography>
                <Typography variant="h5" color="success.main">
                  ${stats.totalPaid.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
