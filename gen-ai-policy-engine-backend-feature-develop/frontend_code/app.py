from flask import Flask, request, jsonify
from datetime import datetime
print('started')
print(datetime.now())
import boto3
import json
import botocore
import weaviate
from weaviate.connect import ConnectionParams
from weaviate.classes.init import AdditionalConfig, Timeout, Auth
from weaviate.classes.query import MetadataQuery
import weaviate.classes as wvc
from weaviate.classes.query import Filter
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import BedrockChat
import oracledb
from llm_guard.input_scanners import Regex
from llm_guard.vault import Vault
from llm_guard.input_scanners import Anonymize
from llm_guard.input_scanners.regex import MatchType
from llm_guard import scan_prompt
import time
from flask_cors import CORS
from flask_caching import Cache
import threading
import cx_Oracle
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import os
import re
import random
import yaml

with open("config.yml", "r") as f:
    config_data=yaml.safe_load(f)

#get oracle credentials from aws secrets
def get_oracle_secret():

    secret_name = config_data['oracle_secret']['secret_name']
    region_name = config_data['oracle_secret']['region_name']

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name=config_data['oracle_secret']['service_name'],
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except botocore.exceptions.ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

#get weaviate credentials
def get_weaviate_secret():

    secret_name = config_data['weaviate_secret']['secret_name']
    region_name = config_data['weaviate_secret']['region_name']

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name=config_data['weaviate_secret']['service_name'],
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except botocore.exceptions.ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)


#Instantiate Flask app
app = Flask(__name__)
CORS(app)
cache = Cache(app)
#Limiting the number of requests to be handled to 50
limiter = Limiter(get_remote_address, app=app, default_limits=config_data['app']['request_per_limit'])
    
#Instantiate the parameters and other required variables
modelId = config_data['app']['titan_model_id']
accept = config_data['app']['accept']
contentType = config_data['app']['contentType']
client_titan = boto3.client('bedrock-runtime', region_name=config_data['app']['region_name'])
username = get_oracle_secret()['username']
password = get_oracle_secret()['password']
password_weaviate = get_weaviate_secret()['password_frontend']
hostname =  os.environ['oracle_hostname']
port = config_data['app']['port']
service_name = os.environ['oracle_service']
app.config['CACHE_TYPE'] = 'SimpleCache'  # You can use Redis, Memcached, etc.
app.config['CACHE_DEFAULT_TIMEOUT'] = config_data['app']['SESSION_TTL']  # Default cache timeout of 10 minutes
client = None
memory = None
connection = None
memory_store = {}
active_sessions = {}
condense_question_prompt = None
llm = None
initialization_successful = True
SESSION_TTL = config_data['app']['SESSION_TTL']
pool = None
# limiter = None
links = {
'SNAP': 'https://gadhs.gitlab.io/pamms/dfcs/snap/appendix-e/', 
'Medicaid': 'https://gadhs.gitlab.io/pamms/dfcs/medicaid/appendix-e/',
'TANF':'https://gadhs.gitlab.io/pamms/dfcs/tanf/appendix-e/'
}
references = {
'included in an AU':'included in an MAGI AU',
"for the children based on client statement":"for the children based on A/R's statement to determine the MAGI AU and BG, Non-MAGI AU and BG composition if conflicting or questionable",
'for a 3 year old':'for a 3 year old 149% child 1-5 and 247% PCK',
'giving away a horse-drawn buggy used for transportation for a NH applicant': 'a transferred asset horse drawn buggy other than a homeplace excluded under FBR policy',
'RSDI retirement': 'RSDI Retirement',                                         
'retro months': 'retroactive medicaid',                                       
'Q track': 'Q track income and resource',                                     
'horse-drawn':'animal-drawn',
'buggy':'vehicle',
'carriage':'vehicle',
'QTrack' : '(QMB,SLMB,QI-1)',
'QTrack COA' : '(QMB,SLMB,QI-1)',
'felon':'felony',
'Dad' : 'Dad MAGI BG',
'taxes': 'taxes tax filer',
'shred': 'destroy',
'retirement':'retirement funds annuities resources 401K',
'401K': 'retirement funds annuities resources 401K',
'PGW':'PGW Pregnant Woman',
"""mother's income""": """mother's BG income""",
'Pregnant woman Medicaid' :'PGW',
'What do I do if someone':'What is detailed contact phone, email, mailing and website if someone',
'gives me a fake':'gives AU a fake or inconsistent with pre-existing information or counterfeit or altered',
'Pregnant Woman Medicaid' :'PGW Newborn',
'discharge 59' :'DMA-59 assistance unit (AU) may provide verification using any of the following methods',
'birth of a baby':'birth of a baby meaning increase or decrease in AU or BG size',
'mileage': 'Medically Needy Mileage Re-Imbursement Rate',
'If an application was closed':'If an application not assistance cases was closed',
'verification within 90 days':'verification within 90 days? This application is not ongoing/rewnal case, does it have 90 day grace period',
'July and August 2022 coverage':'coverage can or cannot be transmitted electronically',
#
'exclude one of my children':'exclude one of my children who may be SFU member',
'her father provides for her':'her father provides for her? What are members of the SFU',
'following customer within the degree of relationship': 'following relationships meet the relationship requirement',
"seeking TANF as a payee": "receiving cash assistance on the child's behalf",
"that she is applying for TANF for": "receiving cash assistance on the child's behalf. what other relationship meet the relationship requirement",
'two parent household receive TANF':'dependent child eligible for cash assistance with deprivation',
'if I want to receive TANF':'if I want to be included in the AU',    
'receive TANF if I have a felony conviction':'be included in the AU if I have a felony conviction? Which certain felon crime are considered',
'receive TANF if I have legal guardianship of my cousin':'receive TANF if I have legal guardianship of my cousin? What relationships meet the relationship requirements',
'apply for TANF for a foster child':'apply for TANF for a foster child? What if only dependent child',
'TANF recipients':'AU recipients',
'still TANF eligible':'be included in AU? Dependent child need work requirements of the TANF program',
'age limits':'age requirements',
'is also in the home':'is also living in the home or SSI',
'following customer':'following relation',
'apply for GRG':'apply for GRG two types and what criteria to receive TANF cash assistance',
'add a child to a TANF case':'determine ongoing eligibility and steps to add AU member and change AU composition',
'Can a minor':'Can a minor who is pregnant applicant',
'GRG eligibility criteria':'GRG eligibility criteria to receive TANF',
'TANF Work Participation Requirements':'Work Requirements',
"TANF for my cousin's children":"TANF for my cousin's children and be included in the AU",
'eligibility criteria for TANF Work Requirement Exemptions':'eligibility criteria that make a parent eligible for a TANF Work Requirement Exemption? Ineligible conditions',
'if I am disabled':'if I am disabled or with a disability/limitation',
'for living arrangements for a child':'for living with a child or a specified relative',
#
'gross income limit':'Maximum Gross Monthly Income, Maximum Net Monthly Income, Monthly Gross Income Limit and Maximum Allotments'
}

