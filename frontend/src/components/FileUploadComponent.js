import React, { useState } from 'react';
import './FileUploadComponent.css';

function FileUploadComponent({ uploadedFiles, onFilesUploaded }) {
  const [selectedFiles, setSelectedFiles] = useState([]);

  const handleFileSelect = (e) => {
    setSelectedFiles([...e.target.files]);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      alert('Please select files to upload.');
      return;
    }

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append('pdf_files', file);
    });

    try {
      // You can make an API call here if needed
      // For now, we'll just call the onFilesUploaded callback
      onFilesUploaded();
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  };

  return (
    <div className="file-upload-component">
      {uploadedFiles && uploadedFiles.length > 0 ? (
        <div className="uploaded-files-list">
          <h3>Uploaded Files:</h3>
          <ul>
            {uploadedFiles.map((file, index) => (
              <li key={index}>{file.name}</li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="upload-section">
          <input
            type="file"
            accept=".pdf"
            multiple
            onChange={handleFileSelect}
          />
          <button onClick={handleUpload}>Upload</button>
        </div>
      )}
    </div>
  );
}

export default FileUploadComponent;