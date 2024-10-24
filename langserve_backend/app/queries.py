def summary_query():
    summary_query = """ 
    Please write a summary of the protocol that can be used as the introduction to an informed
    consent document for a patient to participate in the study described in the protocol.  This
    summary should be between 500 and 1000 words in length, and should be understandable by a normally
    intelligent adult patient.  You must explain any medical or technical terms in a way
    that a high school graduate can understand. The summary should briefly explain the study, the rationale for the study,
    the risks and benefits of participation, and that participation is entirely voluntary.

    Start the summary with a level 2 Markdown header (##) titled "Study Summary". Then continue with
    the content without any further subheadings. Produce the entire summary in Markdown format so it 
    can be nicely printed for the reader.

    You should assume that the consent form is addressed to the parent of a potentially eligible
    child, and the very beginnning of the summary should indicate that they are being invited to allow
    their child to participate because the child is potentially eligible. State why their child is potentially
    eligible.  

    All the details of this introductory summary should be specific for this protocol.

    """
    return summary_query

def background_query():

    background_query = """ 
    Please write a summary of the protocol that can be used as the background section of an informed
    consent document for a patient to participate in the study described in the protocol.  This
    summary should be between 500 and 1000 words in length, and should be understandable by a normally
    intelligent adult patient.  You must explain any medical or technical terms in a way
    that a high school graduate can understand. The summary should briefly explain why this patient is being
    approached to be in the study, including a brief description of the disease that is being studied in the 
    protocol, a description of the study interventions, and the scientific reasons that the investigators believe
    the intervention might help the patient.  

    Do not include the specific study procedures in this summary, because this will be presented in a different section of 
    the informed consent document.  You also do not need to mention that participation is voluntary, nor
    the specific risks and benefits of the study, because this information is being presented in a different
    part of the informed consent document.

    Start the summary with a level 2 Markdown header (##) titled "Background". Then continue with
    the content without any further subheadings. Produce the entire summary in Markdown format so it 
    can be nicely printed for the reader. 

    All the details of this background summary should be specific for this protocol.

    """
    return background_query

def number_of_participants_query():

    number_of_participants_query = """ 
    Please write a summary of the protocol that can be used 
    for the "number of participants" section of the informed consent document.  This should include where the
    study is being conducted (for example, at this hospital, or in a network, or in multiple hospitals), the funding source
    (often the NIH), the total number of participants that are planned to be enrolled in the study,
    and the total period of the time that the study is expected to enroll subjects. This summary should not require more than 200 words.

    Start the summary with a level 2 Markdown header (##) titled "Number of Participants". Then continue with
    the content without any further subheadings. Produce the entire summary in Markdown format so it 
    can be nicely printed for the reader. 

    All the details of this number of participants summary should be specific for this protocol.

    """
    return number_of_participants_query

def study_procedures_query():
    study_procedures_query = """ 
    Please write a detailed summary of all the study procedures that will be carried out in this protocol based on the provided context. These procedures should be included in the 'Study Procedures' section of the informed consent document that the patient will read when deciding whether to participate in the study. All significant procedures should be included.

    Ensure the language is understandable for a non-medical audience.
    Write the summary as if speaking directly to the patient (use 'you' instead of 'patient').
    Exclude any discussions on risks, benefits, or voluntariness, as they are covered in separate sections.
    Be detailed, as it is important that the patient understands each procedure.
    The summary should begin with a Level 2 Markdown header (##) titled 'Study Procedures' and include subheadings to organize the information effectively. Do not go deeper than two subheadings.
    """
    return study_procedures_query

def alt_procedures_query():
    alt_procedures_query = """ 
    Please write a  summary of alternatives to participation in this study.  An example is:

    " Your participation in this study is voluntary.  It is not necessary to be in this study to get care for
    your illness.  Monitoring of immune function is not currently done as part of routine ICU care.  There are no
    other treatments designed to increase immune function of reduce inflammation that are routinely used in 
    children with sepsis."

    Note that this example is purely an example, and your summary must be specific to the protocol. The summary should
    be easily understandable by medically untrained readers.  This section is usually less than 500 words in length.


    Start the summary with a level 2 Markdown header (##) titled "Alternative Procedures", and then continue with
    the content without any further subheadings. Produce the entire summary in Markdown format so it 
    can be nicely printed for the reader. 


    """
    return alt_procedures_query

def risks_query():
    risks_query = """ 
    Please write a detailed summary of the possible risks of participating in a clinical trial. This summary will be used for the 'Risks' section of an informed consent document, and should cover common risks associated with clinical research, including risks related to the administration of drugs or devices, side effects, adverse reactions, and any risks from study procedures such as testing, data collection, and blood draws.

    You do not need to rely on specific details from the protocol. Instead, provide a comprehensive, general overview of the potential risks, including:

    Risks related to the study drug, device, or intervention
    Risks from study procedures like blood draws, imaging, or surgeries
    Possible allergic reactions or unexpected side effects
    Risks of data breaches or loss of privacy
    Any unforeseeable risks or long-term concerns that might arise from participation
    Make sure the language is simple and accessible for individuals without a medical background, and speak directly to the participant by using 'you' instead of 'the patient'. Define any complex or technical terms.

    The risk summary should be 2000 to 3000 words long, and structured with a Level 2 Markdown header titled 'Risks'. Use subheadings where appropriate, but keep the depth to no more than two levels.

    In this case, focus on potential side effects such as common, rare, and serious adverse reactions, as well as risks associated with the use of investigational drugs or devices, including possible complications and long-term health impacts. 
    """
    return risks_query

def benefits_query():
    benefits_query = """ 
    Please write a  summary of the potential benefits of participating in  the study.  This will be used for the
    "Benefits" section of the informed consent document.  The summary should include potential benefits for the patient
    (addressed as "you"), and potential benefits for others.  Since this is a research study and it is
    not known if the intervention is helpful, it is important to not overstate potential benefits for the patient.

    The length of this risk summary is usually
    500 to 750 words.

    Start the summary with a level 2 Markdown header (##) titled "Benefits",  and then continue 
    with a subheading for "Potential
    Benefits for You" and another subheading for "Potential Benefits for Others".

    All the information of study benefits should be specific to this protocol.

    """
    return benefits_query