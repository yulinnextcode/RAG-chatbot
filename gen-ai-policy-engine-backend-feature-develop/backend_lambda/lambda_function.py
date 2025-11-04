import requests
import boto3
import json
import pandas as pd
import botocore
import re
import weaviate
from weaviate.connect import ConnectionParams
from weaviate.classes.init import AdditionalConfig, Timeout, Auth
import os
from weaviate.classes.query import MetadataQuery
import weaviate.classes as wvc

def get_weaviate_secret():

    secret_name = "PolicyEngine/weaviateDev"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
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

# Instantiating the variables
s3 = boto3.resource('s3')
modelId = "amazon.titan-embed-text-v1"
accept = "application/json"
contentType = "application/json"
client_titan = boto3.client('bedrock-runtime', region_name='us-east-1')
password_weaviate = get_weaviate_secret()['password_backend']

# Function to create chunks out of the input text    
def new_chunks(value):
    max_tokens = 8192
    start = 0
    chunks = []
    stride = 256
    while start < len(value):
        end = min(start + max_tokens, len(value))
        chunk = value[start:end]
        chunks.append(chunk)
        start += max_tokens - stride
    return chunks

# Function to create rows where we have data in section. if not used this, then we will miss out on section_content data.
def create_new_row(row):
    new_row = row.copy()
    new_row['subsection_path'] = row['path']
    new_row['subsection_title'] = row['section_title']
    new_row['subsection_link'] = row['section_internal_link']
    new_row['subsection_content'] = row['section_content']
    return new_row



# Function to generate embeddings out of the chunked content
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

