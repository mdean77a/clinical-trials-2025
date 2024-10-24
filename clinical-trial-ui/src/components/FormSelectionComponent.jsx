import './FormSelectionComponent.css';

function FormSelectionComponent({ onFormOptionSelected }) {
  const handleFormSelect = (option) => {
    onFormOptionSelected(option);
  };

  return (
    <div className="form-selection-component">
      <h2>Select a Form to Proceed</h2>
      <button onClick={() => handleFormSelect('Consent Form')}>Consent Form</button>
      <button onClick={() => handleFormSelect('Site Initiation')}>
        Site Initiation Checklist
      </button>
      <button onClick={() => handleFormSelect('IRB Checklist')}>
        IRB Checklist
      </button>
      <button onClick={() => handleFormSelect('Chat with your trial documents')}>
        Chat with your trial
      </button>
    </div>
  );
}

export default FormSelectionComponent;
