# Knowhow-Liberator


Open web is dying (more like being killed), useful information communities online is being hidden in the silos. As a long time contrbutor to open online communities I want to make them sustainable again. To do that I want to automatically convert useful information, usually Question and Answer exchanges from closed platforms like Discord and publish it on open web (with original posters approval of course.). 
To make this happen we need some way of doing complicated NLP work: finding conversation threads in unstructured chats, extracting metadata of the exchanges (who started the thread, what is it about, was it answered succcessfully), converting those exchanges

A pipeline works as follows:

1. Select a channel in your ML discord server
2. We take data from discord using [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter)
3. Filter big json files with small `jq` program to fit longer conversation in 100k token budget
4. Going over message history in batches
    1. Extracting conversation threads metadata with "Claude 2" function calls
    2. Iterating over topics, extracting each relevant thread, and converting into markdown file
5. publishing as hugo website


For the testing purposes I chose "hall/help" channel in [LAION](https://laion.ai/) discord server.




```commandline
docker run --rm  -v /tmp/dce_output:/dce_output tyrrrz/discordchatexporter export -t '$DTOKEN' -c '1100516714791313479' -o '/dce_output/' -f 'Json'
```

```commandline
jq '[                  
  .messages[] | {
    id: .id,
    content: .content,
    date: .timestamp,
    poster: .author.name,
    reply_id: .reference.messageId
  }
]' LAION_help_chat_1100516714791313479.json > help_messages.json
```



Example of generating papges from json: 



Here are the last three conversations quoted in markdown format:

### Conversation 1

**elvispresniy:**
> Hi everyone! I am trying to use dalle2_laion in colab, but I don't understand how to install and import it correctly. Can you help me?

**qasb:**
> You can use Deep Floyd's "IF" instead. That repository you linked is for reaearch and only has an architecture implementation.

**qasb:**
> Deep Floyd's IF is the same (with very small changes)
IF = Imagen Free btw

**destructo5065:** 
> I'll look into that. Thank you

### Conversation 2

**philipmay:**
> The LeoLM blog article is talking about "a large German text corpus of 65 billion tokens of deliberately filtered and deduplicated web text".
Did LAION publish this German filtered dataset somewhere?
If not -> could you please do that?

**bjoernp:**
> The dataset is based on the Oscar Corpus 23.01 and German Wikipedia. We currently haven't released it in any official function but you can find the dedupd but unfiltered version of German Oscar here: https://huggingface.co/datasets/bjoernp/oscar2023_de_deduped
