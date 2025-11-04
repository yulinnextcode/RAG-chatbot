import './Loading.css'
import './BotMessage.css'
import React, { useEffect, useState, forwardRef } from 'react';
import { RiRobot3Line } from "react-icons/ri";

export const Loading = forwardRef(({}, ref) => {
    const [message, setMessage] = useState('.');
    useEffect(()=>{
        const interval = setInterval(() => setMessage(prev=>prev.length < 5 ? prev + '.' : '.'), 1000);

        return () => clearInterval(interval);
    },[])
    return(
        <div className='message-container'>
            <div className='message-icon'>
                <RiRobot3Line />
            </div>
            <div ref={ref} className="loading-message bot-message message">
                {message}
            </div>
        </div>
    ) 
})