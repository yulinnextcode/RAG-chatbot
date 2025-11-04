import React from "react";
import chatIcon from '../../../icons/messenger-cx-chat-icon.svg'
import chatCloseIcon from '../../../icons/messenger-cx-chat-close-icon.svg'
import './ChatbotButton.css' 
import { usePolicyEngineContext } from "../../../Context";

export const ChatbotButton = () => {
    const {switchIsChatbotWindowOpen, isChatbotWindowOpen} = usePolicyEngineContext()

    return ( 
            <button type="button" id="policy-engine-chatbot-button" className={'policy-engine-chatbot-botton'} aria-label="show chat window" onClick={()=>switchIsChatbotWindowOpen()}>
                <div className="v-btn__content">
                {isChatbotWindowOpen ? 
                    <img src={chatCloseIcon}/> 
                : 
                    <img src={chatIcon}/>
                }
                </div>
            </button> 
    )
}