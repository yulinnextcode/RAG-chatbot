import { PolicyEngineContextProvider } from "../Context"
import { PolicyEngineChatBotApp } from "./PolicyEngineChatBotApp";

export const PolicyEngineChatBot = () => { 
    
    return <div id='PolicyEngineChatBotContainer'>
        <PolicyEngineContextProvider> 
            <PolicyEngineChatBotApp/> 
        </PolicyEngineContextProvider>
    </div>
}