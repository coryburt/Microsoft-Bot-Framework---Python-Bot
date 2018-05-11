# Microsoft-Bot-Framework---Python-Bot

## A Thesaurus Bot Server, by Cory Burt

This is a simple bot server based on the <a href="https://github.com/Microsoft/BotBuilder-python" target="_blank">Microsoft BotBuilder Framework for Python</a>.&nbsp; Once running, you may send it a word and it will respond with a list of synonyms and related phrases, as provided by thesaurus.altervista.org.

To run this server, install the requirements (requirements.txt), and enter:

```
python main.py
```

Which will run on http://localhost:9000, by default.

To test this server, you must use the <a href="https://github.com/Microsoft/BotFramework-Emulator" target="_blank">Microsoft Bot Framework Emulator</a>.&nbsp; Simply install it on your favorite platform and connect a bot to your running server.

#### NOTE, NOTE, NOTE!

As a thesaurus server, this bot server utilizes the thesaurus service provided from <a href="http://thesaurus.altervista.org/" target="_blank">thesaurus.altervista.org</a>.&nbsp; In order to use it successfully, you must visit altervista and register for your own key!&nbsp; (No, you can't have mine).&nbsp;  Once you've obtained a key, replace the string "test_only" in the line:

```
YOUR_KEY = 'test_only'
```
in the bot code with the key string you obtained there.&nbsp; Otherwise, you will get only a warning message from the bot server whenever you attempt to use it.

