import React, { useState } from 'react';
import HomeComponent from './components/HomeComponent.jsx';
import ConsentFormComponent from './components/ConsentFormComponent.jsx';
import DownloadPDFComponent from './components/DownloadPDFComponent.jsx';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import './App.css';
import './transitions.css';

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [formOption, setFormOption] = useState('');
  const [textAreaData, setTextAreaData] = useState({});
  const [showConsentForm, setShowConsentForm] = useState(false);

  const handleFilesSelected = (files) => {
    setSelectedFiles(files);
  };

  const handleFormOptionSelected = (option) => {
    if (option === 'Consent Form') {
      setFormOption(option);
      setShowConsentForm(true);
    } else {
      alert('This option is not implemented yet.');
    }
  };

  const handleTextAreaDataUpdate = (data) => {
    setTextAreaData(data);
  };

  const handleRestart = () => {
    // Reset all states to initial values
    setSelectedFiles([]);
    setFormOption('');
    setTextAreaData({});
    setShowConsentForm(false);
  };

  return (
    <div className="App">
      {!showConsentForm ? (
        <HomeComponent
          onFilesSelected={handleFilesSelected}
          onFormOptionSelected={handleFormOptionSelected}
        />
      ) : (
        <>
          <ConsentFormComponent
            selectedFiles={selectedFiles}
            textAreaData={textAreaData}
            onTextAreaDataUpdate={handleTextAreaDataUpdate}
          />
          <DownloadPDFComponent textAreaData={textAreaData} />
          <button onClick={handleRestart}>Restart</button>
        </>
      )}
    </div>
  );
}

export default App;