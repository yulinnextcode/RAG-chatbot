import { createContext, useContext, useReducer } from "react";
import { SEND_MESSAGE, FEEDBACK, TIMEOUT, MessageType, PolicyEngineReducerActions, WindowSize, FeedbackType, TTL, WARNING_TIME, SESSION_EXPIRATION_WARNING_PERIOD, RESPONSE_TIMEOUT, EXTEND_SESSION } from "./constant";
import { v4 as uuid } from 'uuid'

const Context = createContext();    

const reducer = (state, action) => {
    switch(action.type) {
        case PolicyEngineReducerActions.ADD_MESSAGE:
            return {
                ...state,
                isWaitingforAnswer: action.payload.type===MessageType.USER_MESSAGE,
                chatHistory: [...state.chatHistory, action.payload],
                lastMessage: state.chatHistory.length
            } 
        case PolicyEngineReducerActions.RESET_SESSION:
            return {
                ...state,
                ttl: -1,
                isSessionExpiring: false,
                sessionId: uuid(),
                currentProgram: ""
            }
        case PolicyEngineReducerActions.TIMEOUT:
            return {
                ...state,
                isWaitingforAnswer: false,
                chatHistory: [...state.chatHistory, { 
                    type: MessageType.INFO,
                    message: "Your Internet connection is slow. Try again.", 
                }],
                lastMessage: state.chatHistory.length,
                isServerDown: false
            } 
        case PolicyEngineReducerActions.SERVER_DOWN:
            return {
                ...state,
                isWaitingforAnswer: false,
                chatHistory: [...state.chatHistory, action.payload],
                lastMessage: state.chatHistory.length,
                isServerDown: true
            } 
        case PolicyEngineReducerActions.CLICK_CHATBOT_BUTTON:
            return {
                ...state,
                isChatbotWindowOpen: !state.isChatbotWindowOpen
            };
        case PolicyEngineReducerActions.SET_CURRENT_PROGRAM:
            return {
                ...state,
                currentProgram: state.program
            };
        case PolicyEngineReducerActions.SET_PROGRAM:
            return {
                ...state,
                program: action.payload
            };
        case PolicyEngineReducerActions.SET_EXPANDED:
            return {
                ...state,
                chatHistory: state.chatHistory.map((message) => {
                    if(action.payload.requestId===message.requestId) {
                        return {
                            ...message,
                            expanded: action.payload.expanded
                        }
                    }
                    else {
                        return message
                    }
                })
            };
        case PolicyEngineReducerActions.SET_USER_MESSAGE:
            return {
                ...state,
                userMessage: action.payload
            };
        case PolicyEngineReducerActions.SET_CURRENT_FEEDBACK_ID:
            return {
                ...state,
                currentFeedbackId: action.payload
            }
        case PolicyEngineReducerActions.UPDATE_TTL:
            return {
                ...state,
                ttl: Date.now() + TTL,
                isSessionExpiring: false,
            }
        case PolicyEngineReducerActions.SET_WINDOW_SIZE:
            return {
                ...state,
                windowSize: action.payload
            }   
        case PolicyEngineReducerActions.CANCEL_FEEDBACK:
            return {
                ...state,
                currentFeedbackId: -1,
                chatHistory: state.chatHistory.map((message) => {
                    if(action.payload===message.requestId) {
                        return {
                            ...message,
                            feedback: {}
                        }
                    }
                    else {
                        return message
                    }
                })
            }
        case PolicyEngineReducerActions.SET_IS_SESSION_EXPIRING:
            return {
                ...state,
                isSessionExpiring: true,
            }
        case PolicyEngineReducerActions.SET_FEEDBACK:
            return {
                ...state,
                currentFeedbackId: -1,
                chatHistory: state.chatHistory.map((message) => {
                    if(action.payload.id===message.requestId) {
                        return {
                            ...message,
                            feedback: {
                                message: action.payload.message,
                                type: action.payload.type,
                            }
                        }
                    }
                    else {
                        return message
                    }
                })
            }
    }
}

const usePolicyEngineContext = () => {
    const context = useContext(Context);

    if(context === undefined) {
        throw new Error('usePolicyEngineContext must be used within PolicyEngineContextProvider')
    }

    return context;
}