# Function to parse in JSON data and create a structured dataframe out of it
def df_data(json_data):

    # Get all the URLs example:https://gadhs.gitlab.io/pamms/dfcs/tanf/1315/
    url = []
    for a in range(len(json_data['pages'])):
        url.append(json_data['pages'][a]['pageUrl'])
    
    # Get all the titles example: 1315 Deprivation
    title = []
    for a in range(len(json_data['pages'])):
        title.append(json_data['pages'][a]['pageTitle'])

    # Get the entire text of the page
    text = []
    for a in range(len(json_data['pages'])):
        text.append(json_data['pages'][a]['pageContent'])

    df = pd.DataFrame()
    df['url'] = url
    df['title'] = title
    df['text'] = text

    # Get the path of the page - [
              #  "Division of Family and Children Services",
              #  "TANF",
              #  "1300 Basic Eligibility",
              #  "1315 Deprivation"
            #],
    path = []
    for a in range(len(json_data['pages'])):
        path.append(json_data['pages'][a]['path'])

    path_updated = []
    for a in path:
        if len(a)>1:
            path_updated.append(a[1])
        else:
            path_updated.append(a[0])

    df['path'] = path_updated

    # Get the internal links now structured as in example - 
    # "internalLinks": [ {
    #                 "sectionTitle": "Basic Considerations",
    #                 "internalLink": "/dfcs/tanf/1315/#basic-considerations",
    #                 "sectionContent": "A dependent child must be deprived of the support or care of one or both parents to be eligible for cash assistance.",
    #                 "subsections": [
    #      {
    #                         "subsectionTitle": "Paternity",
    #                         "subsectionPath": "/dfcs/tanf/1315/#paternity",
    #                         "subsectionContent": "The identity of a dependent child's father must be established for the following purposes:\n\nto determine on which parent to base
    # ]
    #             },]

    internal_links = []
    for a in range(len(json_data['pages'])):
        internal_links.append(json_data['pages'][a]['internalLinks'])

    df['internal_links'] = internal_links

    df_data = df[(df['path'] == 'SNAP') | (df['path'] == 'TANF')]

    df_new = df_data.explode('internal_links')

    df_new = df_new.reset_index()

    df_new = df_new.drop('index',axis=1)

    df_new['is_dict'] = df_new['internal_links'].apply(lambda x:isinstance(x,dict))
    df_new_false = df_new[df_new['is_dict']==False]

    df_new = df_new[df_new['is_dict']]

    df_new['subsection'] = df_new['internal_links'].apply(lambda x:x.get('subsections'))

    df_new = df_new.explode('subsection')

    df_new['is_dict_subsection'] = df_new['subsection'].apply(lambda x:isinstance(x,dict))

    df_new_subsection_false = df_new[df_new['is_dict_subsection']==False]

    df_new_subsection_true = df_new[df_new['is_dict_subsection']]

    df_new_subsection_true['subsection_title'] = df_new_subsection_true['subsection'].apply(lambda x:x.get('subsectionTitle'))

    df_new_subsection_true['subsection_path'] = df_new_subsection_true['subsection'].apply(lambda x:x.get('subsectionPath'))
    df_new_subsection_true['subsection_content'] = df_new_subsection_true['subsection'].apply(lambda x:x.get('subsectionContent'))

    df_new_subsection_true['subsection_link'] = '#' + df_new_subsection_true['subsection_path'].str.split('#', expand=True)[1]

    df_new_subsection_true['subsection_link'] = df_new_subsection_true['url'] + df_new_subsection_true['subsection_link']

    df_new_subsection_true['section_title'] = df_new_subsection_true['internal_links'].apply(lambda x:x.get('sectionTitle'))
    df_new_subsection_true['section_internal_link'] = df_new_subsection_true['internal_links'].apply(lambda x:x.get('internalLink'))
    df_new_subsection_true['section_content'] = df_new_subsection_true['internal_links'].apply(lambda x:x.get('sectionContent'))

    df_new_subsection_true['section_internal_link'] = '#' + df_new_subsection_true['section_internal_link'].str.split('#', expand=True)[1]
    df_new_subsection_true['section_internal_link'] = df_new_subsection_true['url'] + df_new_subsection_true['section_internal_link']

    new_df = df_new_subsection_true.apply(create_new_row, axis=1)
    new_df = new_df.drop_duplicates(subset='subsection_link', keep='first').reset_index(drop=True)
    df_new_subsection_true = pd.concat([df_new_subsection_true, new_df], ignore_index=True)
    

    columns = ['url','title','text','path','internal_links','is_dict','subsection','is_dict_subsection','section_title','section_internal_link',
          'section_content','subsection_title','subsection_path','subsection_link','subsection_content','text_to_use']
    df_new_subsection_true = df_new_subsection_true.reindex(columns = columns)

    df_new_subsection_false['section_title'] = df_new_subsection_false['internal_links'].apply(lambda x:x.get('sectionTitle'))
    df_new_subsection_false['section_internal_link'] = df_new_subsection_false['internal_links'].apply(lambda x:x.get('internalLink'))
    df_new_subsection_false['section_content'] = df_new_subsection_false['internal_links'].apply(lambda x:x.get('sectionContent'))

    df_new_subsection_false['section_internal_link'] = '#' + df_new_subsection_false['section_internal_link'].str.split('#', expand=True)[1]
    df_new_subsection_false['section_internal_link'] = df_new_subsection_false['url'] + df_new_subsection_false['section_internal_link']

    df_new_subsection_false['subsection_title'] = df_new_subsection_false['section_title']
    df_new_subsection_false['subsection_path'] = df_new_subsection_false['path']
    df_new_subsection_false['subsection_link'] = df_new_subsection_false['section_internal_link']
    df_new_subsection_false['subsection_content'] = df_new_subsection_false['section_content']
    
    chunks_subsection_true = []
    for index,row in df_new_subsection_true.iterrows():
        chunks_subsection_true.append(new_chunks(row['subsection_content']))

    chunks_subsection_false = []
    for index,row in df_new_subsection_false.iterrows():
        chunks_subsection_false.append(new_chunks(row['subsection_content']))
    
    df_new_subsection_true['chunks'] = chunks_subsection_true
    df_new_subsection_false['chunks'] = chunks_subsection_false

    df_new_subsection_true_exploded = df_new_subsection_true.explode('chunks')
    df_new_subsection_false_exploded = df_new_subsection_false.explode('chunks')

    df_new_subsection_false_exploded['text_to_embed'] = df_new_subsection_false_exploded['title'] + ' ' + df_new_subsection_false_exploded['section_title'] + ' ' + df_new_subsection_false_exploded['chunks']
    df_new_subsection_true_exploded['text_to_embed'] = df_new_subsection_true_exploded['title'] + ' ' + df_new_subsection_true_exploded['section_title'] + ' ' + df_new_subsection_true_exploded['subsection_title'] + ' ' + df_new_subsection_true_exploded['chunks']

    df_new_false['subsection'] = df_new_false['internal_links']
    df_new_false['is_dict_subsection'] = df_new_false['is_dict']
    df_new_false['section_title'] = df_new_false['title']
    df_new_false['section_internal_link'] = df_new_false['url']
    df_new_false['section_content'] = df_new_false['text']
    df_new_false['subsection_path'] = df_new_false['path']
    df_new_false['subsection_link'] = df_new_false['url']
    df_new_false['subsection_content'] = df_new_false['text']

    chunks_false = []
    for index,row in df_new_false.iterrows():
        chunks_false.append(new_chunks(row['subsection_content']))

    df_new_false['chunks'] = chunks_false

    df_new_false_explode = df_new_false.explode('chunks')

    df_new_false_explode['text_to_embed'] = df_new_false_explode['title'] + ' ' + df_new_false_explode['chunks']


    frames = [df_new_subsection_true_exploded, df_new_subsection_false_exploded, df_new_false_explode]
    df_combined = pd.concat(frames)

    # Generate Embeddings of the concerning chunks
    embeddings_updated = []
    for index, row in df_combined.iterrows():
        embeddings_updated.append(generate_embedding(row['text_to_embed']))
    
    # Put the embeddings into dataframe
    df_combined['embeddings'] = embeddings_updated
    df_combined = df_combined.reset_index()    
    return df_combined

