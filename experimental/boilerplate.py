def boilerplate():
    boilerplate = """ 
    ## Right of the Investigator to Withdraw Participants
    The investigator can withdraw you from the study without your approval.  If at any time the
    investigator believes participating in the study is not the best choice of care, the study
    may be stopped and other care prescribed.  If unexpected medical problems come up, the investigator
    may decide to stop your participation in the study.

    ---

    ## New Information
    Sometimes during the course of a research project, new information becomes available about the
    drugs that are being studied. If this happens, your research doctor will tell you about it and discuss
    with you whether you want to continue in the study. If you decide to continue in the study, you
    may be asked to sign an updated consent form. Also, on receiving new information the research
    doctor might consider it to be in your best interests to withdraw you from the study. He/she will
    explain the reasons and arrange for your medical care to continue.

    ---

    ## Costs and Compensation to Participants
    While you are in this study, the cost of your usual medical care - procedures, medications and
    doctor visits - will continue to be billed to you or your insurance. There will be no additional costs
    to you for your participation in this study. You will receive up to \$50 to compensate you for your
    time when completing the follow-up surveys at the 3- and 12-month time points. You will receive
    \$25 for each follow-up period once we receive your answers to the surveys. Any tests that are
    performed or medications administered solely for the purposes of being in this study will be paid
    for by the research doctor. The National Institutes of Health is providing funding for this study.

    ---

    ## Single IRB Contact
    **Institutional Review Board:** The University of Utah Institutional Review Board (IRB) is
    serving as the single IRB (SIRB) for this study. Contact the SIRB if you have questions, complaints
    or concerns which you do not feel you can discuss with the investigator. The University of Utah
    IRB may be reached by phone at (801) 581-3655 or 
    by e-mail at irb@hsc.utah.edu.

    """
    return boilerplate

def part2(protocol_title, principal_investigator, support):
    part2 = f""" 
    ## Parental Permission, Teen Assent and Authorization Document

    **Study Title:** {protocol_title}

    **Principal Investigator:** {principal_investigator}

    **Source of Support:** {support}

    ---

    <div style="text-align: center;">

    ## Part 2 of 2: SITE SPECIFIC INFORMATION
    </div>

    This section of the consent form, as well as signature pages, are very specific
    to individual sites, and the Clinical Trial Accelerator does not have the ability
    to create this section.principal_investigator

    ---

    """
    return part2

def heading(protocol_title, version_date, support):
    heading = f""" 
    ## Parental Permission, Teen Assent and Authorization Document

    **Study Title:** {protocol_title}

    **Version Date:** {version_date}

    **Source of Support:** {support}

    ---

    <div style="text-align: center;">

    ## Part 1 of 2: MASTER CONSENT
    </div>

    **Parents/Guardians:**
    You have the option of having your child or teen join a research study.
    This is a parental permission form. It provides a summary of the information the research team
    will discuss with you. If you decide that your child can take part in this study, you would sign
    this form to confirm your decision. If you sign this form, you will receive a signed copy for your
    records. *The word “you” in this form refers to your child/teen unless otherwise indicated.*

    **Assent Teen Participants:**
    This form also serves as an assent form. That means that if you
    choose to take part in this research study, you would sign this form to confirm your choice. Your
    parent or guardian would also need to give their permission and sign this form for you to join the
    study

    **Consent for Continued Participation (Participants who turn 18 during the study):**
    This is a consent form for continued participation. It provides a summary of the information the
    research team will discuss with you. If you decide that you would like to continue participating in
    this research study, you would sign this form to confirm your decision. If you sign this form, you
    will receive a signed copy of this form for your records.

    ---

    """ 
    return heading