const PolicyEngineContextProvider = ({children}) => {
    const [policyEngineState, policyEngineDispatch] = useReducer(reducer, {
        sessionId: uuid(),
        isChatbotWindowOpen: false,
        isWaitingforAnswer: false,
        userMessage: "",
        program: "",
        currentProgram: "",
        chatHistory: [],
        currentFeedbackId: -1,
        windowSize: WindowSize.MIN,
        lastMessage: "",
        isServerDown: false,
        isSessionExpiring: false,
        ttl: -1,
    });

    const setExpanded = (requestId, expanded) => {
        policyEngineDispatch({
            type: PolicyEngineReducerActions.SET_EXPANDED,
            payload: {requestId, expanded}
        })
    }

    const setCurrentFeedbackId = (id) => {
        policyEngineDispatch({
            type: PolicyEngineReducerActions.SET_CURRENT_FEEDBACK_ID,
            payload: id
        })
    }

    const updateTtl = () => {
        policyEngineDispatch({
            type: PolicyEngineReducerActions.UPDATE_TTL
        })
    }

    const renewCurrentSession = async () => {
        try{ 
            const request = await fetch(EXTEND_SESSION, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "sessionId": policyEngineState.sessionId,
                    "timestamp": new Date().toLocaleString("en-US", {timeZone: 'America/New_York'})
                })
            })  
            
            switch(request.status) {
                case 200: 
                    updateTtl();
                    policyEngineDispatch({
                        type: PolicyEngineReducerActions.ADD_MESSAGE,
                        payload: {
                            type: MessageType.INFO,
                            message: `Thank you. Please continue.`
                        }
                    }); 
                break;
                case 404:
                    policyEngineDispatch({
                        type: PolicyEngineReducerActions.RESET_SESSION, 
                    })
                    policyEngineDispatch({
                        type: PolicyEngineReducerActions.ADD_MESSAGE,
                        payload: {
                            type: MessageType.ERROR,
                            message: `Your session has ended. You can ask a question to start a new session.`
                        }
                    })
                    break;
                default:
                    policyEngineDispatch({
                        type: PolicyEngineReducerActions.RESET_SESSION, 
                    })
                    policyEngineDispatch({
                        type: PolicyEngineReducerActions.SERVER_DOWN,
                        payload: {
                            type: MessageType.ERROR,
                            message: "Service Unavailable!",
                            feedback: '',
                        }
                    })

            }
        }
        catch {
            policyEngineDispatch({
                type: PolicyEngineReducerActions.RESET_SESSION, 
            })
            policyEngineDispatch({
                type: PolicyEngineReducerActions.SERVER_DOWN,
                payload: {
                    type: MessageType.ERROR,
                    message: "Service Unavailable!",
                    feedback: '',
                }
            })
        }  
    }

    const cancelFeedback = async(id) => {
        try {
            const request = await fetch(FEEDBACK, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "requestId": id,
                    "feedback": FeedbackType.CANCEL
                })
            })

            if(request.status===200) { 
                policyEngineDispatch({
                    type: PolicyEngineReducerActions.CANCEL_FEEDBACK,
                    payload: id
                })
                updateTtl();
            }
            else {
                policyEngineDispatch({
                    type: PolicyEngineReducerActions.SERVER_DOWN,
                    payload: {
                        type: MessageType.ERROR,
                        message: "Service Unavailable!",
                        feedback: '',
                    }
                })
            }
        }
        catch {
            policyEngineDispatch({
                type: PolicyEngineReducerActions.SERVER_DOWN,
                payload: {
                    type: MessageType.ERROR,
                    message: "Service Unavailable!",
                    feedback: '',
                }
            })
        }        
    }

    const resetSession = () => {
        policyEngineDispatch({
            type: PolicyEngineReducerActions.RESET_SESSION, 
        })
        policyEngineDispatch({
            type: PolicyEngineReducerActions.ADD_MESSAGE,
            payload: {
                type: MessageType.INFO,
                message: `Thank you. Your current session has ended. Asking a new question will start a new session.`
            }
        })
    }
    
    const setFeedback = async (id, type, message) => {
        try {
            const request = await fetch(FEEDBACK, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "requestId": id,
                    "feedback": type,
                    "feedbackMessage": message
                })
            })  

            if(request.status===200) { 
                policyEngineDispatch({
                    type: PolicyEngineReducerActions.SET_FEEDBACK,
                    payload: {
                        id,
                        type,
                        message
                    }
                })
                updateTtl();
            }
            else {
                setCurrentFeedbackId(-1);
                policyEngineDispatch({
                    type: PolicyEngineReducerActions.SERVER_DOWN,
                    payload: {
                        type: MessageType.ERROR,
                        message: "System error",
                        feedback: '',
                    }
                })
            }

            updateTtl();
        }
        catch {
            policyEngineDispatch({
                type: PolicyEngineReducerActions.SERVER_DOWN,
                payload: {
                    type: MessageType.ERROR,
                    message: "System error",
                    feedback: '',
                }
            })
        }
    }

    const submitQuestion = async (userMessage, userProgram) => {
        const requestId = uuid();
        const message = userMessage || policyEngineState.userMessage;
        const program = userProgram || policyEngineState.program;
        if(message.length>0) {
            const chainOfThought = policyEngineState.currentProgram !== program;
            if(chainOfThought) {
                policyEngineDispatch({
                    type: PolicyEngineReducerActions.ADD_MESSAGE,
                    payload: {
                        type: MessageType.INFO,
                        message: `You started a new conversation regarding ${program} program.`,
                        program: program,
                        requestId
                    }
                })
                setCurrentProgram();
            }
            setProgram(program);
            
            policyEngineDispatch({
              type: PolicyEngineReducerActions.ADD_MESSAGE,
              payload: {
                type: MessageType.USER_MESSAGE,
                message: message,
                program: policyEngineState.currentProgram,
                requestId
              }
            })

            policyEngineDispatch({
                type: PolicyEngineReducerActions.SET_USER_MESSAGE,
                payload: ''
            })  

            const body = JSON.stringify({
                "sessionId": policyEngineState.sessionId,
                "requestId": requestId,
                "chainOfThought": chainOfThought?'Y':'N',
                "prompt": message,
                "prog": program,
                "timestamp": new Date().toLocaleString("en-US", {timeZone: 'America/New_York'})
            });

        try{ 
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), RESPONSE_TIMEOUT);

            const request = await fetch(SEND_MESSAGE, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body,
                signal: controller.signal  
            }) 

    
            clearTimeout(id);
            
            let result;

            switch(request.status) {
                case 200:
                    result = await request.json();            
                    policyEngineDispatch({
                        type: PolicyEngineReducerActions.ADD_MESSAGE,
                        payload: {
                            type: MessageType.BOT_MESSAGE,
                            message: result,
                            feedback: '',
                            program: program,
                            expanded: false,
                            requestId
                        }
                    })
                    
                    updateTtl();
                    break;
                case 400:
                    result = await request.json();
                    policyEngineDispatch({
                        type: PolicyEngineReducerActions.ADD_MESSAGE,
                        payload: {
                            type: MessageType.ERROR,
                            message: result,
                            feedback: '',
                            requestId
                        }
                    })
                    updateTtl();
                    break;
                case 429:
                case 504:
                    result = await request.json();
                    policyEngineDispatch({
                        type: PolicyEngineReducerActions.ADD_MESSAGE,
                        payload: {
                            type: MessageType.INFO,
                            message: "System is busy. Try again.",
                            feedback: '',
                            requestId
                        }
                    })
                    break;
                case 503:
                    result = await request.json();
                    policyEngineDispatch({
                        type: PolicyEngineReducerActions.SERVER_DOWN,
                        payload: {
                            type: MessageType.ERROR,
                            message: result,
                            feedback: '',
                            requestId
                        }
                    })
                    break; 
                default: 
                    policyEngineDispatch({
                        type: PolicyEngineReducerActions.SERVER_DOWN,
                        payload: {
                            type: MessageType.ERROR,
                            message: "System error",
                            feedback: '',
                            requestId
                        }
                    })
                }
            }
            catch (error) {
                switch(error.name){
                    case 'AbortError':
                        try {
                            const request = await fetch(TIMEOUT, {
                                method: 'POST',
                                headers: {
                                    'Accept': 'application/json',
                                    'Content-Type': 'application/json',
                                },
                                body,
                            });

                            if(request.status === 200) {
                                policyEngineDispatch({
                                    type: PolicyEngineReducerActions.TIMEOUT
                                });
                                updateTtl();
                            }
                            else {
                                policyEngineDispatch({
                                    type: PolicyEngineReducerActions.SERVER_DOWN,
                                    payload: {
                                        type: MessageType.ERROR,
                                        message: "System error",
                                        feedback: '',
                                        requestId
                                    }
                                })
                            }
                        }
                        catch {
                            policyEngineDispatch({
                                type: PolicyEngineReducerActions.SERVER_DOWN,
                                payload: {
                                    type: MessageType.ERROR,
                                    message: "System error",
                                    feedback: '',
                                    requestId
                                }
                            })
                        }
                        break;
                    default: 
                        policyEngineDispatch({
                            type: PolicyEngineReducerActions.SERVER_DOWN,
                            payload: {
                                type: MessageType.ERROR,
                                message: "System error",
                                feedback: '',
                                requestId
                            }
                        })
                }
                
            }
            
        }
    }

    const switchIsChatbotWindowOpen = () => {
        policyEngineDispatch({type: PolicyEngineReducerActions.CLICK_CHATBOT_BUTTON})
    }

    const setWindowSize = (size) => {
        policyEngineDispatch({
            type: PolicyEngineReducerActions.SET_WINDOW_SIZE,
            payload: size
        })
    }
    
    const setProgram = (value) => {
        policyEngineDispatch({
        type: PolicyEngineReducerActions.SET_PROGRAM,
        payload: value
        })
    }
    
    const setCurrentProgram = () => {
        policyEngineDispatch({
            type: PolicyEngineReducerActions.SET_CURRENT_PROGRAM
        })
    }

    const setUserMessage = (value) => {
        policyEngineDispatch({
        type: PolicyEngineReducerActions.SET_USER_MESSAGE,
        payload: value
        })
    }

    return (
        <Context.Provider value={{
            policyEngineDispatch,
            submitQuestion,
            cancelFeedback,
            setFeedback,
            switchIsChatbotWindowOpen,
            setProgram,
            setUserMessage,
            setCurrentFeedbackId,
            setWindowSize,
            updateTtl,
            resetSession,
            renewCurrentSession,
            setExpanded,
            ...policyEngineState
        }}>
            {children}
        </Context.Provider>
    )
}

export {usePolicyEngineContext, PolicyEngineContextProvider, PolicyEngineReducerActions}