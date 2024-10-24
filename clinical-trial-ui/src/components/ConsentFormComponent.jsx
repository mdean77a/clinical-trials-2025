import { useState, useEffect, useRef } from "react";
import { jsPDF } from "jspdf";
import "./ConsentFormComponent.css";
import "./animations.css";

function ConsentFormComponent({
  selectedFiles,
  textAreaData,
  onTextAreaDataUpdate,
}) {
  const initialData = {
    summary: "",
    background: "",
    number_of_participants: "",
    study_procedures: "",
    alt_procedures: "",
    risks: "",
    benefits: "",
  };

  const [data, setData] = useState(textAreaData || initialData);
  const [buffer, setBuffer] = useState(textAreaData || initialData);
  const [activeField, setActiveField] = useState(null);
  const [aiAssistantVisible, setAiAssistantVisible] = useState(false);
  const [aiAssistantInput, setAiAssistantInput] = useState("");
  const [collapsedSections, setCollapsedSections] = useState({
    "Part 1: Master Consent": false,
    "Part 2: Site Specific Information": false,
  });
  const [loading, setLoading] = useState(false);
  const [streamStarted, setStreamStarted] = useState(false);
  
  const isGeneratedRef = useRef(false);
  const textareaRefs = useRef({});
  const processingFields = useRef(new Set());
  const bufferQueue = useRef([]);

  const scrollToBottom = (key) => {
    if (textareaRefs.current[key]) {
      const textarea = textareaRefs.current[key];
      textarea.scrollTop = textarea.scrollHeight;
    }
  };

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    const generateConsentForm = async () => {
      if (isGeneratedRef.current || !selectedFiles.length) {
        return;
      }
      isGeneratedRef.current = true;

      try {
        setLoading(true);
        const response = await fetch(
          `${BACKEND_URL}/generate-consent-form`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ files: selectedFiles }),
          }
        );

        if (!response.body) {
          throw new Error("ReadableStream not supported in this browser.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          try {
            const jsonData = JSON.parse(chunk);
            setStreamStarted(true);
            bufferQueue.current.push(jsonData);
            setBuffer(prevBuffer => ({
              ...prevBuffer,
              ...jsonData
            }));
          } catch (error) {
            console.error("Error parsing chunk:", error);
          }

          if (!streamStarted) {
            setLoading(false);
          }
        }
      } catch (error) {
        console.error("Error generating consent form:", error);
      } finally {
        setLoading(false);
        setStreamStarted(false);
      }
    };

    generateConsentForm();
  }, [selectedFiles]);

  const processField = async (key, content, existingContent = '') => {
    if (processingFields.current.has(key)) return;
    processingFields.current.add(key);

    try {
      const words = content.split(' ');
      let currentText = existingContent;

      for (const word of words) {
        if (!currentText.includes(word)) {
          currentText += (currentText ? ' ' : '') + word;
          setData(prev => ({
            ...prev,
            [key]: currentText
          }));
          scrollToBottom(key);
          await new Promise(r => setTimeout(r, 30));
        }
      }
    } finally {
      processingFields.current.delete(key);
    }
  };

  useEffect(() => {
    const updateFields = async () => {
      const currentBuffer = { ...buffer };
      const currentData = { ...data };
      const updatePromises = [];

      for (const key of Object.keys(initialData)) {
        if (currentBuffer[key] && currentBuffer[key] !== currentData[key]) {
          updatePromises.push(processField(key, currentBuffer[key], currentData[key]));
        }
      }

      await Promise.all(updatePromises);

      // Process any queued updates
      while (bufferQueue.current.length > 0) {
        const nextUpdate = bufferQueue.current.shift();
        if (nextUpdate) {
          setBuffer(prev => ({
            ...prev,
            ...nextUpdate
          }));
        }
      }
    };

    updateFields();
  }, [buffer]);

  // Rest of the component remains the same...
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
      const response = await fetch(`${BACKEND_URL}/revise`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
        scrollToBottom(activeField);
      }

      setAiAssistantInput("");
      setAiAssistantVisible(false);
    } catch (error) {
      console.error("Error with AI assistant:", error);
    }
  };

  const sections = [
    {
      title: "Part 1: Master Consent",
      key: "Part 1: Master Consent",
      fields: [
        { key: "summary", label: "Summary" },
        { key: "background", label: "Background" },
        { key: "number_of_participants", label: "Number of Participants" },
        { key: "study_procedures", label: "Study Procedures" },
        { key: "alt_procedures", label: "Alternative Procedures" },
        { key: "risks", label: "Risks" },
        { key: "benefits", label: "Benefits" },
      ],
    },
  ];

  const toggleSection = (sectionKey) => {
    setCollapsedSections((prevState) => ({
      ...prevState,
      [sectionKey]: !prevState[sectionKey],
    }));
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/download-consent-pdf`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ data }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to generate PDF");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "consent_form.pdf");
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error("Error downloading PDF:", error);
    }
  };

  const hasData = Object.values(data).some((value) => value !== "");

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
                  {collapsedSections[section.key] ? "+" : "-"}
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
                          ref={el => textareaRefs.current[field.key] = el}
                          value={data[field.key]}
                          onFocus={() => handleFocus(field.key)}
                          onChange={(e) => {
                            const newData = {
                              ...data,
                              [field.key]: e.target.value,
                            };
                            setData(newData);
                            onTextAreaDataUpdate(newData);
                            scrollToBottom(field.key);
                          }}
                        />
                      </div>
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