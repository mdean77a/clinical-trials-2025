import { useState, useEffect, useRef } from 'react';
import { jsPDF } from 'jspdf';
import './ConsentFormComponent.css';
import './animations.css';

function ConsentFormComponent({
  selectedFiles,
  textAreaData,
  onTextAreaDataUpdate,
}) {
  const initialData = {
    summary: '',
    background: '',
    number_of_participants: '',
    study_procedures: '',
    alt_procedures: '',
    risks: '',
    benefits: ''
  };

  const [data, setData] = useState(textAreaData || initialData);
  const [activeField, setActiveField] = useState(null);
  const [aiAssistantVisible, setAiAssistantVisible] = useState(false);
  const [aiAssistantInput, setAiAssistantInput] = useState('');
  const [collapsedSections, setCollapsedSections] = useState({
    'Part 1: Master Consent': false,
    'Part 2: Site Specific Information': false,
  });
  const [loading, setLoading] = useState(false);
  const [streamStarted, setStreamStarted] = useState(false);

  // Use a ref to track if the consent form has already been generated
  const isGeneratedRef = useRef(false);

  // Fetch consent form data from the backend and handle streaming
  useEffect(() => {
    const generateConsentForm = async () => {
      if (isGeneratedRef.current || !selectedFiles.length) {
        return;
      }
      isGeneratedRef.current = true;

      try {
        setLoading(true);
        
        const response = await fetch('http://localhost:8000/generate-consent-form', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ files: selectedFiles }),
        });

        if (!response.body) {
          throw new Error('ReadableStream not supported in this browser.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonData = JSON.parse(line.slice(6));
                console.log("Received update:", jsonData);
                setData(prevData => {
                  const newData = { ...prevData };
                  for (const [key, value] of Object.entries(jsonData)) {
                    if (Array.isArray(value) && value.length > 0) {
                      newData[key] = value[0];  // Use the first (and only) element of the array
                    } else if (value !== undefined && value !== null) {
                      newData[key] = value;
                    }
                  }
                  return newData;
                });
                onTextAreaDataUpdate(prevData => {
                  const newData = { ...prevData };
                  for (const [key, value] of Object.entries(jsonData)) {
                    if (value !== undefined && value !== null) {
                      newData[key] = value;
                    }
                  }
                  return newData;
                });
                if (!streamStarted) {
                  setStreamStarted(true);
                  setLoading(false);
                }
              } catch (e) {
                console.error('Error parsing JSON:', e);
              }
            }
          }
        }

      } catch (error) {
        console.error('Error generating consent form:', error);
      } finally {
        setLoading(false);
        setStreamStarted(false);
      }
    };

    generateConsentForm();
  }, [selectedFiles, onTextAreaDataUpdate]);

  // AI Assistant functionality
  const handleFocus = (field) => {
    setActiveField(field);
    setAiAssistantVisible(true);
  };

  const handleBlur = (e) => {
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setActiveField(null);
      setAiAssistantVisible(false);
    }
  };

  const handleAiAssistantSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/revise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          field: activeField,
          content: data[activeField],
          question: aiAssistantInput,
        }),
      });

      const result = await response.json();
      if (result && result[activeField]) {
        setData((prevData) => ({
          ...prevData,
          [activeField]: result[activeField],
        }));
        onTextAreaDataUpdate((prevData) => ({
          ...prevData,
          [activeField]: result[activeField],
        }));
      }

      setAiAssistantInput('');
      setAiAssistantVisible(false);
    } catch (error) {
      console.error('Error with AI assistant:', error);
    }
  };

  // Define the sections and fields
  const sections = [
    {
      title: 'Part 1: Master Consent',
      key: 'Part 1: Master Consent',
      fields: [
        { key: 'summary', label: 'Summary' },
        { key: 'background', label: 'Background' },
        { key: 'number_of_participants', label: 'Number of Participants' },
        { key: 'study_procedures', label: 'Study Procedures' },
        { key: 'alt_procedures', label: 'Alternative Procedures' },
        { key: 'risks', label: 'Risks' },
        { key: 'benefits', label: 'Benefits' }
      ],
    }
  ];

  const toggleSection = (sectionKey) => {
    setCollapsedSections((prevState) => ({
      ...prevState,
      [sectionKey]: !prevState[sectionKey],
    }));
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await fetch('http://localhost:8000/download-consent-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }
  
      const blob = await response.blob();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'consent_form.pdf');
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };
  
  const hasData = Object.values(data).some((value) => value !== '');

  return (
    <div className="consent-form-component">
      {loading && !streamStarted ? (
        <div className="loading-spinner">Loading...</div>
      ) : (
        <div className="text-area-component">
          {sections.map((section, sIndex) => (
            <div key={sIndex} className="consent-section">
              <h2
                onClick={() => toggleSection(section.key)}
                className="collapsible-header"
              >
                {section.title}
                <span className="toggle-icon">
                  {collapsedSections[section.key] ? '+' : '-'}
                </span>
              </h2>
              {!collapsedSections[section.key] && (
                <div className="section-content">
                  {section.fields.map((field, fIndex) => (
                    <div
                      key={fIndex}
                      className="text-area-container"
                      onBlur={handleBlur}
                      tabIndex="-1"
                    >
                      <div className="text-area-field">
                        <label>{field.label}</label>
                        <textarea
                          value={data[field.key]}
                          onFocus={() => handleFocus(field.key)}
                          onChange={(e) => {
                            const newData = {
                              ...data,
                              [field.key]: e.target.value,
                            };
                            setData(newData);
                            onTextAreaDataUpdate(newData);
                          }}
                        />
                      </div>
                      {/* AI Assistant Panel */}
                      {activeField === field.key && aiAssistantVisible && (
                        <div className="ai-assistant-panel">
                          <form onSubmit={handleAiAssistantSubmit}>
                            <input
                              type="text"
                              placeholder="Ask AI assistant"
                              value={aiAssistantInput}
                              onChange={(e) =>
                                setAiAssistantInput(e.target.value)
                              }
                            />
                            <button type="submit">Submit</button>
                          </form>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      {hasData && !loading && (
        <div className="actions">
          <button onClick={handleDownloadPDF}>Download PDF</button>
          <button onClick={() => window.location.reload()}>Restart</button>
        </div>
      )}
    </div>
  );
}

export default ConsentFormComponent;