references_llm_scan = {
'Bendex': 'Benefit Data Exchange system',
'bendex': 'Benefit Data Exchange system'
}

#Initialize Oracle, LLM, Weaviate Resources
def initialize_resources():
    global pool, client, memory, connection, condense_question_prompt, llm, initialization_successful
    try:
        #Create Oracle Connection Pool to ensure smooth concurrency of actions
        if pool is None:
                pool = cx_Oracle.SessionPool(
                user = username,
                password = password,
                dsn = oracledb.makedsn(hostname, port, service_name=service_name),
                min = config_data['oracle_connection_pool']['min'],
                max = config_data['oracle_connection_pool']['max'],
                increment = config_data['oracle_connection_pool']['increment'],
                threaded = True,
                wait_timeout = config_data['oracle_connection_pool']['wait_timeout']
        )
        if pool is not None:
                print('oracle connection successful')
        else:
                print('oracle no success')    
        
        #Create Weaviate Connection
        print(f"Weaviate client status before initialization: {client}")
        if client is not None:
            client = None
        else:
            pass
        if client is None:
            host_dns = os.environ['weaviate_hostname']
            client = weaviate.WeaviateClient(
                connection_params=ConnectionParams.from_params(
                    http_host=host_dns,
                    http_port=config_data['weaviate_client']['http_port'],
                    http_secure=False,
                    grpc_host=host_dns,
                    grpc_port=config_data['weaviate_client']['grpc_port'],
                    grpc_secure=False,
                ),
                auth_client_secret=Auth.api_key(password_weaviate),
                additional_config=AdditionalConfig(
                    timeout=Timeout(init=config_data['weaviate_client']['timeout_init'], query=config_data['weaviate_client']['timeout_query'], insert=config_data['weaviate_client']['timeout_insert']),
                ),
                skip_init_checks=True
            )
            client.connect()
            if client:
               print('weaviate success')
            else:
               print('connection to weaviate unsuccessful')
            
        #Creating template to have llm model re-phrase the question based on chain of thought
        if condense_question_prompt is None:
            condense_template = """If the question is referencing the chat history, incorporate the exact original question along with the necessary chat history to form a simple standalone question. This new standalone question should be clear and understandable on its own.
            If the question is not referencing the chat history, return the exact original question without any modification to form a simple standalone question. This new standalone question should be clear and understandable on its own.
            Chat History:\"""
            {chat_history}
            \"""
            Follow Up Input: \"""
            {question}
            \"""
            Standalone question:"""
            condense_question_prompt = PromptTemplate(input_variables=["chat_history", "question"], template=condense_template)
        
        #Instantiating the llm connection
        if llm is None:
            lm = BedrockChat(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
                          client=client_titan,
                          model_kwargs={"max_tokens": config_data['llm']['max_tokens'],
                                        "temperature": config_data['app']['temperature']})