def df_data_medicaid(json_data):

    # Get all the URLs example:https://gadhs.gitlab.io/pamms/dfcs/tanf/1315/
    url = []
    for a in range(len(json_data['pages'])):
        url.append(json_data['pages'][a]['pageUrl'])
    
    # Get all the titles example: 1315 Deprivation
    title = []
    for a in range(len(json_data['pages'])):
        title.append(json_data['pages'][a]['pageTitle'])

    # Get the entire text of the page
    text = []
    for a in range(len(json_data['pages'])):
        text.append(json_data['pages'][a]['pageContent'])

    df = pd.DataFrame()
    df['url'] = url
    df['title'] = title
    df['text'] = text

    # Get the path of the page - [
              #  "Division of Family and Children Services",
              #  "TANF",
              #  "1300 Basic Eligibility",
              #  "1315 Deprivation"
            #],
    path = []
    for a in range(len(json_data['pages'])):
        path.append(json_data['pages'][a]['path'])

    path_updated = []
    for a in path:
        if len(a)>1:
            path_updated.append(a[1])
        else:
            path_updated.append(a[0])

    df['path'] = path_updated
    
    df_data = df[(df['path'] == 'Medicaid')]
    
    chunks = []
    for index, row in df_data.iterrows():
        chunks.append(new_chunks(row['text']))

    df_data['chunks'] = chunks

    df_data = df_data.explode('chunks')

    df_data['text_to_embed'] = df_data['title'] + ' ' + df_data['chunks']

    embeddings_updated = []
    for index, row in df_data.iterrows():
        embeddings_updated.append(generate_embedding(row['text_to_embed']))

    df_data['embeddings'] = embeddings_updated
    df_data = df_data.reset_index()
    return df_data
    
def handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    obj = s3.Object(bucket_name, object_key)
    data = obj.get()['Body'].read().decode('utf-8')
    json_file = json.loads(data)
    
    df = df_data(json_file)
    df_medicaid = df_data_medicaid(json_file) 
    host_dns = os.environ['weaviate_hostname']
    client = weaviate.WeaviateClient(
    connection_params=ConnectionParams.from_params(
        http_host=host_dns,
        http_port=8080,
        http_secure=False,
        grpc_host=host_dns,
        grpc_port=50051,
        grpc_secure=False,
    ),
    auth_client_secret=Auth.api_key(password_weaviate),
    additional_config=AdditionalConfig(
        timeout=Timeout(init=30, query=60, insert=120),
    ),
    skip_init_checks=True
    )

    client.connect()  # Connect to Weaviate
    
    collections = client.collections.list_all()
    
    if 'Document_all_updated' in collections:
        client.collections.delete("Document_all_updated")
    
        collection_all = {
        "class": "Document_all_updated",
        "description": "A class to represent documents of SNPA and TANF",
        "vectorizer": "none",  # Set to "none" because embeddings are provided
        "moduleConfig": {
            },
         "properties": [
        {"name": "sub_section_title", "dataType": ["text"]},
        {"name": "sub_section_link", "dataType": ["text"]},
        {"name": "path", "dataType": ["text"]},
        {"name": "chunks", "dataType": ["text"]},
            ]
            }
        client.collections.create_from_dict(collection_all)

    else:
        collection_all = {
        "class": "Document_all_updated",
        "description": "A class to represent documents of Medicaid",
        "vectorizer": "none",  # Set to "none" because embeddings are provided
        "moduleConfig": {
            },
         "properties": [
        {"name": "sub_section_title", "dataType": ["text"]},
        {"name": "sub_section_link", "dataType": ["text"]},
        {"name": "path", "dataType": ["text"]},
        {"name": "chunks", "dataType": ["text"]},
            ]
            }
        client.collections.create_from_dict(collection_all)
    
    if 'Document_Medicaid_updated' in collections:
        client.collections.delete("Document_Medicaid_updated")
    
        collection_all = {
        "class": "Document_Medicaid_updated",
        "description": "A class to represent documents of Medicaid",
        "vectorizer": "none",  # Set to "none" because embeddings are provided
        "moduleConfig": {
            },
         "properties": [
        {"name": "title", "dataType": ["text"]},
        {"name": "url", "dataType": ["text"]},
        {"name": "path", "dataType": ["text"]},
        {"name": "chunks", "dataType": ["text"]},
            ]
            }
        client.collections.create_from_dict(collection_all)

    else:
        collection_all_medicaid = {
        "class": "Document_Medicaid_updated",
        "description": "A class to represent documents of Medicaid",
        "vectorizer": "none",  # Set to "none" because embeddings are provided
        "moduleConfig": {
            },
         "properties": [
        {"name": "title", "dataType": ["text"]},
        {"name": "url", "dataType": ["text"]},
        {"name": "path", "dataType": ["text"]},
        {"name": "chunks", "dataType": ["text"]},
            ]
            }
        client.collections.create_from_dict(collection_all_medicaid)

        
    with client.batch.dynamic() as batch:
        for i, row in df.iterrows():
            print(f"Importing document: {i+1}")
            properties = {
            "sub_section_title": row["subsection_title"],
            "sub_section_link": row["subsection_link"],
            "path": row["path"],
            "chunks": row["chunks"],
            }
            batch.add_object(
                collection="Document_all_updated",  # Specify the collection name here
                vector=row["embeddings"],
                properties=properties
            )
        failed_objs_a = client.batch.failed_objects
    print('batch import successful for SNAP and TANF')
    print(len(failed_objs_a))

    with client.batch.dynamic() as batch:
        for i, row in df_medicaid.iterrows():
            print(f"Importing document: {i+1}")
            properties = {
            "title": row["title"],
            "url": row["url"],
            "path": row["path"],
            "chunks": row["chunks"],
            }
            batch.add_object(
                collection="Document_Medicaid_updated",  # Specify the collection name here
                vector=row["embeddings"],
                properties=properties
            )
        failed_objs_a = client.batch.failed_objects
    print('batch import successful for Medicaid')
    print(len(failed_objs_a))

    return {
        'statusCode': 200,
        'body': 'document uploaded'
        }
