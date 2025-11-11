import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Paper,
  Typography,
  Box,
  Button,
  Alert,
  LinearProgress,
} from '@mui/material';
import { CloudUpload, CheckCircle } from '@mui/icons-material';
import { claimService } from '../services/api';

function UploadClaim() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [uploadedClaim, setUploadedClaim] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      // Validate file extension
      const validExtensions = ['.txt', '.x12', '.edi'];
      const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
      
      if (!validExtensions.includes(fileExtension)) {
        setError('Invalid file type. Please upload a .txt, .x12, or .edi file.');
        setFile(null);
        return;
      }

      setFile(selectedFile);
      setError('');
      setSuccess(false);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const claim = await claimService.uploadClaim(file);
      setSuccess(true);
      setUploadedClaim(claim);
      setFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload claim file');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setError('');
    setSuccess(false);
    setUploadedClaim(null);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload Claim File
      </Typography>

      <Paper sx={{ p: 4, maxWidth: 600, mx: 'auto' }}>
        {!success ? (
          <>
            <Box
              sx={{
                border: '2px dashed #ccc',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                mb: 3,
                cursor: 'pointer',
                '&:hover': {
                  borderColor: 'primary.main',
                  backgroundColor: 'action.hover',
                },
              }}
              onClick={() => document.getElementById('file-input').click()}
            >
              <CloudUpload sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Drop X12 837 file here or click to browse
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Supported formats: .txt, .x12, .edi
              </Typography>
              <input
                id="file-input"
                type="file"
                accept=".txt,.x12,.edi"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </Box>

            {file && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Selected file: <strong>{file.name}</strong> ({(file.size / 1024).toFixed(2)} KB)
              </Alert>
            )}

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {uploading && (
              <Box sx={{ mb: 2 }}>
                <LinearProgress />
                <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 1 }}>
                  Uploading and parsing claim file...
                </Typography>
              </Box>
            )}

            <Box display="flex" justifyContent="center" gap={2}>
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={!file || uploading}
                startIcon={<CloudUpload />}
              >
                Upload Claim
              </Button>
              <Button
                variant="outlined"
                onClick={handleReset}
                disabled={uploading}
              >
                Reset
              </Button>
            </Box>
          </>
        ) : (
          <Box textAlign="center">
            <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Claim Uploaded Successfully!
            </Typography>
            <Alert severity="success" sx={{ my: 3 }}>
              <Typography><strong>Claim ID:</strong> {uploadedClaim?.claim_id}</Typography>
              <Typography><strong>Type:</strong> {uploadedClaim?.claim_type}</Typography>
              <Typography><strong>Patient:</strong> {uploadedClaim?.patient_name}</Typography>
              <Typography><strong>Status:</strong> {uploadedClaim?.status}</Typography>
            </Alert>
            <Box display="flex" justifyContent="center" gap={2}>
              <Button
                variant="contained"
                onClick={() => navigate(`/claims/${uploadedClaim?.claim_id}`)}
              >
                View Claim Details
              </Button>
              <Button
                variant="outlined"
                onClick={handleReset}
              >
                Upload Another
              </Button>
            </Box>
          </Box>
        )}
      </Paper>

      {/* Information Section */}
      <Paper sx={{ p: 3, mt: 3, maxWidth: 600, mx: 'auto' }}>
        <Typography variant="h6" gutterBottom>
          X12 837 Claim File Information
        </Typography>
        <Typography variant="body2" paragraph>
          Upload X12 837 claim files (institutional or professional) to process healthcare claims.
          The system will automatically:
        </Typography>
        <ul>
          <li>
            <Typography variant="body2">Parse the X12 format and extract claim data</Typography>
          </li>
          <li>
            <Typography variant="body2">Validate patient and provider information</Typography>
          </li>
          <li>
            <Typography variant="body2">Extract diagnosis and procedure codes</Typography>
          </li>
          <li>
            <Typography variant="body2">Calculate total charges from service lines</Typography>
          </li>
          <li>
            <Typography variant="body2">Set initial claim status to RECEIVED</Typography>
          </li>
        </ul>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
          Sample files are available in the <code>sample_files/</code> directory.
        </Typography>
      </Paper>
    </Box>
  );
}

export default UploadClaim;