#            llm = BedrockChat(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",

    except Exception as e:
        print(e)
        initialization_successful = False

#Exponential Backoff Strategy which will handle remainder requests that can't get handled by Flask app. Retries will happen and if resources don't become available within 30 seconds, the request will get rejected.
def exponential_backoff_retry(retries=config_data['ebo']['retries'], base_delay=config_data['ebo']['base_delay'], max_delay=config_data['ebo']['max_delay']):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    wait_time = min(max_delay, base_delay * (2 ** attempt) + random.uniform(0, 1))
                    print(f"Attempt {attempt}/{retries} failed: {e}. Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
            raise Exception(f"All {retries} attempts failed.")
        return wrapper
    return decorator

#Function to take take care of session managemenet. Expired sessions are removed from the memory
def monitor_sessions():
    """
    Continuously monitors the active_sessions dictionary and removes expired sessions.
    """
    while True:
        current_time = time.time()
        expired_sessions = []  # Reinitialize the expired_sessions list at the start of each iteration
        
        for session_id, last_activity_time in list(active_sessions.items()):
            time_left = SESSION_TTL - (current_time - last_activity_time)
            
            if time_left <= 0:
                # Session has expired, mark it for removal
                expired_sessions.append(session_id)
        
        # Remove expired sessions from memory_store and active_sessions
        for session_id in expired_sessions:
            print(f"Session {session_id} has expired and is being removed.")
            if session_id in memory_store:
                del memory_store[session_id]  # Remove from memory_store
            del active_sessions[session_id]  # Remove from active_sessions
        
        # Clean up the expired_sessions list after processing
        expired_sessions.clear()
        
        # Sleep for a minute before scanning again
        time.sleep(60)

#Starting the session monitor in the backend
def start_session_monitor():
    """
    Starts the session monitor in a background thread.
    This thread runs continuously and checks session expiry.
    """
    monitor_thread = threading.Thread(target=monitor_sessions)
    monitor_thread.daemon = True  # Ensures the thread will close when the main program exits
    monitor_thread.start()

#Function takes in the question asked by user, consideres the chain of thought boolean value and session_id
def get_question_from_cot(session_id, prompt, boolean):
    current_time = time.time()
    
    #If session_id not present in memory store, then create a new memory instance for that session_id, store the question in the buffer window memory
    # and store the session_id and corresponding memory in the memory store
    if session_id not in memory_store:
        memory = ConversationBufferWindowMemory(
            k=config_data['cbwm']['K'],  # Keeps the last 5 questions, each asked question is having two set of questions - one original, one generated by question_generator
            memory_key="chat_history",
            output_key="answer"
        )
        question_generator = LLMChain(
            llm=llm,
            prompt=condense_question_prompt,
            memory=memory,
            output_key="answer"
        )
        # Initialize a new memory object if one doesn't exist for the session
        print('executing not in session_id block')
        output = question_generator.predict(question = prompt)
        memory_store[session_id] = memory
    
    #If session_id exists in the memory store, then fetch the memory. 
    else:
        memory = memory_store[session_id]
        question_generator = LLMChain(
            llm=llm,
            prompt=condense_question_prompt,
            memory=memory,
            output_key="answer"
        )
        #if boolean is set to clear by 'Y' value, clear the memory. Store the new question in memory then.
        if boolean == 'Y':
            memory.clear()
            print('executing in session_id block but clear memory')
            output = question_generator.predict(question = prompt)
            memory_store[session_id] = memory
        else:
            #if boolean is not set to clear, check the number of questions in memory. if less than or equal to 10, then continue appending the questions to it. Will save up to 5 questions.
            # note: a conversation buffer window memory will store 2 questions for each question - one original question and one output as part of question_generator.predict value
            # hence checking if count is less than or equal 10.
            if len(memory.chat_memory.messages)<= config_data['cbwm']['K']:
                print('executing in session_id block but len<10')
                print(len(memory.chat_memory.messages))
                print('\n')
                print('chat_history')
                print(memory.chat_memory.messages)
                output = question_generator.predict(question = prompt)
                memory_store[session_id] = memory         
            else:
                # When 6th question is asked, the first question from the list is popped out and 6th question is appened. Evenutally, maintaining the 5 questions in memory. 
                print('executing in session_id block but memory>10')
                memory.chat_memory.messages = memory.chat_memory.messages[len(memory.chat_memory.messages) - 10:]
                output = question_generator.predict(question = prompt)
                memory_store[session_id] = memory
    # Update the last activity timestamp for the session
    active_sessions[session_id] = current_time
    return output

# Generate embeddings of the output from above function
def generate_embedding(value):
    try:
        body = json.dumps({"inputText": value})
        response = client_titan.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
            )
        response_body = json.loads(response.get("body").read())
        embeddings = response_body['embedding']
        return embeddings
    except botocore.exceptions.ClientError as error:
        print(error)

