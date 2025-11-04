import { forwardRef, useEffect, useState } from 'react';
import { PolicyEngineReducerActions, usePolicyEngineContext } from '../../../../Context';
import './TimeoutMessage.css';
import { getTimeRemain } from '../../../../utils';
import { MessageType, SESSION_EXPIRATION_WARNING_PERIOD } from '../../../../constant';

export const TimeoutMessage = forwardRef(({}, ref) => {  
    const {ttl, renewCurrentSession, resetSession} = usePolicyEngineContext();
    const [timeRemain, setTimeRemain] = useState(()=>getTimeRemain(ttl));

    useEffect(() => {
        const intervalId = setInterval(() => {
            setTimeRemain(getTimeRemain(ttl));
        }, 1000);
 
        return () => clearInterval(intervalId);
    }, []);

    useEffect(() => {
        const intervalId = setInterval(() => {
            resetSession();
        }, SESSION_EXPIRATION_WARNING_PERIOD);
 
        return () => clearInterval(intervalId);
    }, []);

    return (
        <div className='message-container'>
            <div className='message-icon'> 
            </div>
            <div ref={ref} className='timeout-message message'> 
                Your session will end in {timeRemain}. Do you want to continue? You can also ask a new question or provide a feedback to continue in the current session.
                <div><button onClick={()=>renewCurrentSession()}>Yes, continue</button> <button onClick={()=>resetSession()}>No, I finished</button></div>
            </div>
        </div>
    )
})