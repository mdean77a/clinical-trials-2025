// src/services/pdfService.js

export const validateFormData = (formData) => {
  const errors = {};
  const requiredFields = [
    'summary',
    'background',
    'number_of_participants',
    'study_procedures',
    'risks',
    'benefits'
  ];

  requiredFields.forEach(field => {
    if (!formData[field] || formData[field].trim() === '') {
      errors[field] = 'This field is required';
    }
  });

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

const stripHtmlAndFormatText = (text) => {
  if (!text) return '';
  
  // First, fix any unclosed tags and common issues
  let processed = text
    // Remove single line breaks and normalize spaces
    .replace(/\r?\n|\r/g, ' ')
    .replace(/\s+/g, ' ')
    // Fix unclosed strong tags
    .replace(/<strong>([^<]*?)(?!<\/strong>)/g, '<strong>$1</strong>')
    // Remove para and p tags
    .replace(/<\/?para>/g, '')
    .replace(/<\/?p>/g, '')
    // Convert <br> to newlines
    .replace(/<br\s*\/?>/gi, '\n')
    // Convert lists to text with newlines and bullets
    .replace(/<li>/g, '• ')
    .replace(/<\/li>/g, '\n')
    .replace(/<\/?[uo]l>/g, '\n')
    // Remove all other HTML tags
    .replace(/<[^>]+>/g, '')
    // Trim whitespace
    .trim();

  // Replace multiple spaces with single space
  processed = processed.replace(/\s+/g, ' ');
  
  // Add proper paragraph spacing
  return processed.split('\n').filter(line => line.trim()).join('\n\n');
};

const formatContentForPdf = (formData) => {
  const formatted = {};
  Object.entries(formData).forEach(([key, value]) => {
    formatted[key] = stripHtmlAndFormatText(value);
  });
  return formatted;
};

export const downloadConsentPdf = async (formData) => {
  try {
    // Format the content for PDF generation
    const formattedData = formatContentForPdf(formData);

    const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/download-consent-pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/pdf',
      },
      body: JSON.stringify({ data: formattedData }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to generate PDF: ${errorText}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    const timestamp = new Date().toISOString().split('T')[0];
    link.href = url;
    link.setAttribute('download', `consent_form_${timestamp}.pdf`);
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    setTimeout(() => {
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }, 100);

    return true;
  } catch (error) {
    console.error('Error downloading PDF:', error);
    throw error;
  }
};