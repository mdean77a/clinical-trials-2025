import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FileListComponent from './FileListComponent.jsx';
import FormSelectionComponent from './FormSelectionComponent.jsx';
import './HomeComponent.css';

function HomeComponent({ onFilesSelected, onFormOptionSelected }) {
  const [option, setOption] = useState('');
  const [files, setFiles] = useState([]);
  const [existingFiles, setExistingFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [selectedFormOption, setSelectedFormOption] = useState('');
  const [showFormSelection, setShowFormSelection] = useState(false);

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    if (option === 'Use Existing Files') {
      fetchExistingFiles();
    }
  }, [option]);

  const fetchExistingFiles = async () => {
    try {
      // use backendUrl to in below get request
      const response = await axios.get(`${BACKEND_URL}/existing-files`);
      setExistingFiles(response.data.files);
    } catch (error) {
      console.error('Error fetching existing files:', error);
    }
  };

  const handleOptionSelect = (selectedOption) => {
    setOption(selectedOption);
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
      await axios.post(`${BACKEND_URL}/upload`, formData);
      alert('Files uploaded successfully. Please select "Use Existing Files" to proceed.');
      setOption(''); // Reset option to allow user to select again
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
      // Pass the selected files and form option to parent component
      onFilesSelected(selectedFiles);
      onFormOptionSelected(formOption);
    } else {
      alert('This option is not implemented yet.');
    }
  };

  const handleRestart = () => {
    // Reset all states to initial values
    setOption('');
    setFiles([]);
    setExistingFiles([]);
    setSelectedFiles([]);
    setSelectedFormOption('');
    setShowFormSelection(false);
  };

  return (
    <div className="home-component">
      {!option ? (
        // Option selection
        <div className="option-selection">
          <h2>Select an option:</h2>
          <button onClick={() => handleOptionSelect('Upload New Files')}>Upload New Files</button>
          <button onClick={() => handleOptionSelect('Use Existing Files')}>Use Existing Files</button>
        </div>
      ) : option === 'Upload New Files' ? (
        // File upload section
        <div className="upload-section">
          <h2>Upload New Files</h2>
          <input
            type="file"
            accept=".pdf"
            multiple
            onChange={(e) => setFiles([...e.target.files])}
          />
          <button onClick={handleFileUpload} disabled={isProcessing}>
            {isProcessing ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      ) : existingFiles.length > 0 ? (
        // File selection and form selection
        !showFormSelection ? (
          <FileListComponent
            files={existingFiles}
            onFilesSelected={handleFilesSelection}
          />
        ) : !selectedFormOption ? (
          <FormSelectionComponent
            onFormOptionSelected={handleFormOptionSelection}
          />
        ) : (
          // Display selected files and form option as static view
          <div className="selection-summary">
            <h2>Selection Summary</h2>
            <p><strong>Selected Files:</strong></p>
            <ul>
              {selectedFiles.map((file, index) => (
                <li key={index}>{file.name}</li>
              ))}
            </ul>
            <p><strong>Selected Form:</strong> {selectedFormOption}</p>
            <button onClick={handleRestart}>Restart</button>
          </div>
        )
      ) : (
        <div>Loading files...</div>
      )}
    </div>
  );
}

export default HomeComponent;
