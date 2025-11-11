import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Paper,
  Typography,
  Box,
  Button,
  Grid,
  Chip,
  Card,
  CardContent,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  ArrowBack,
  CheckCircle,
  Cancel,
  Receipt,
} from '@mui/icons-material';
import { claimService, remittanceService } from '../services/api';

function ClaimDetail() {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [adjudicateDialog, setAdjudicateDialog] = useState(false);
  const [adjudicateData, setAdjudicateData] = useState({
    approve: true,
    paid_amount: '',
    denial_reason: '',
  });
  const [remittance, setRemittance] = useState(null);
  const [remittanceDialog, setRemittanceDialog] = useState(false);

  useEffect(() => {
    loadClaim();
  }, [claimId]);

  const loadClaim = async () => {
    setLoading(true);
    try {
      const data = await claimService.getClaim(claimId);
      setClaim(data);
    } catch (error) {
      console.error('Error loading claim:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAdjudicate = async () => {
    try {
      const data = {
        approve: adjudicateData.approve,
        paid_amount: adjudicateData.paid_amount ? parseFloat(adjudicateData.paid_amount) : null,
        denial_reason: adjudicateData.denial_reason || null,
      };

      await claimService.adjudicateClaim(claimId, data);
      setAdjudicateDialog(false);
      loadClaim();
    } catch (error) {
      console.error('Error adjudicating claim:', error);
      alert('Failed to adjudicate claim');
    }
  };

  const loadRemittance = async () => {
    try {
      const data = await remittanceService.getRemittance(claimId);
      setRemittance(data);
      setRemittanceDialog(true);
    } catch (error) {
      console.error('Error loading remittance:', error);
      alert('Failed to load remittance. Claim may not be adjudicated yet.');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!claim) {
    return <Alert severity="error">Claim not found</Alert>;
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={3}>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/claims')}>
          Back to Claims
        </Button>
      </Box>

      <Typography variant="h4" gutterBottom>
        Claim Details: {claim.claim_id}
      </Typography>

      {/* Status and Actions */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Chip label={claim.status} color="primary" size="large" />
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              Type: {claim.claim_type}
            </Typography>
          </Box>
          <Box>
            {claim.status === 'VALIDATED' && (
              <Button
                variant="contained"
                color="success"
                startIcon={<CheckCircle />}
                onClick={() => {
                  setAdjudicateData({ approve: true, paid_amount: '', denial_reason: '' });
                  setAdjudicateDialog(true);
                }}
                sx={{ mr: 1 }}
              >
                Adjudicate
              </Button>
            )}
            {(claim.status === 'ADJUDICATED' || claim.status === 'PAID') && (
              <Button
                variant="outlined"
                startIcon={<Receipt />}
                onClick={loadRemittance}
              >
                View Remittance
              </Button>
            )}
          </Box>
        </Box>
      </Paper>

      <Grid container spacing={3}>
        {/* Patient Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Patient Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography><strong>Name:</strong> {claim.patient_name}</Typography>
              <Typography><strong>ID:</strong> {claim.patient_id}</Typography>
              <Typography><strong>DOB:</strong> {claim.patient_dob || 'N/A'}</Typography>
              <Typography><strong>Gender:</strong> {claim.patient_gender || 'N/A'}</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Provider Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Provider Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography><strong>Name:</strong> {claim.provider_name}</Typography>
              <Typography><strong>ID:</strong> {claim.provider_id}</Typography>
              <Typography><strong>NPI:</strong> {claim.provider_npi || 'N/A'}</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Financial Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Typography color="textSecondary">Total Charges</Typography>
                  <Typography variant="h5">${claim.total_charges?.toFixed(2) || '0.00'}</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography color="textSecondary">Allowed Amount</Typography>
                  <Typography variant="h5">${claim.allowed_amount?.toFixed(2) || '0.00'}</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography color="textSecondary">Paid Amount</Typography>
                  <Typography variant="h5" color="success.main">
                    ${claim.paid_amount?.toFixed(2) || '0.00'}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Service Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Service Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography><strong>Service Date:</strong> {claim.service_date || 'N/A'}</Typography>
              {claim.admission_date && (
                <Typography><strong>Admission Date:</strong> {claim.admission_date}</Typography>
              )}
              {claim.discharge_date && (
                <Typography><strong>Discharge Date:</strong> {claim.discharge_date}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Diagnosis Codes */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Diagnosis Codes
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box display="flex" flexWrap="wrap" gap={1}>
                {claim.diagnosis_codes && claim.diagnosis_codes.length > 0 ? (
                  claim.diagnosis_codes.map((code, index) => (
                    <Chip key={index} label={code} />
                  ))
                ) : (
                  <Typography color="textSecondary">No diagnosis codes</Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Procedure Codes */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Procedure Codes
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box display="flex" flexWrap="wrap" gap={1}>
                {claim.procedure_codes && claim.procedure_codes.length > 0 ? (
                  claim.procedure_codes.map((code, index) => (
                    <Chip key={index} label={code} color="primary" variant="outlined" />
                  ))
                ) : (
                  <Typography color="textSecondary">No procedure codes</Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Service Lines */}
        {claim.service_lines && claim.service_lines.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Service Lines
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Line #</TableCell>
                        <TableCell>Procedure Code</TableCell>
                        <TableCell>Service Date</TableCell>
                        <TableCell align="right">Units</TableCell>
                        <TableCell align="right">Charge</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {claim.service_lines.map((line, index) => (
                        <TableRow key={index}>
                          <TableCell>{line.line_number}</TableCell>
                          <TableCell>{line.procedure_code}</TableCell>
                          <TableCell>{line.service_date || 'N/A'}</TableCell>
                          <TableCell align="right">{line.units}</TableCell>
                          <TableCell align="right">${line.charge_amount?.toFixed(2)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Adjudication Dialog */}
      <Dialog open={adjudicateDialog} onClose={() => setAdjudicateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Adjudicate Claim</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              select
              fullWidth
              label="Decision"
              value={adjudicateData.approve}
              onChange={(e) => setAdjudicateData({ ...adjudicateData, approve: e.target.value === 'true' })}
              sx={{ mb: 2 }}
              SelectProps={{ native: true }}
            >
              <option value="true">Approve</option>
              <option value="false">Deny</option>
            </TextField>

            {adjudicateData.approve ? (
              <TextField
                fullWidth
                type="number"
                label="Paid Amount"
                value={adjudicateData.paid_amount}
                onChange={(e) => setAdjudicateData({ ...adjudicateData, paid_amount: e.target.value })}
                helperText="Leave empty for automatic calculation"
              />
            ) : (
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Denial Reason"
                value={adjudicateData.denial_reason}
                onChange={(e) => setAdjudicateData({ ...adjudicateData, denial_reason: e.target.value })}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAdjudicateDialog(false)}>Cancel</Button>
          <Button onClick={handleAdjudicate} variant="contained" color="primary">
            Submit
          </Button>
        </DialogActions>
      </Dialog>

      {/* Remittance Dialog */}
      <Dialog open={remittanceDialog} onClose={() => setRemittanceDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Remittance Advice (835)</DialogTitle>
        <DialogContent>
          {remittance && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography><strong>Remittance ID:</strong> {remittance.payment_info?.remittance_id}</Typography>
                  <Typography><strong>Check Number:</strong> {remittance.payment_info?.check_number}</Typography>
                  <Typography><strong>Payment Date:</strong> {remittance.payment_info?.payment_date}</Typography>
                  <Typography><strong>Payment Method:</strong> {remittance.payment_info?.payment_method}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography><strong>Total Billed:</strong> ${remittance.total_billed?.toFixed(2)}</Typography>
                  <Typography><strong>Total Allowed:</strong> ${remittance.total_allowed?.toFixed(2)}</Typography>
                  <Typography><strong>Total Paid:</strong> ${remittance.total_paid?.toFixed(2)}</Typography>
                  <Typography><strong>Total Adjustments:</strong> ${remittance.total_adjustments?.toFixed(2)}</Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>Adjustment Details</Typography>
              {remittance.adjustment_details && remittance.adjustment_details.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Group Code</TableCell>
                        <TableCell>Reason Code</TableCell>
                        <TableCell align="right">Amount</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {remittance.adjustment_details.map((adj, index) => (
                        <TableRow key={index}>
                          <TableCell>{adj.group_code}</TableCell>
                          <TableCell>{adj.reason_code}</TableCell>
                          <TableCell align="right">${adj.amount?.toFixed(2)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography color="textSecondary">No adjustments</Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemittanceDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ClaimDetail;