# Conduct Weaviate Vector Search filtering based on the program name selected
def knn_search_weaviate(query_vector,program, prompt):
    if program != 'Medicaid':
        document_collection = client.collections.get('Document_all_updated')
        filters = (Filter.by_property("path").equal(program))
        response = document_collection.query.near_vector(
        near_vector=query_vector,
        filters = filters,
        limit=config_data['app']['non_medicaid_limit'],
        return_metadata=MetadataQuery(distance=True)
)
    else:
        document_collection = client.collections.get('Document_Medicaid_updated')
        response = document_collection.query.hybrid(
        query = prompt,
        query_properties=["chunks"],
        vector=query_vector,
        alpha = config_data['app']['alpha'],
        limit=config_data['app']['medicaid_limit'],
        return_metadata=MetadataQuery(distance=True)
)

    return response.objects

#Template for the Claude Model to generate the response
@exponential_backoff_retry(retries=config_data['ebo']['retries'], base_delay=config_data['ebo']['base_delay'], max_delay=config_data['ebo']['max_delay'])
def summarize_with_claude(text, prompt, urls, program):
    messages = [
        {"role": "user", "content": f"""
         Use the following context:
    {text}

    Using the context provided, answer this question: {prompt}
    It is important to provide responses only from the given context in {text}.
    It is always best to answer in plain language, but some the answers may require the use of specific policy language and terms.
    Do not include the instructions you received while providing the response.
    If the user mentions something absolutely incorrect/false, do not use this information in your reasoning. Also please correct the user gently.
    If the question is in another language, respond in that language.
    Do not use any adjectives such as "crucially", "crtically", "explicitly" etc. or any verbs such as "emphasizes" etc. unless mentioned in the {text}.
    Treat the mention of "food stamp benefits" as "SNAP Benefits".
    For every {program}, we have a corresponding glossary referred through {links}. This is to be referred to if any acronym is present in {prompt}.
    
    Output Guidelines:
    '''
    [    **summary:**
    Start your answer with "Based on the information provided in the policy manual," and then proceed with answering the {prompt} only when you can find the answer.
    For the Summary section, write a complete paragraph to summarize the reponse and state the answer to the question. Explain the reasoning behind it.
    Make sure to summarize based on the content in {text}.
   
    
        **reasoning:**
    For the reasoning section, only include one quote from each page of the context that is used to answer the question in the response section.
    State your reasoning only in quotes step-wise.
    Mention the source for the reasoning at the end of each quote which includes the Policy Manual name and the section number.
    Mention the url for the reasoning at the end of the each quote as well.
    
    
        **reference:**
    For the reference section, state the URL links used in your reasoning step-wise. The URLs to be quoted are present in this :{urls}
    Summarize for each URL, what information user can expect.
    Here is an example of a URL link: 'https://gadhs.gitlab.io/pamms/dfcs/snap/3400/#income-limits'
    If any acronym like 'ABAWD','AU' etc. is present in {prompt}, only then please include the corresponding glossary link from {links} for the concerning {program}
    Do not provide URL links if you don't know the answer.
    Please make sure to provide URLs from which you will quote the content in the Reasoning Section.
    Do not mix the URLs.
        
         **suggested:**
    For the Suggested Questions, list general questions that can be asked to the question to get a better answer that is related to the context.
    '''
    ### Header Instructions:
    Always include the headers 'Summary', 'Reasoning', 'References' and 'Suggested Questions' in the response.
    Do not repeat the headers.

    ### Additional Output Guidelines:
    For Summary Section, please make sure to summarize the response based on the links you will quote in the Reasoning Section.
    Please ensure to not to have mismatch between what you quote in reasoning section and what you summarize in summary section.
    Do not reword a sentence and repeat it in the summary, must avoid redundancy.
    If {prompt} includes terms such as "QTrack" or "Q track", must include links : "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2145/" in the reference section.
    If {prompt} includes terms such as "QTrack" or "Q track", must include links : "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2503/" in the reference section.
    If {prompt} includes terms such as "MAGI BG" and "tax filer", do include "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2610/" in the reference and reasoning sections from {urls} and also include some summary from this {urls} into the summary section.  Lastly, include these links in the reference section as well.
    If {prompt} includes terms such as "shred" or "destroy", do refer "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2760/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "cancer", do refer "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2905/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "PGW Pregnant Woman", must include "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2184/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "retirement" or "annuities" or "401K", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2399/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "retirement" or "annuities" or "401K", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2332/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "resources" or "resource", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2301/" in the summary, reference and reasoning sections.
    If {prompt} includes terms such as "resources" or "resource", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2300/" in the summary, reference and reasoning sections.
    If {prompt} includes terms such as "BG income", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2196/" in the summary, reference and reasoning sections.
    If {prompt} includes terms such as "deeming", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2502/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "buy-in", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/appendix-f/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "fake" or "counterfeit", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2050/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "fake" or "counterfeit", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2060/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "fake" or "counterfeit", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2065/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "fake" or "counterfeit", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/medicaid/2051/" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "legal guardinaship", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/tanf/1335/#relationship" in the summary, reference and reasoning sections from {urls}.
    If {prompt} includes terms such as "violent felons", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/tanf/1387/#controlled-substance-abuse-felons" in the summary, reference and reasoning sections.
    If {prompt} includes terms such as "violent felons", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/tanf/1387/#fleeing-felons" in the summary, reference and reasoning sections.
    If {prompt} includes terms such as "violent felons", must mention link: "https://gadhs.gitlab.io/pamms/dfcs/tanf/1387/#paroleprobation-violators" in the summary, reference and reasoning sections.
    If you can't find the answer, don't begin your response with "Based on the information provided in policy manual", just respond with this sentence in summary: "I’m sorry, but I don’t fully understand your question. Could you please clarify your request, provide more context, or ask in a different way?"
    If you can't find the answer, provide an empty array for 'reasoning' and 'references' section.
    Always provide the response in JSON structure. Refer to the below JSON example to organize the response as no response should be in non-JSON format for every section.
    Make sure to escape any special character like "" or new line etc. if present while quoting from policy manual in reasoning's message section, so that the JSON doesn't become invalid.
    Before giving output, check if the quote in reasoning's message section is not making the entire json in-valid. If it is, ensure to make it valid by escaping any special character present in it.
    Refer to the JSON Example where a special character was escaped.

    {{
    "summary": "Based on the information provided in the policy manual, the resident shelter program refers to two types of facilities.",
    
    "reasoning": [
        {{  
            "message": "Certain Medicaid recipients are not issued or reissued a Medicaid card. Members who will not receive cards are those approved for: SLMB, QI-1, QDWI, EMA under any COA, Retroactive eligibility under any COA, No reissuance of a Medicaid card if not eligible in current month, Hospice if no \"Lock In\" received from the Hospice provider",
            "references": "SNAP Policy Manual, Basic Considerations section 3230",
            "url": "https://gadhs.gitlab.io/pamms/dfcs/snap/3230/#basic-considerations"
        }},
        {{
            "message": "Individuals are considered residents of a homeless shelter if the primary nighttime residence is one of the following:",
            "references": "SNAP Policy Manual, Basic Considerations section 3230",
            "url": "https://gadhs.gitlab.io/pamms/dfcs/snap/3230/#basic-considerations"
        }}
    ],

    "references": [
        {{
            "url": "https://gadhs.gitlab.io/pamms/dfcs/snap/3230/#basic-considerations",
            "message": "This link provides information about the basic considerations for homeless individuals residing in shelters and their eligibility for SNAP benefits."
        }},
        {{
            "url": "https://gadhs.gitlab.io/pamms/dfcs/snap/appendix-e/",
            "message": "This link provides a glossary of terms related to SNAP benefits."
        }}
    ],

    "suggested": [
        "What are the eligibility criteria for homeless individuals living in shelters to receive SNAP benefits?",
        "How does the number of meals provided by a shelter affect SNAP eligibility for residents?"
    ]
}}

    Answer:
    """
        }
    ]
    response = client_titan.invoke_model(
    modelId = config_data['app']['bedrock_modelId'],
    body = json.dumps( {
    "anthropic_version": config_data['app']['anthropic_version'],
    "messages":messages,
    "max_tokens": config_data['app']['max_tokens'],
    "temperature": config_data['app']['temperature'],
    } ),
    contentType = 'application/json')
    response_body = json.loads(response.get("body").read())
    return response_body['content'][0]['text']

