import './Notice.css';

export const Notice = () => {
    return (
        <div className='notice'>
             <h3 className='header'>Welcome to the Georgia Policy Engine!</h3>
              <h4 className='header'>*** INTERNAL USE ONLY ***</h4>
              <strong className='reminder'>Reminders:</strong>
              <ul>
                <li>
                  Do not provide screenshots or copy answers for the public. Use
                  the wording in the the policy manual in written communications.
                </li>
                <li>Do not include PIl/PHI in questions.</li>
                <li>
                  This tool does not replace your research. You are responsible
                  for confirming the answer is correct in the policy manuals
                  before using it.
                </li>
                <li>Comprehensive questions give comprehensive answers.</li>
                <li>
                  This tool will query the following documents to inform answers
                  to your policy questions:
                </li>
                <ul>
                  <li>
                    <strong>(SNAP)</strong> Supplemental Nutrition Assistance
                    Program Manual
                  </li>
                  <li>
                    <strong>(Medicaid)</strong> / Medical Assistance Manual
                  </li>
                  <li>
                    <strong>(TANF)</strong> Temporary Assistance for Needy
                    Families Manual
                  </li>
                </ul>
              </ul>
              <p className="warning">
                Please do not enter any Personally Identifiable Information (PII)
                into the Georgia Policy Engine.
              </p>
        </div>
    )
}