import { usePolicyEngineContext } from '../../../../Context';
import './SuggestedQuestion.css';

export const SuggestedQuestion = ({message, program}) => {
    const {submitQuestion, isWaitingforAnswer, isServerDown} = usePolicyEngineContext();
    const status = !isServerDown && !isWaitingforAnswer ? 'enabled':'disabled'
    const sendSuggestedQuestion = () => {
        if(status==='enabled') {
            submitQuestion(message, program);
        }
    }
    
    return (
        <div onClick={()=>sendSuggestedQuestion()} className={`suggested-question ${status}`}>  
            {message}
        </div>
    ) 
}