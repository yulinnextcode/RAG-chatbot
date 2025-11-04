import { useEffect, useRef } from "react"
import "./UserMessage.css"
import { TbUserQuestion } from "react-icons/tb";

export const UserMessage = ({message}) => {
    const messageRef = useRef();
    useEffect(()=> {
        messageRef.current.focus();
    })
    return (
        
        <div className='message-container user-message-container'>
            <div ref={messageRef} className='user-message message'>
                {message.message}  
            </div>
            <div className='message-icon'>
                <TbUserQuestion />
            </div>
        </div>
        
        
    )
}