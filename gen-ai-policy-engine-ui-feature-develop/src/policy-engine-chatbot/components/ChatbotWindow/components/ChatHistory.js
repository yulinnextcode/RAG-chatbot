import { Notice } from "./Notice"
import './ChatHistory.css'
import { usePolicyEngineContext } from "../../../../Context";
import { MessageType } from "../../../../constant";
import { UserMessage } from "./UserMessage";
import { useEffect, useRef } from "react";
import { Loading } from "./Loading";
import { BotMessage } from "./BotMessage";
import { InfoMessage } from "./InfoMessage"; 
import { ErrorMessage } from "./ErrorMessage";
import { TimeoutMessage } from "./TimeoutMessage";

export const ChatHistory = () => {
    const {isWaitingforAnswer, chatHistory, lastMessage, isSessionExpiring} = usePolicyEngineContext();
    const lastMessageRef = useRef();
    useEffect(()=>{
        if(lastMessageRef?.current) {
            lastMessageRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [lastMessage, isSessionExpiring])

    return <div className='chat-history'>
        <Notice/>
        {chatHistory.map((message, i)=>{
            const ref = lastMessage === i ? lastMessageRef:null; 
            switch(message.type) {
                case MessageType.USER_MESSAGE: return <UserMessage key={i} message={message}/>
                case MessageType.BOT_MESSAGE: return <BotMessage key={i} ref={ref} message={message} i={i}/>
                case MessageType.INFO: return <InfoMessage key={i} message={message} />
                case MessageType.ERROR: return <ErrorMessage message={message} />
            }
        })}
        {isSessionExpiring && <TimeoutMessage ref={lastMessageRef}/>}
        {isWaitingforAnswer && <Loading ref={lastMessageRef}/>}
        <div className="bottom-margin"></div>
    </div>
}