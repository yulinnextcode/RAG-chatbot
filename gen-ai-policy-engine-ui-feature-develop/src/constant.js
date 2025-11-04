export const MessageType ={
    USER_MESSAGE: 'USER_MESSAGE',
    BOT_MESSAGE: 'BOT_MESSAGE',
    INFO: 'INFO',
    WARNING: 'WARNING',
    ERROR: 'ERROR',
}

export const PolicyEngineReducerActions = {
    CLICK_CHATBOT_BUTTON: 'CLICK_CHATBOT_BUTTON',
    TIMEOUT: 'TIMEOUT',
    SERVER_DOWN: 'SERVER_DOWN',
    ADD_MESSAGE: 'ADD_MESSAGE',
    SET_FEEDBACK: 'SET_FEEDBACK',
    CANCEL_FEEDBACK: 'CANCEL_FEEDBACK',
    SET_USER_MESSAGE: 'SET_USER_MESSAGE',
    SET_PROGRAM: 'SET_PROGRAM',
    SET_CURRENT_PROGRAM: 'SET_CURRENT_PROGRAM',
    SET_CURRENT_FEEDBACK_ID: 'SET_CURRENT_FEEDBACK_ID',
    SET_WINDOW_SIZE: 'SET_WINDOW_SIZE',
    SET_IS_SESSION_EXPIRING: 'SET_IS_SESSION_EXPIRING',
    RESET_SESSION: 'RESET_SESSION',
    UPDATE_TTL: "UPDATE_TTL"
}

export const FeedbackType = {
    UP_VOTE: 'UP_VOTE',
    DOWN_VOTE: 'DOWN_VOTE',
    CANCEL: 'CANCEL',
}

export const WindowSize = {
    MIN: 'MIN',
    MAX: 'MAX'
}

const BACKEND_SERVER_URL = process.env.BACKEND_API_URL || `${window.location.protocol}//${window.location.hostname}:${window.location.port}`;
export const SEND_MESSAGE = `${BACKEND_SERVER_URL}/sendMessage`
export const FEEDBACK = `${BACKEND_SERVER_URL}/feedback`
export const TIMEOUT = `${BACKEND_SERVER_URL}/timeout`
export const EXTEND_SESSION = `${BACKEND_SERVER_URL}/extendSession`

export const RESPONSE_TIMEOUT = process.env.RESPONSE_TIMEOUT || 40000;

export const TTL = process.env.TTL || 1800000;
export const SESSION_EXPIRATION_WARNING_PERIOD = process.env.SESSION_EXPIRATION_WARNING_PERIOD || 300000;