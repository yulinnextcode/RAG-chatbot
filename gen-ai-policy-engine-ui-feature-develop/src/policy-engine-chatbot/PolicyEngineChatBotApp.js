import React, { useEffect } from "react";
import { ChatbotButton } from "./components/ChatbotButton/ChatbotButton";
import { ChatbotWindow } from "./components/ChatbotWindow/ChatbotWindow";
import { usePolicyEngineContext } from "../Context";
import { PolicyEngineReducerActions, SESSION_EXPIRATION_WARNING_PERIOD, TTL } from "../constant";

export const PolicyEngineChatBotApp = () => {
    const {isChatbotWindowOpen, ttl, policyEngineDispatch} = usePolicyEngineContext();

    useEffect(() => { 
        let intervalId;
        if(ttl>0) {
            intervalId = setInterval(() => {
                policyEngineDispatch({
                    type: PolicyEngineReducerActions.SET_IS_SESSION_EXPIRING
                })
            }, TTL - SESSION_EXPIRATION_WARNING_PERIOD); 
        }
        else {
            clearInterval(intervalId);
        }
        return () => clearInterval(intervalId);
    }, [ttl]);

    return <>
        {isChatbotWindowOpen && <ChatbotWindow/>}
        <ChatbotButton/>
    </>
}