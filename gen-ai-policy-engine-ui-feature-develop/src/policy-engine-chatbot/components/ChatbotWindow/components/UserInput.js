import './UserInput.css'
import sendIcon from '../../../../icons/messenger-cx-chat-send-icon.svg';
import { usePolicyEngineContext } from "../../../../Context";

export const UserInput = () => { 

  const {setProgram, setUserMessage, submitQuestion, isWaitingforAnswer, userMessage, program, isServerDown} = usePolicyEngineContext()

  const placeholder = program ? isWaitingforAnswer? "Please wait for the answer..." : `Type your ${program} question...` : "Please select a program first.";

  const handleSendQuestion = async (e) => {
    e.preventDefault();
    submitQuestion();
  }

  return ( 
      <div className="input-container">       
        <form className="input-box-form" onSubmit={(e)=>handleSendQuestion(e)}>
          <select id='program' disabled={isWaitingforAnswer || isServerDown} value={program} onChange={(e)=>setProgram(e.target.value)}>
            <option disabled={program}>Select a program</option>
            <option value='SNAP'>SNAP</option>
            <option value='TANF'>TANF</option>
            <option value='Medicaid'>Medicaid</option>
          </select>
          <input disabled={isWaitingforAnswer || !program || isServerDown} id='userQuestion' placeholder={placeholder} value={userMessage} onChange={(e)=>setUserMessage(e.target.value)}/>          
          <button disabled={isWaitingforAnswer || !program || isServerDown} type="submit">
              <img src={sendIcon}/>
          </button>
        </form>
      </div> 
  )
}