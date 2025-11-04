import { useState } from "react"
import { IoMdCheckmark } from "react-icons/io";
import { IoMdClose } from "react-icons/io";
import './FeedbackInput.css'
import { FeedbackType } from "../../../../constant";
import { usePolicyEngineContext } from "../../../../Context";

export const FeedbackInput = ({id}) => {
    const [feedbackValue, setFeedbackValue] = useState('');
    const {setFeedback, setCurrentFeedbackId} = usePolicyEngineContext();

    const handleFeedbackSubmission = (e) => {
        e.preventDefault();
        setFeedback(id, FeedbackType.DOWN_VOTE, feedbackValue)
    }

    return (
        <form className="feedback-input" onSubmit={(e) => handleFeedbackSubmission(e)}>
            <input id='userFeedback' placeholder='Enter your feedback...' value={feedbackValue} onChange={(e)=>setFeedbackValue(e.target.value)}/>
                <button className="feedback-button" type="submit">
                    <IoMdCheckmark />
                </button>
                <button className="feedback-button">
                    <IoMdClose onClick={()=>setCurrentFeedbackId(-1)}/>
                </button>
        </form>
    )
}