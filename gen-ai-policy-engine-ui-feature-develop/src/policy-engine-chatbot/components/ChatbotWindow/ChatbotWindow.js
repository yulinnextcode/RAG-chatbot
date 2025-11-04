import React from "react";
import './ChatbotWindow.css' 
import { UserInput } from "./components/UserInput";
import { ChatHistory } from "./components/ChatHistory";
import { MdOutlineZoomInMap } from "react-icons/md";
import { MdOutlineZoomOutMap } from "react-icons/md";
import { usePolicyEngineContext } from "../../../Context";
import { WindowSize } from "../../../constant";


export const ChatbotWindow = () => {
    const {setWindowSize, windowSize} = usePolicyEngineContext();

    return <div className={`window ${windowSize}`.toLowerCase()}>
        
        <button className="resize-button" onClick={() => setWindowSize(windowSize==WindowSize.MAX?WindowSize.MIN:WindowSize.MAX)} >
           {windowSize==WindowSize.MAX && <MdOutlineZoomInMap />}
           {windowSize==WindowSize.MIN && <MdOutlineZoomOutMap />}
        </button>
        <h3 className='window-header'>Georgia Policy Engine</h3>
        <ChatHistory/>
        <UserInput/>
    </div>
}