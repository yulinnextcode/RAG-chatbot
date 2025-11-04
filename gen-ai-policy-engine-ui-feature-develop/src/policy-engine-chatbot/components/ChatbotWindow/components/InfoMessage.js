import './InfoMessage.css';

export const InfoMessage = ({message}) => {

    return (
        <div className='message-container'>
            <div className='message-icon'> 
            </div>
            <div className='info-message message'> 
                {message.message} 
            </div>
        </div>
    ) 
}