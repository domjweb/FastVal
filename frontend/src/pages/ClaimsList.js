import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Paper,
  Typography,
  Box,
  Button,
  TextField,
  MenuItem,
  CircularProgress,
  Chip,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { Add, Refresh } from '@mui/icons-material';
import { claimService } from '../services/api';

const statusColors = {
  RECEIVED: 'default',
  VALIDATED: 'info',
  PROCESSING: 'warning',
  ADJUDICATED: 'success',
  PAID: 'success',
  DENIED: 'error',
  PENDING: 'warning',
};

function ClaimsList() {
  const navigate = useNavigate();
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: '',
    patient_id: '',
    provider_id: '',
  });

  useEffect(() => {
    loadClaims();
  }, [filters]);

  const loadClaims = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.patient_id) params.patient_id = filters.patient_id;
      if (filters.provider_id) params.provider_id = filters.provider_id;

      const response = await claimService.getClaims(params);
      setClaims(response.claims || []);
    } catch (error) {
      console.error('Error loading claims:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
  };

  const columns = [
    {
      field: 'claim_id',
      headerName: 'Claim ID',
      width: 150,
      renderCell: (params) => (
        <Button
          variant="text"
          onClick={() => navigate(`/claims/${params.value}`)}
        >
          {params.value}
        </Button>
      ),
    },
    {
      field: 'claim_type',
      headerName: 'Type',
      width: 100,
    },
    {
      field: 'patient_name',
      headerName: 'Patient',
      width: 180,
    },
    {
      field: 'provider_name',
      headerName: 'Provider',
      width: 200,
    },
    {
      field: 'service_date',
      headerName: 'Service Date',
      width: 120,
    },
    {
      field: 'total_charges',
      headerName: 'Charges',
      width: 120,
      renderCell: (params) => `$${params.value?.toFixed(2) || '0.00'}`,
    },
    {
      field: 'paid_amount',
      headerName: 'Paid',
      width: 120,
      renderCell: (params) => `$${params.value?.toFixed(2) || '0.00'}`,
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={statusColors[params.value] || 'default'}
          size="small"
        />
      ),
    },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Claims</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadClaims}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => navigate('/upload')}
          >
            Upload Claim
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Filters
        </Typography>
        <Box display="flex" gap={2}>
          <TextField
            select
            label="Status"
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="RECEIVED">Received</MenuItem>
            <MenuItem value="VALIDATED">Validated</MenuItem>
            <MenuItem value="PROCESSING">Processing</MenuItem>
            <MenuItem value="ADJUDICATED">Adjudicated</MenuItem>
            <MenuItem value="PAID">Paid</MenuItem>
            <MenuItem value="DENIED">Denied</MenuItem>
            <MenuItem value="PENDING">Pending</MenuItem>
          </TextField>
          <TextField
            label="Patient ID"
            value={filters.patient_id}
            onChange={(e) => handleFilterChange('patient_id', e.target.value)}
            sx={{ minWidth: 200 }}
          />
          <TextField
            label="Provider ID"
            value={filters.provider_id}
            onChange={(e) => handleFilterChange('provider_id', e.target.value)}
            sx={{ minWidth: 200 }}
          />
        </Box>
      </Paper>

      {/* Claims Table */}
      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={claims}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10, 25, 50]}
          loading={loading}
          disableSelectionOnClick
        />
      </Paper>
    </Box>
  );
}

export default ClaimsList;