#Function taking in the original user prompt and program name provided. Generate the required response
def summary_llm(prompt,program):
    print(f'generating embeddings: {datetime.now()}')
    if program == 'Medicaid':
        for key, value in references.items():
            prompt = re.sub(r'\b' + re.escape(key) + r'\b', value, prompt)

        embeddings = generate_embedding(prompt)
        print(f'embeddings generation done: {datetime.now()}')
        print(f'conduction vector search: {datetime.now()}')
        documents = knn_search_weaviate(embeddings,program, prompt)
        print(f'vector search finished: {datetime.now()}')
        combined_text = [''.join(text.properties['chunks'])  for text in documents]
        urls = [''.join(text.properties['url'])  for text in documents]
        print('Following documents were pulled up as vector search results')
        print(urls)
        print(f'summarizing the response now: {datetime.now()}')
        summary = summarize_with_claude(combined_text, prompt, urls, program)
        print(f'summarizing the response done: {datetime.now()}')
    else:
        for key, value in references.items():
            prompt = re.sub(r'\b' + re.escape(key) + r'\b', value, prompt)

        embeddings = generate_embedding(prompt)
        print(f'embeddings generation done: {datetime.now()}')
        print(f'conduction vector search: {datetime.now()}')
        documents = knn_search_weaviate(embeddings,program, prompt)
        print(f'vector search finished: {datetime.now()}')
        combined_text = [''.join(text.properties['chunks'])  for text in documents]
        urls = [''.join(text.properties['sub_section_link'])  for text in documents]
        print('Following documents were pulled up as vector search results')
        print(urls)
        print(f'summarizing the response now: {datetime.now()}')
        summary = summarize_with_claude(combined_text, prompt, urls, program)
        print(f'summarizing the response done: {datetime.now()}')
    return summary


