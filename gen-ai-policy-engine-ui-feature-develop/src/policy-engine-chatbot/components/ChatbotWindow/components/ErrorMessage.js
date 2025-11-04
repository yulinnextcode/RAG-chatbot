import { forwardRef, useEffect, useRef } from 'react';
import './ErrorMessage.css';

export const ErrorMessage = forwardRef(({message}, ref) => {
    return (
        <div className='message-container'>
            <div className='message-icon'> 
            </div>
            <div ref={ref} className='error-message message'>
                {message.message}
            </div>
        </div>
    ) 
})