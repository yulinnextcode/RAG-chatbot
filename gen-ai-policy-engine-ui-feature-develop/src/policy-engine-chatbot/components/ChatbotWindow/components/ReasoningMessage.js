import './ReasoningMessage.css';

export const ReasoningMessage = ({reasoning}) => {

    return (
        <div className='message-container'>
            <div className='message-icon'> 
            </div>
            <div className='reasoning-message message'>  
                <h4>Reasonings</h4>
                <ul>
                    {reasoning.map(r=> {
                        return <li>{r.message} (<a href={r.url} target="_blank" rel="noopener noreferrer">{r.references}</a>)</li>
                    })}
                </ul> 
            </div>
        </div>
    ) 
}