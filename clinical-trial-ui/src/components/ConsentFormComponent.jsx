import { useState, useEffect, useRef } from 'react';
import { parse } from 'best-effort-json-parser';
import { jsPDF } from 'jspdf';
import './ConsentFormComponent.css';
import './animations.css';

function ConsentFormComponent({
  selectedFiles,
  textAreaData,
  onTextAreaDataUpdate,
}) {
  const initialData = {
    // Part 1: Master Consent
    summary: '',
    background: '',
    numberOfParticipants: '',
    studyProcedures: '',
    alternativeProcedures: '',
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

  // Use a ref to track if the consent form has already been generated
  const isGeneratedRef = useRef(false);

  // Fetch consent form data from the backend and handle streaming
  useEffect(() => {
    const generateConsentForm = async () => {
      // Avoid calling the endpoint if already generated or if no files are selected
      if (isGeneratedRef.current || !selectedFiles.length) {
        return;
      }
      isGeneratedRef.current = true; // Mark as generated

      try {
        setLoading(true);
        
        // Start listening to the streaming data from the "generate-consent-form" endpoint
        const response = await fetch('http://localhost:5000/generate-consent-form', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ files: selectedFiles }),
        });

        if (!response.body) {
          console.error('ReadableStream not supported in this browser.');
          setLoading(false);
          return;
        }

        const reader = response.body.getReader();
        setLoading(false);
        const decoder = new TextDecoder('utf-8');
        let partialResponse = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          partialResponse += decoder.decode(value, { stream: true });

          // Attempt to parse JSON from buffer using best-effort-json-parser
          try {
            // const jsonStr = partialResponse.trim();
            const parsedData = parse(partialResponse);
            console.log("JsonMessage: ", JSON.stringify(parsedData));
            if (parsedData) {
              setData((prevData) => ({
                ...prevData,
                ...parsedData,
              }));
              onTextAreaDataUpdate((prevData) => ({
                ...prevData,
                ...parsedData,
              }));
            }
          } catch (e) {
            // Continue collecting data until we get complete JSON fragments
            continue;
          }
        }
      } catch (error) {
        console.error('Error generating consent form:', error);
        setLoading(false);
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
      const response = await fetch('http://localhost:5000/revise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          field: activeField,
          content: data[activeField],
          question: aiAssistantInput,
        }),
      });

      // Start listening to the streaming data for the revised field
      if (!response.body) {
        console.error('ReadableStream not supported in this browser.');
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Update the text area with the streamed content
        try {
          const newData = parse(buffer);
          if (newData && newData[activeField]) {
            setData((prevData) => ({
              ...prevData,
              [activeField]: newData[activeField],
            }));
            onTextAreaDataUpdate((prevData) => ({
              ...prevData,
              [activeField]: newData[activeField],
            }));
            buffer = '';
          }
        } catch (e) {
          // Continue if the JSON is incomplete
          continue;
        }
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
        { key: 'numberOfParticipants', label: 'Number of Participants' },
        { key: 'studyProcedures', label: 'Study Procedures' },
        { key: 'alternativeProcedures', label: 'Alternative Procedures' },
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
      const response = await fetch('http://localhost:5000/download-consent-pdf', {
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
      {loading ? (
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
