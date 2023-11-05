# %%
import json
with open('LAION_help_chat_1100516714791313479.json') as fh:
    data = json.loads(fh.read())

print(data.keys())

print(data['messages'][0]['timestamp'], data['messages'][-1]['timestamp'])

# %%
from dotenv import load_dotenv
load_dotenv()
import os


from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
anthropic = Anthropic(api_key=os.environ['API_KEY'])
completion = anthropic.completions.create(
    model="claude-2",
    max_tokens_to_sample=300,
    prompt=f"{HUMAN_PROMPT} How many toes do dogs have?{AI_PROMPT}",
)
print(completion.completion)

# %%
import matplotlib.pyplot as plt

messages = data['messages'] 

# Extract timestamps  
timestamps = [msg['timestamp'] for msg in messages]

# Convert to datetime objects
from datetime import datetime
timestamps = [datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f%z') for ts in timestamps]

# Plot timeline  
fig, ax = plt.subplots()
ax.plot(timestamps, [0]*len(timestamps), 'bo')

ax.set_xlabel('Timestamp')
ax.set_ylabel('Message ID')
ax.set_title('Message Timeline')

# Format x-axis ticks  
fig.autofmt_xdate()

plt.show()
# %%
import networkx as nx

with open('help_messages.json') as fh:
    messages_text = fh.read()
    messages = json.loads(messages_text)

G = nx.DiGraph()

for message in messages:
    G.add_node(message['id'])
    if message['reply_id']:
        G.add_edge(message['id'], message['reply_id'])

def give_cc(graph):
    for c in nx.connected_components(graph.to_undirected()):
        if False:
            yield graph.subgraph(c).copy()
        else:
            yield graph.subgraph(c)


ccg = list(give_cc(G))

graphs = sorted(ccg, key=len, reverse=True)

print(f'longest explicit thread has {len(graphs[0].nodes)} messages')
# %%
# got it from here https://twitter.com/hwchase17/status/1685667799174393857/
# https://python.langchain.com/docs/integrations/chat/anthropic_functions

from langchain_experimental.llms.anthropic_functions import AnthropicFunctions
from langchain.chains import create_extraction_chain

# %%
model = AnthropicFunctions(model="claude-2", anthropic_api_key=os.environ['API_KEY'])

# %%
# prompts from Claude 2 webapp 

prompt1 = "Please read all the messages in this json file and provide me with markdown text quoting last three conversations in that file."

prompt2 = "Please read the file, message by message and find all discussion topics. After that list them in order of frequency of occurrence. List topics as they are mentioned exactly, no paraphrasing."

prompt3 = "Read this file again, find messages regarding {TOPIC} and render them as conversations in markdown format."

prompt4 = "Read this file again, find messages regarding {TOPIC} and list the id's of the relevant messages in sequential order."

# %%
metadata_extraction_function_schema = {
        "name": "return_topics",
        "description": "Return all discussion topics in message threads",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic being discussed in a thread"
                },
                "num_occurances": {
                    "type": "string",
                    "description": "Number of times given topic been mentioned"
                },
                "thread_start_id": {
                    "type": "int64",
                    "description": "id of message in which conversation have started"
                },
                "message_ids": {
                    "type": "list",
                    "description": "list of int64, of all messages belonging to a thread on a given topic"
                },
            },
            },
            "required": ["topic","num_occurances","thread_start_id","message_ids"],
        }

# %%

# %%
# schema = {
#     "properties": {
#         "name": {"type": "string"},
#         "height": {"type": "integer"},
#         "hair_color": {"type": "string"},
#     },
#     "required": ["name", "height"],
# }

# inp = """
# Alex is 5 feet tall. Claudia is 1 feet taller Alex and jumps higher than him. Claudia is a brunette and Alex is blonde.
#         """

# %%

# %%
metadata_extraction_function_schema = { 
            "properties": {
                "topic": {
                    "type": "string",
                    # "description": "Topic being discussed in a thread"
                },
                "num_occurances": {
                    "type": "string",
                    # "description": "Number of times given topic been mentioned"
                },
                "thread_start_id": {
                    "type": "int64",
                    # "description": "id of message in which conversation have started"
                },
                "message_ids": {
                    "type": "list",
                    # "description": "list of int64, of all messages belonging to a thread on a given topic"
                },
            },
            
            "required": ["topic", "num_occurances"]}

chain = create_extraction_chain(metadata_extraction_function_schema, model)
results = chain.run(inp)

# %%
inp = f"""{HUMAN_PROMPT}Here are all the messages:
```
{messages_text}
```

Please read the file, find all discussion topics. After that list them in order of frequency of occurrence. List topics as they are mentioned exactly, no paraphrasing.
{AI_PROMPT}
"""

# %%

# %%
completion = anthropic.completions.create(
    model="claude-2",
    max_tokens_to_sample=4000,
    prompt=inp,
)

# %%
print(completion.completion)

# %%
topic_list = completion.completion.split('\n\n')[-1]

# %%
topic_list = [topic.split(' - ') for topic in topic_list.split('\n')]

# %%
from tqdm import tqdm

# %%
for _freq, _topic in tqdm(topic_list):
    
    _prompt = f"""{HUMAN_PROMPT}Read file with messages, find messages regarding {_topic}. 

Here is the file with messages
```
{messages_text}
```
When you find the messages: rewrite them as a conversations in markdown article format for high quality blog.

Return only markdown code, text should start with this block: 
```
---
title: {{blogpost title}}
date: {{timestamp of the first message in ISO format}}
draft: false
---
```

{AI_PROMPT}"""
    
    completion = anthropic.completions.create(
    model="claude-2",
    max_tokens_to_sample=4000,
    prompt=_prompt)
    slug = _topic.replace(' ', '-').replace('/', '-')
    with open(f'site/content/post/{slug}.md', 'w+') as fh:
        fh.write(completion.completion)

# %%
