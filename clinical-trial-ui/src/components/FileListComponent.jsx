import React, { useState } from 'react';
import './FileListComponent.css';

function FileListComponent({ files, onFilesSelected }) {
  const [selectedFiles, setSelectedFiles] = useState([]);

  const handleFileSelection = (file) => {
    setSelectedFiles((prev) =>
      prev.includes(file) ? prev.filter((f) => f !== file) : [...prev, file]
    );
  };

  const handleProceed = () => {
    if (selectedFiles.length === 0) {
      alert('Please select at least one file.');
      return;
    }
    onFilesSelected(selectedFiles);
  };

  return (
    <div className="file-list-component">
      <h2>Select Files for Processing</h2>
      <ul>
        {files.map((file, index) => (
          <li key={index}>
            <label>
              <input
                type="checkbox"
                onChange={() => handleFileSelection(file)}
              />
              {file.name} {file.status !== 'processed' && '(Processing)'}
            </label>
          </li>
        ))}
      </ul>
      <button onClick={handleProceed}>Proceed</button>
    </div>
  );
}

export default FileListComponent;
