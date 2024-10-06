import React, { useState, useEffect } from 'react';
import TextAreaComponent from './TextAreaComponent';
// import './ConsentFormComponent.css';

function ConsentFormComponent({
  selectedFiles,
  textAreaData,
  onTextAreaDataUpdate,
}) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConsentFormData = async () => {
      try {
        const response = await fetch('http://localhost:5000/consent-form', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ files: selectedFiles }),
        });

        if (!response.body) {
          console.error('ReadableStream not supported in this browser.');
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let receivedData = false;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          if (!receivedData) {
            setLoading(false);
            receivedData = true;
          }

          let parsed = false;
          while (!parsed) {
            try {
              const jsonStr = buffer.trim();
              if (jsonStr.endsWith('}')) {
                const parsedData = JSON.parse(jsonStr);
                onTextAreaDataUpdate((prevData) => ({
                  ...prevData,
                  ...parsedData,
                }));
                buffer = '';
              }
              parsed = true;
            } catch (e) {
              // Incomplete JSON; wait for more data
              parsed = true;
            }
          }
        }
      } catch (error) {
        console.error('Error fetching consent form data:', error);
      }
    };

    fetchConsentFormData();
  }, [selectedFiles, onTextAreaDataUpdate]);

  return (
    <div className="consent-form-component">
      {loading && <div className="loading-spinner">Loading...</div>}
      {!loading && (
        <TextAreaComponent
          textAreaData={textAreaData}
          onTextAreaDataUpdate={onTextAreaDataUpdate}
        />
      )}
    </div>
  );
}

export default ConsentFormComponent;
