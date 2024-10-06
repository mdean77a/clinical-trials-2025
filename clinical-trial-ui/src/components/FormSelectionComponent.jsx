import React from 'react';
// import './FormSelectionComponent.css';

function FormSelectionComponent({ onFormOptionSelected }) {
  const handleFormSelect = (option) => {
    onFormOptionSelected(option);
  };

  return (
    <div className="form-selection-component">
      <h2>Select a Form to Proceed</h2>
      <button onClick={() => handleFormSelect('Consent Form')}>Consent Form</button>
      <button onClick={() => handleFormSelect('Some Other Form 1')}>
        Some Other Form 1
      </button>
      <button onClick={() => handleFormSelect('Some Other Form 2')}>
        Some Other Form 2
      </button>
    </div>
  );
}

export default FormSelectionComponent;
