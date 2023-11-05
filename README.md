# Knowhow-Liberator

Open web is dying (more like being killed), useful information communities online is being hidden in the silos. As a long time contrbutor to open online communities I want to make them sustainable again. To do that I want to automatically convert useful information, usually Question and Answer exchanges from closed platforms like Discord and publish it on open web (with original posters approval of course.). 
To make this happen we need some way of doing complicated NLP work: finding conversation threads in unstructured chats, extracting metadata of the exchanges (who started the thread, what is it about, was it answered succcessfully), converting those exchanges into a static webpage. Claude 2 is great for that with it's huge context window of 100k tokens. After generating content we can serve them using Hugo.

A pipeline works as follows:

1. Select a channel in your ML discord server
2. We take data from discord using [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter)
3. Filter big json files with small `jq` program to fit longer conversation in 100k token budget
4. Going over message history in batches
    1. Extracting conversation threads metadata with "Claude 2" function calls
    2. Iterating over topics, extracting each relevant thread, and converting into markdown file
5. publishing as hugo website


For the testing purposes I chose "hall/help" channel in [LAION](https://laion.ai/) discord server.


Using `discordchatexporter` to download json with messages.

```commandline
docker run --rm  -v /tmp/dce_output:/dce_output tyrrrz/discordchatexporter export -t '$DTOKEN' -c '$CHANNELID' -o '/dce_output/' -f 'Json'
```

It has too many irrelevant fields:

```json
"messages": [
    {
      "id": "1100516799390429195",
      "type": "Default",
      "timestamp": "2023-04-25T20:20:51.588+00:00",
      "timestampEdited": null,
      "callEndedTimestamp": null,
      "isPinned": false,
      "content": "cause Im a child - first",
      "author": {
        "id": "361704756575600660",
        "name": "dudewhatzup",
        "discriminator": "0000",
        "nickname": "Dudewhatzup",
        "color": "#749074",
        "isBot": false,
        "roles": [
          {
            "id": "1053371565934395463",
            "name": "model-trainer",
            "color": "#749074",
            "position": 20
          }
        ],
        "avatarUrl": "https://cdn.discordapp.com/avatars/361704756575600660/7bbc6b3a6d83e186663a6b10e46e1c20.png?size=512"
      },
      "attachments": [],
      "embeds": [],
      "stickers": [],
      "reactions": [],
      "mentions": []
    },
]
```

remove them with `jq`.

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

then run `anthropic_hackathon.py` notebook, which converts `help_messages.json` to markdown files. 


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
