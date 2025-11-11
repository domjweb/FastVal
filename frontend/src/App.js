import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Box,
  Button,
} from '@mui/material';
import { LocalHospital } from '@mui/icons-material';

import ClaimsList from './pages/ClaimsList';
import ClaimDetail from './pages/ClaimDetail';
import UploadClaim from './pages/UploadClaim';
import Dashboard from './pages/Dashboard';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <AppBar position="static">
            <Toolbar>
              <LocalHospital sx={{ mr: 2 }} />
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                FastVal - Claims Processing System
              </Typography>
              <Button color="inherit" component={RouterLink} to="/">
                Dashboard
              </Button>
              <Button color="inherit" component={RouterLink} to="/claims">
                Claims
              </Button>
              <Button color="inherit" component={RouterLink} to="/upload">
                Upload
              </Button>
            </Toolbar>
          </AppBar>

          <Container component="main" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/claims" element={<ClaimsList />} />
              <Route path="/claims/:claimId" element={<ClaimDetail />} />
              <Route path="/upload" element={<UploadClaim />} />
            </Routes>
          </Container>

          <Box
            component="footer"
            sx={{
              py: 3,
              px: 2,
              mt: 'auto',
              backgroundColor: (theme) =>
                theme.palette.mode === 'light'
                  ? theme.palette.grey[200]
                  : theme.palette.grey[800],
            }}
          >
            <Container maxWidth="sm">
              <Typography variant="body2" color="text.secondary" align="center">
                FastVal Healthcare Claims Processing System © 2023
              </Typography>
            </Container>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