initialize_resources()
vault = Vault()
scanners = [Anonymize(vault, allowed_names=["KATIE BECKETT", "Katie Beckett", "katie backett", "Bendex", "BENDEX", "bendex"], language="en"), Regex(
    patterns=[rf"{config_data['patterns']}"],
    is_blocked=True,
    match_type=MatchType.SEARCH,  
    redact=True,  
)]
start_session_monitor()

###scanners = [Anonymize(vault, allowed_names=["KATIE BECKETT", "Katie Beckett", "katie backett", "Bendex", "BENDEX", "bendex"], 

@app.after_request
def add_header(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response

@app.route('/health', methods=['GET'])
def health():
    output = {'statusCode': 200, 'body': 'Service is healthy'}
    print (output)
    return jsonify(output)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Too many requests."), 429

# Endpoint for /sendMessage route. This will provide the user prompt provided, program name selected by the user and other important fields. 
# Will eventually return the response to the user
@app.route('/sendMessage', methods=['POST'])
@limiter.limit("50 per minute")
def process_request():
    print(request)
    body = request.get_json()
    if body is not None:
        if 'prompt' in body and body['prompt']:
            prompt_new = body['prompt']
            program = body['prog']
            sessionId = body['sessionId']
            requestId = body['requestId']
            chainOfThought = body['chainOfThought']
            timestamp = datetime.strptime(body['timestamp'], '%m/%d/%Y, %I:%M:%S %p')
            print(f'question received: {datetime.now()}')
            sql_question = '''
                INSERT INTO GENAI_POLICY."AI_POLICY_ENGINE"  (
                    SES_ID, RQST_ID, SES_RSET_IND, USER_QSTN_TXT,
                    PROG_NM, RQST_SENT_TMS, CRE_TMS, UPDT_TMS
                    ) VALUES (
                    :1, :2, :3, :4,
                    :5, :6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
            '''
            if initialization_successful:
                try:
                    print(f'getting oracle connection: {datetime.now()}')
                    connection = pool.acquire()
                    cursor = connection.cursor()
                    print(f'inserting question into db: {datetime.now()}')
                    cursor.execute(sql_question, (sessionId, requestId, chainOfThought, prompt_new, program, timestamp))
                    print(datetime.now())
                    print(body)
                    print('inserted into db')
                    connection.commit()
                    print(f'checking pii: {datetime.now()}')
                    for key, value in references_llm_scan.items():                                    # Fix Bendex issue
                        prompt_new = re.sub(r'\b' + re.escape(key) + r'\b', value, prompt_new)
                    sanitized_prompt, is_valid, risk_score = scan_prompt(scanners,prompt_new)
                    print(f'pii checking done: {datetime.now()}')
                    if is_valid['Regex'] is True and is_valid['Anonymize'] is True:
                        print(f'getting question from buffer: {datetime.now()}')
                        output = get_question_from_cot(sessionId, prompt_new, chainOfThought)
                        print(f'got question from buffer: {datetime.now()}')
                        print(output)
                        print(f'getting final response now: {datetime.now()}')
                        updated_summary = summary_llm(output,program)
                        print('answer at timestamp:')
                        print('\n')
                        print(datetime.now())
                        print('updating row, inserting into database')
                        sql_answer = '''
                            UPDATE GENAI_POLICY."AI_POLICY_ENGINE"
                            SET ANSW_TXT = :1, ANSW_RCV_TMS = CURRENT_TIMESTAMP, UPDT_TMS = CURRENT_TIMESTAMP
                           WHERE SES_ID = :2 and RQST_ID = :3
                            '''
                        cursor.execute(sql_answer, (updated_summary, sessionId, requestId))
                        connection.commit()
                        print('inserted into database')
                        pool.release(connection)
                        print('released connection')
                    else:
                        response = 'PII/PHI Detected in the prompt, please remove the concerning elements from the prompt and try again.'
                        updated_summary = jsonify(response), 400
                        print('answer at timestamp:')
                        print('\n')
                        print(datetime.now())
                        print('inserting into database')
                        sql_answer = '''
                            UPDATE GENAI_POLICY."AI_POLICY_ENGINE"
                            SET ANSW_TXT = :1, ANSW_RCV_TMS = CURRENT_TIMESTAMP, UPDT_TMS = CURRENT_TIMESTAMP
                            WHERE SES_ID = :2 and RQST_ID = :3
                        '''
                        cursor.execute(sql_answer, (response, sessionId, requestId))
                        connection.commit()
                        print('inserted into database')
                        pool.release(connection)
                        print('released connection')
                except Exception as e:
                    print(e)
                    error = "Service Unavailable"
                    updated_summary = jsonify(error), 503            
            else:
                error = "Service Unavailable"
                updated_summary = jsonify(error), 503
        else:
            error = "No Prompt Provided"
            updated_summary = jsonify(error), 400
    else:
        error = "No event received"
        updated_summary = jsonify(error), 400
    try:
        print(updated_summary)
        return (updated_summary)
    except Exception as e:
        print(e)

# Endpoint to take in the user feedback for a given response
# Results in either successful feedback capture or error in case couldn't capture due to service unavailability
@app.route('/feedback', methods=['POST'])
@limiter.limit("2 per second")
def feedback():
    print(request)
    body = request.get_json()
    requestId = body['requestId']
    feedback = body['feedback']
    if feedback != 'CANCEL':
        feedback_text = body['feedbackMessage']
        print(datetime.now())
        print('updating row with feedback, inserting into database')
        sql_answer = '''
                    UPDATE GENAI_POLICY."AI_POLICY_ENGINE"
                    SET USER_FDBK_VOTE = :1, USER_FDBK_TXT =:2, UPDT_TMS = CURRENT_TIMESTAMP
                    WHERE RQST_ID = :3
                    '''
        if initialization_successful:
            try:
                connection = pool.acquire()
                cursor = connection.cursor()
                cursor.execute(sql_answer, (feedback, feedback_text, requestId))
                connection.commit()
                print('inserted into database')
                pool.release(connection)
                output = jsonify("Thank you for your feedback!"), 200
            except Exception as e:
                print(e)
                output = jsonify("Service Unavailable"), 503
        else:
            output = jsonify("Service Unavailable"), 503
    else:
        print('deleting the feedback')
        sql_answer = '''
                    UPDATE GENAI_POLICY."AI_POLICY_ENGINE"
                    SET USER_FDBK_VOTE = NULL, USER_FDBK_TXT = NULL, UPDT_TMS = CURRENT_TIMESTAMP
                    WHERE RQST_ID = :1
                    '''
        if initialization_successful:
                try:
                    connection = pool.acquire()
                    cursor = connection.cursor()
                    cursor.execute(sql_answer, (requestId,))
                    connection.commit()
                    print('inserted into database')
                    pool.release(connection)
                    output = jsonify("Previous Feedback deleted!"), 200
                except Exception as e:
                    print(e)
                    output = jsonify("Service Unavailable"), 503
        else:
            output = jsonify("Service Unavailable"), 503
    return output

# Endpoint to extend the session based on user's selection after a certain duration of inactivity
@app.route('/extendSession', methods=['POST'])
@cache.cached(timeout=SESSION_TTL, key_prefix="extend_session")
def extend_session():
    """
    Endpoint to extend the session if the user chooses to continue.
    Resets the session's expiration timer.
    """
    print(request)
    body = request.get_json()
    if 'sessionId' in body and body['sessionId']:
        sessionId = body['sessionId']
        timestamp = datetime.strptime(body['timestamp'], '%m/%d/%Y, %I:%M:%S %p')

    
    if sessionId in active_sessions:
        # Reset the session's last activity timestamp to the current time
        active_sessions[sessionId] = timestamp
        print(f"Session {sessionId} has been extended.")
        
        # Return success response to frontend
        return jsonify(
            f"Session {sessionId} has been successfully extended."
       ), 200
    else:
        # Session ID not found
        return jsonify(
            "Session not found."
        ), 404

# Endpoint to handle requests that were timedout.When user doesn't get response to a question, it will timeout and such questions are being logged through this endpoint
@app.route('/timeout', methods=['POST'])
def session_timeout():
    """
    Endpoint to handle session timeouts and log the data for later use.
    """
    print(request)
    body = request.get_json()
    # Extract data from the request body
    sessionId = body.get('sessionId')
    requestId = body.get('requestId')
    chainOfThought = body.get('chainOfThought')
    prompt_new = body.get('prompt')
    program = body.get('prog')
    timestamp = datetime.strptime(body.get('timestamp'), '%m/%d/%Y, %I:%M:%S %p')
    
    if initialization_successful:
        try:
            connection = pool.acquire()
            cursor = connection.cursor()
            # Check if the request ID exists
            cursor.execute('''
            SELECT COUNT(*) FROM GENAI_POLICY."AI_POLICY_ENGINE"
            WHERE RQST_ID = :1
            ''', (requestId,))
            result = cursor.fetchone()
 
            if result[0] > 0:
                    # Request ID already exists, update the SES_TIMEOUT_IND to 1
                print('Updating database')
                sql_update = '''
                   UPDATE GENAI_POLICY."AI_POLICY_ENGINE"
                    SET SES_TIMEOUT_IND = 1
                    WHERE RQST_ID = :1
                    '''
                cursor.execute(sql_update, (requestId,))
                connection.commit()
                pool.release(connection)
                print('Updated database')
                output = jsonify({"statusCode": 200}), 200
            else:
                # Request ID does not exist, insert a new record
                sql_insert = '''
                        INSERT INTO GENAI_POLICY."AI_POLICY_ENGINE" (
                        SES_ID, RQST_ID, SES_RSET_IND, USER_QSTN_TXT, 
                        PROG_NM, RQST_SENT_TMS, CRE_TMS, UPDT_TMS, SES_TIMEOUT_IND
                        ) VALUES (
                        :1, :2, :3, :4, 
                        :5, :6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 2
                        )
                        '''
                cursor.execute(sql_insert, (sessionId, requestId, chainOfThought, prompt_new, program, timestamp))
                connection.commit()
                pool.release(connection)
                print('Inserted into database')
                output = jsonify({"statusCode": 200}), 200
        except Exception as e:
                print(e)
                output = jsonify("Service Unavailable"), 503
    else:
        output = jsonify("Service Unavailable"), 503

    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0')
   
