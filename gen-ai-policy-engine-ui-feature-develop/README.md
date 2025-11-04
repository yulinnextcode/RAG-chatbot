# GA Policy Engine Frontend


## Setup
The chatbot plugin is developed using React and packaged using Webpack. The final output includes _policy-engine.css_ and _policy-engine.js_ files, which need to be included in the client's webpage for the chatbot to function.

 

### Prerequisites 

Before proceeding with the setup, ensure that the following prerequisites are met: 
- Node.js and npm are installed on your development machine. 
- Access to the server where the final packaged files (_policy-engine.css_ and _policy-engine.js_) will be hosted. 

### Packaging the Application 

The application uses Webpack to bundle the source code into the final output files. The packaging process can be initiated using the following command: 

_npm run package -- --env BACKEND_API_URL=[Backend Gateway URL]_ 

Replace _[Backend Gateway URL]_ with the backend gateway URL.  

Upon successful execution, the packaged files (_policy-engine.css_ and _policy-engine.js_) will be generated and placed in the _dist_ folder. 

  
### Hosting the Packaged Files 

The packaged files need to be hosted on a server that is accessible to the end user's browser. Currently, these files are hosted in an AWS ECS container and can be accessed through AWS API Gateway. However, they can be hosted on any server of your choice. 
 
### Integrating the Chatbot Plugin 

To integrate the chatbot plugin into your webpage, insert the following lines of code into the HTML file of your webpage: 

```
<script defer="" src="[Application Load Balancer URL]/policy-engine.js"></script> 
<link rel="stylesheet" href="[Application Load Balancer URL]/policy-engine.css"> 
<div id="policy-engine"></div> 
```

Replace _[Application Load Balancer URL]_ with the URL where the _policy-engine.css_ and _policy-engine.js_ files are hosted. 

#### Placement of Integration Code 

Ideally, the above lines should be inserted at the end of the <body> tag in your webpage. However, they can be placed anywhere within the <body> tag. 

#### Example 

Here is an example of how the integration code would look in an HTML file: 
```
<!DOCTYPE html> 
<html lang="en"> 
<head> 
    <meta charset="UTF-8"> 
    <meta name="viewport" content="width=device-width, initial-scale=1.0"> 
    <title>Client's Webpage</title> 
</head> 
<body> 
    <!-- Other content of the webpage --> 

    <!-- Chatbot Plugin Integration --> 
    <script defer="" src="https://example.com/policy-engine.js"></script> 
    <link rel="stylesheet" href="https://example.com/policy-engine.css"> 
    <div id="policy-engine"></div> 
</body> 
</html> 
```


 

### Verification 

By following the steps outlined in this setup section, you will successfully integrate the chatbot plugin into your webpage. Ensure that the packaged files are hosted on a server accessible to the end user's browser and that the integration code is correctly placed within the _<body>_ tag of your HTML file. Follow the steps below to ensure everything is functioning as expected: 

 

#### Verifying Frontend Deployment 

To verify that the frontend components are correctly deployed, access the following URLs in your web browser: 

__CSS File:__ _[Frontend Gateway URL]/policy-engine.css_ 

__JavaScript File:__ _[Frontend Gateway URL]/policy-engine.js_ 

Replace _[Frontend Gateway URL]_ with the actual URL where the _policy-engine.css_ and _policy-engine.js_ files are hosted. If these files are correctly deployed, you should be able to view the contents of the CSS and JavaScript files in your browser. 

 

#### Verifying Chatbot Integration 

To verify that the chatbot application is correctly integrated into your webpage, open the webpage where the integration code was added. Look for the following indicator: 

__Chatbot Icon__: A blue chatbot icon should appear at the bottom right corner of the window. 

If the blue chatbot icon is visible, it confirms that the chatbot application is successfully integrated and ready for use. 

### Troubleshooting 

If you encounter any issues during the verification process, consider the following troubleshooting steps: 

__File Accessibility:__ Ensure that the policy-engine.css and policy-engine.js files are accessible via the provided URLs. Check for any network or permission issues that might prevent access. 

