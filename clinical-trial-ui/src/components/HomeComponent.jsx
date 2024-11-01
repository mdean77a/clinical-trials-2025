import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid2';
import {
  Container,
  Paper,
  Typography,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  CircularProgress,
  Snackbar,
  Alert
} from '@mui/material';
import {
  CloudUpload,
  Description,
  CheckCircle,
  Refresh
} from '@mui/icons-material';

function HomeComponent({ onFilesSelected, onFormOptionSelected }) {
  const [option, setOption] = useState('');
  const [files, setFiles] = useState([]);
  const [existingFiles, setExistingFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [selectedFormOption, setSelectedFormOption] = useState('');
  const [showFormSelection, setShowFormSelection] = useState(false);
  const [showNotification, setShowNotification] = useState(false);

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    if (option === 'Use Existing Files') {
      fetchExistingFiles();
    }
  }, [option]);

  const fetchExistingFiles = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/existing-files`);
      const data = await response.json();
      setExistingFiles(data.files);
    } catch (error) {
      console.error('Error fetching existing files:', error);
    }
  };

  const handleFileUpload = async () => {
    if (files.length === 0) {
      alert('Please select files to upload.');
      return;
    }

    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    setIsProcessing(true);

    try {
      const response = await fetch(`${BACKEND_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      alert('Files uploaded successfully. Please select "Use Existing Files" to proceed.');
      setOption('');
    } catch (error) {
      console.error('Error uploading files:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFilesSelection = (selectedFiles) => {
    setSelectedFiles(selectedFiles);
    setShowFormSelection(true);
  };

  const handleFormOptionSelection = (formOption) => {
    if (formOption === 'Consent Form') {
      setSelectedFormOption(formOption);
      onFilesSelected(selectedFiles);
      onFormOptionSelected(formOption);
    } else {
      setShowNotification(true);
    }
  };

  const handleRestart = () => {
    setOption('');
    setFiles([]);
    setExistingFiles([]);
    setSelectedFiles([]);
    setSelectedFormOption('');
    setShowFormSelection(false);
  };

  // Standard button style
  const buttonStyle = {
    height: '50px',
    fontSize: '0.875rem'
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Clinical Trial Document Generator
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Generate and manage clinical trial documentation
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Progress Sidebar */}
        <Grid xs={12} md={3}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Progress
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <CloudUpload color={!option ? 'primary' : 'disabled'} />
                </ListItemIcon>
                <ListItemText 
                  primary="Select Option"
                  sx={{ color: !option ? 'primary.main' : 'text.secondary' }}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Description color={option && !showFormSelection ? 'primary' : 'disabled'} />
                </ListItemIcon>
                <ListItemText 
                  primary="Process Files"
                  sx={{ color: option && !showFormSelection ? 'primary.main' : 'text.secondary' }}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color={showFormSelection ? 'primary' : 'disabled'} />
                </ListItemIcon>
                <ListItemText 
                  primary="Acceleration Options"
                  sx={{ color: showFormSelection ? 'primary.main' : 'text.secondary' }}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        {/* Main Content Area */}
        <Grid xs={12} md={9}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {!option ? 'Select Option' : 
               option === 'Upload New Files' ? 'Upload Files' :
               showFormSelection ? 'Acceleration Options' : 'Select Files'}
            </Typography>

            {!option ? (
              <Grid container spacing={2}>
                <Grid xs={12} sm={6}>
                  <Button
                    variant="contained"
                    sx={buttonStyle}
                    startIcon={<CloudUpload />}
                    onClick={() => setOption('Upload New Files')}
                    fullWidth
                  >
                    Upload New Files
                  </Button>
                </Grid>
                <Grid xs={12} sm={6}>
                  <Button
                    variant="contained"
                    sx={buttonStyle}
                    startIcon={<Description />}
                    onClick={() => setOption('Use Existing Files')}
                    fullWidth
                  >
                    Use Existing Files
                  </Button>
                </Grid>
              </Grid>
            ) : option === 'Upload New Files' ? (
              <Box>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 6,
                    textAlign: 'center',
                    border: '2px dashed rgba(0, 0, 0, 0.12)'
                  }}
                >
                  <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Button
                    variant="contained"
                    component="label"
                    disabled={isProcessing}
                    sx={buttonStyle}
                  >
                    Choose Files
                    <input
                      type="file"
                      hidden
                      multiple
                      accept=".pdf"
                      onChange={(e) => setFiles([...e.target.files])}
                    />
                  </Button>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    or drag and drop files here
                  </Typography>
                </Paper>

                {files.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Selected Files:
                    </Typography>
                    <List>
                      {files.map((file, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <Description />
                          </ListItemIcon>
                          <ListItemText primary={file.name} />
                        </ListItem>
                      ))}
                    </List>
                    <Button
                      variant="contained"
                      onClick={handleFileUpload}
                      disabled={isProcessing}
                      startIcon={isProcessing ? <CircularProgress size={20} /> : <CloudUpload />}
                      sx={buttonStyle}
                    >
                      {isProcessing ? 'Uploading...' : 'Upload Files'}
                    </Button>
                  </Box>
                )}
              </Box>
            ) : existingFiles.length > 0 ? (
              !showFormSelection ? (
                <List>
                  {existingFiles.map((file, index) => (
                    <ListItem
                      key={index}
                      secondaryAction={
                        <Button
                          variant="outlined"
                          onClick={() => handleFilesSelection([file])}
                          disabled={file.status !== 'processed'}
                          sx={buttonStyle}
                        >
                          {file.status === 'processed' ? 'Select' : 'Processing...'}
                        </Button>
                      }
                    >
                      <ListItemIcon>
                        <Description />
                      </ListItemIcon>
                      <ListItemText primary={file.name} />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Grid container spacing={2}>
                  <Grid xs={12} sm={6}>
                    <Button
                      variant="contained"
                      sx={buttonStyle}
                      startIcon={<Description />}
                      onClick={() => handleFormOptionSelection('Consent Form')}
                      fullWidth
                    >
                      Consent Form
                    </Button>
                  </Grid>
                  <Grid xs={12} sm={6}>
                    <Button
                      variant="contained"
                      sx={buttonStyle}
                      startIcon={<Description />}
                      onClick={() => handleFormOptionSelection('Site Initiation')}
                      fullWidth
                    >
                      Site Initiation Checklist
                    </Button>
                  </Grid>
                  <Grid xs={12} sm={6}>
                    <Button
                      variant="contained"
                      sx={buttonStyle}
                      startIcon={<Description />}
                      onClick={() => handleFormOptionSelection('IRB Checklist')}
                      fullWidth
                    >
                      IRB Checklist
                    </Button>
                  </Grid>
                  <Grid xs={12} sm={6}>
                    <Button
                      variant="contained"
                      sx={buttonStyle}
                      startIcon={<Description />}
                      onClick={() => handleFormOptionSelection('Chat')}
                      fullWidth
                    >
                      Chat with your Trial
                    </Button>
                  </Grid>
                </Grid>
              )
            ) : (
              <Box sx={{ textAlign: 'center', py: 6 }}>
                <CircularProgress />
                <Typography sx={{ mt: 2 }} color="text.secondary">
                  Loading files...
                </Typography>
              </Box>
            )}
          </Paper>

          {selectedFormOption && (
            <Paper sx={{ mt: 3, p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Selection Summary
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Selected Files:
                </Typography>
                <List>
                  {selectedFiles.map((file, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Description />
                      </ListItemIcon>
                      <ListItemText primary={file.name} />
                    </ListItem>
                  ))}
                </List>
                <Typography variant="subtitle2" gutterBottom>
                  Selected Form:
                </Typography>
                <Typography>{selectedFormOption}</Typography>
                <Button
                  variant="contained"
                  onClick={handleRestart}
                  startIcon={<Refresh />}
                  sx={{ ...buttonStyle, mt: 2 }}
                >
                  Start Over
                </Button>
              </Box>
            </Paper>
          )}
        </Grid>
      </Grid>

      <Snackbar
        open={showNotification}
        autoHideDuration={6000}
        onClose={() => setShowNotification(false)}
      >
        <Alert 
          onClose={() => setShowNotification(false)} 
          severity="info"
          sx={{ width: '100%' }}
        >
          This feature is not implemented yet.
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default HomeComponent;