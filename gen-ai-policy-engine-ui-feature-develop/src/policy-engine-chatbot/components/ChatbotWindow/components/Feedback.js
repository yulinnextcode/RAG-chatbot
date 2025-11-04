import { FaThumbsDown, FaThumbsUp } from "react-icons/fa";
import './Feedback.css';
import { usePolicyEngineContext } from "../../../../Context";
import { FeedbackType } from "../../../../constant";
import { FeedbackInput } from "./FeedbackInput";

export const Feedback = ({id, feedback}) => {
    const {setFeedback, cancelFeedback, currentFeedbackId, setCurrentFeedbackId} = usePolicyEngineContext();

    return <div className="feedback">
      {!feedback.type && currentFeedbackId!==id && <>
        <div className='feedback-container'>
          <button
            variant="link"
            className="feedback-button"
            onClick={()=>setFeedback(id, FeedbackType.UP_VOTE, "")}
          >
            <FaThumbsUp />
          </button>
          <button
            variant="link"
            className="feedback-button"
            onClick={()=>setCurrentFeedbackId(id)}
          >
            <FaThumbsDown />
          </button>
        </div>
      </>}


      {currentFeedbackId===id && <div className='feedback-input-container'>
          <button
            variant="link"
            className="feedback-button"
            onClick={()=>setCurrentFeedbackId(id)}
          >
            <FaThumbsDown />
          </button>
          <FeedbackInput id={id} />
        </div>}

      {feedback.type === FeedbackType.UP_VOTE && <div className='feedback-container'>
        <button
          variant="link"
          className="feedback-button thumb-up"
          onClick={()=>cancelFeedback(id)}
        >
          <FaThumbsUp />
        </button>
        <span>Thank you for your feedback!</span>
      </div>}
      
      {feedback.type === FeedbackType.DOWN_VOTE && <div className='feedback-container'>
        <button
          variant="link"
          className="feedback-button thumb-down"
          onClick={()=>cancelFeedback(id)}
        >
          <FaThumbsDown />
        </button>
        <span>Thank you for your feedback!</span>
      </div>}

  </div>
}