__Integration Code Placement:__ Verify that the integration code is correctly placed within the <body> tag of your HTML file. Ensure there are no typos or syntax errors in the script and link tags. 

__Browser Console:__ Check the browser console for any error messages related to the chatbot plugin. These messages can provide insights into what might be going wrong. 

By following these verification and troubleshooting steps, you can ensure that the chatbot plugin is correctly integrated and functioning on your webpage. 
 

 






## Dependencies
- process: "^0.11.10"
- react-icons: "^5.3.0"
- uuid: "^10.0.0"


## API
### Send message
Endpoint: /sendMessage 
#### Request
```
    {
        "sessionId": "Session UUID",
        "requestId": "Request UUID",
        "chainOfThought": "Y if a new program is selected",
        "prompt": "Prompt message",
        "prog": "Programe name",
        "timestamp": "Request timestamp"
    },
```

#### Responses
Succeed
```
    {
        "statusCode": 200,
        "body": {
            summary: "Response message",
            reasoning: [{
                message: "Reasoning content",
                references: "Reference",
                url: "Link to reference"
            },
            ...],
            suggested:[
                "Question 1",
                "Question 2",
                ....
            ],
            references: [
                {
                    message: "Reference content",
                    url: "Link to the reference"
                }
            ]
        },
    }
```

PII/PHI
```
    {
        "statusCode": 400,
        "body": "PII/PHI Detected in the prompt, please remove the concerning elements from the prompt and try again.",
    }
```

No Prompt Provided
```
    {
        "statusCode": 400,
        "body": "No Prompt Provided",
    }
```


No event received
```
    {
        "statusCode": 400,
        "body": "No event received",
    }
```

Irrelevant Questions
```
    {
        "statusCode": 400,
        "body": "I’m sorry, but I don’t fully understand your question. Could you please clarify your request, provide more context, or ask in a different way?"
    }
```

Server is busy
```
    {
        "statusCode": 429,
        "body": "Too Many Requests"
    }
```


Service Unavailable
```
    {
        "statusCode": 503,
        "body": "Service Unavailable"
    }
```

Maintenance
```
    {
        "statusCode": 503,
        "body": "Service is down for maintenance from 09/25/2024 to 09/28/2024"
    }
```

Gateway Timeout
```
    {
        "statusCode": 504,
        "body": "Gateway Timeout"
    }
```
### Renew Session
Endpoint: /extendSession 
#### Request
```
    {
        "sessionId": "Session UUID",
        "timestamp": "Request timestamp"
    },
```

#### Responses
Succeed
```
    {
        "statusCode": 200,
    }
```

Session not found
```
    { 
        "statusCode": 404, 
        "body": "Session not found." 
    } 
```
### Feedback
Endpoint: /feedback 
#### Request
```
    {
        "requestId": "Request UUID",
        "feedback": "UP_VOTE/DOWN_VOTE/CANCEL",
        "feedbackMessage": "Message"
    },
```

#### Responses
Succeed
```
    {
        "statusCode": 200,
        "body": "Thank you for your feedback!"
    }
```

Error:
```
    {
        "statusCode": 503,  
        "body": "Service Unavailable!" 
    } 
```

### Timeout 
Endpoint: /timeout 
#### Request
```
    {
        "sessionId": "Session UUID",
        "requestId": "Request UUID",
        "chainOfThought": "Y if a new program is selected",
        "prompt": "Prompt message",
        "prog": "Programe name",
        "timestamp": "Original request timestamp"
    },
```

#### Responses
Succeed
```
    {
        "statusCode": 200,
    }
```

Error
```
    {
        "statusCode": 503,
    }
```


## Additional Programs
To support additional programs, you need to add the following line for each program between line 21 and 23 of _src\policy-engine-chatbot\components\ChatbotWindow\components\UserInput.js_,

```
   <option value='[PROGRAM NAME]'>[PROGRAM NAME]</option>
```

Replace _[PROGRAM NAME]_ with the new program's name.  