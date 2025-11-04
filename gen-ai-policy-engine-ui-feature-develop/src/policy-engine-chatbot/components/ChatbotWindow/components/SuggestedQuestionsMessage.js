import './SuggestedQuestionsMessage.css';

import { SuggestedQuestion } from "./SuggestedQuestion"

export const SuggestedQuestionsMessage = ({questions, program}) => {

    return (
        <div className='message-container'>
            <div className='message-icon'> 
            </div>
            <div className='suggested-questions-message message'>  
                <h4>{`Suggested ${program} Questions`}</h4> 
                    {questions.map(question=> { 
                        return <SuggestedQuestion message={question} program={program}/>
                    })} 
            </div>
        </div>
    ) 
}