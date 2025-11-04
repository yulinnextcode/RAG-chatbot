import { forwardRef } from 'react';
import './BotMessage.css';
import { Feedback } from './Feedback';
import { RiRobot3Line } from "react-icons/ri"; 
import { ReasoningMessage } from './ReasoningMessage';
import { SuggestedQuestionsMessage } from './SuggestedQuestionsMessage';
import { usePolicyEngineContext } from '../../../../Context';

export const BotMessage = forwardRef(({message, i}, ref) => {
    const {setExpanded} = usePolicyEngineContext();

    return (<>
            {message?.message && <>
                <div className='message-container'>
                    <div className='message-icon'>
                        <RiRobot3Line />
                    </div>
                    <div ref={ref} className='bot-message message'>  
                        {message.message.summary && <>
                            <h4>Summary:</h4>
                            <div className='summary'>{message.message.summary}</div>
                        </>}
                        {message.message.references && message.message.references.length>0 && <>
                            <h4>References:</h4>
                            <ul>
                                {message.message.references.map(ref=>{
                                    return <li><a href={ref.url} target="_blank" rel="noopener noreferrer">{ref.message}</a></li>
                                })}
                            </ul>
                        </>}
                        
                        { message.expanded? <button onClick={()=>setExpanded(message.requestId, false)} className='see-more'>{"<<see less"}</button>
                        :<button onClick={()=>setExpanded(message.requestId, true)} className='see-more'>{"see more>>"}</button>}
                        <Feedback id={message.requestId} feedback={message.feedback}/>
                    </div>
                </div>
                {message.expanded && <>
                    {message.message.reasoning && message.message.reasoning.length>0 && <ReasoningMessage reasoning={message.message.reasoning}/>}
                    {message.message.suggested && message.message.suggested.length>0 && <SuggestedQuestionsMessage program={message.program} questions={message.message.suggested}/>}
                </>}
            </>}
        </>
    ) 
})