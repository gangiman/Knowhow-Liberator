# %%

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

import json

with open('LAION_help_chat_1100516714791313479.json') as fh:
    data = json.loads(fh.read())

data.keys()

print(data['messages'][0]['timestamp'], data['messages'][-1]['timestamp'])

# %%

anthropic = Anthropic(api_key='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')
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
# -

import networkx as nx

# +
with open('help_messages.json') as fh:
    messages = json.loads(fh.read())

G = nx.DiGraph()

for message in messages:
    G.add_node(message['id'])
    if message['reply_id']:
        G.add_edge(message['id'], message['reply_id'])
        
# -

def give_cc(graph):
    for c in nx.connected_components(graph.to_undirected()):
        if False:
            yield graph.subgraph(c).copy()
        else:
            yield graph.subgraph(c)


ccg = list(give_cc(G))

graphs = sorted(ccg, key=len, reverse=True)

graphs[0].nodes
# %%

# got it from here https://twitter.com/hwchase17/status/1685667799174393857/
# https://python.langchain.com/docs/integrations/chat/anthropic_functions

from langchain_experimental.llms.anthropic_functions import AnthropicFunctions
from langchain.chains import create_extraction_chain


model = AnthropicFunctions(model="claude-2")

# example of openai function
functions = [
    {
        "name": "return_recipe",
        "description": "Return the recipe asked",
        "parameters": {
            "type": "object",
            "properties": {
                "ingredients": {
                    "type": "string",
                    "description": "The ingredients list."
                },
                "steps": {
                    "type": "string",
                    "description": "The recipe steps."
                },
            },
            },
            "required": ["ingredients","steps"],
        }
]

schema = {
    "properties": {
        "name": {"type": "string"},
        "height": {"type": "integer"},
        "hair_color": {"type": "string"},
    },
    "required": ["name", "height"],
}
inp = """
Alex is 5 feet tall. Claudia is 1 feet taller Alex and jumps higher than him. Claudia is a brunette and Alex is blonde.
        """

chain = create_extraction_chain(schema, model)

chain.run(inp)
