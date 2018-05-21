# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from aiohttp import (web, ClientSession)
from botbuilder.schema import (Activity, ActivityTypes)
from botbuilder.core import (BotFrameworkAdapter, BotFrameworkAdapterSettings, BotContext)
import json
import re


# AZURE services keys withheld here... Git yer own.
AZURE_KEY = ''
SECOND_KEY = ''

SENTIMENT_URL = 'https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment'
KEYPHRASE_URL = 'https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/keyPhrases'

HEADERS = {
    'Ocp-Apim-Subscription-Key': AZURE_KEY,
    'content-type': 'application/json'
}

ABOUT_DAISY = False
ACCUMULATED_SENTIMENT = 0.0
DAISY_QUERY_ACTIVE = True

IS_DAISY = re.compile(r'\bdaisy\b', re.I)

APP_ID = ''
APP_PASSWORD = ''
PORT = 9000
SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


def analyze_sentiment(sentiment):
    global ACCUMULATED_SENTIMENT

    score = float(sentiment['documents'][0]['score'])
    if score < 0.5:
        ACCUMULATED_SENTIMENT = -1
    elif score > 0.5:
        ACCUMULATED_SENTIMENT = 1
    else:
        ACCUMULATED_SENTIMENT = 0


def test_for_daisy(keyPhrases):
    global ABOUT_DAISY
    global DAISY_QUERY_ACTIVE

    score = keyPhrases['documents'][0]['keyPhrases']
    result = list(filter(IS_DAISY.match, score))

    if len(result) > 0:
        ABOUT_DAISY = True
        DAISY_QUERY_ACTIVE = False


def answer_maker():
    global ABOUT_DAISY
    global ACCUMULATED_SENTIMENT
    global DAISY_QUERY_ACTIVE

    ans = 'These feelings seem to be '
    if ACCUMULATED_SENTIMENT > 0:
        ans += 'on the positive side.\n'
    elif ACCUMULATED_SENTIMENT < 0:
        ans += 'on the negative side.\n'
    else:
        ans += 'fairly neutral.\n'

    if DAISY_QUERY_ACTIVE == True:
        ans += "Enter \"Daisy\" if we are still talking about Daisy's performance?\n"
    else:
        ans += 'Anything more to add?\n'

    return ans


async def fetch_sentiment(review):
    body = { 'documents': [
        {
            'language': 'en',
            'id': '1',
            'text': '"{}"'.format(review)
        }
    ]}
    async with ClientSession() as session:
        async with session.post(SENTIMENT_URL, data=json.dumps(body), headers=HEADERS ) as response:
            return await response.json()


async def fetch_keyphrases(review):
    body = { 'documents': [
        {
            'language': 'en',
            'id': '1',
            'text': '"{}"'.format(review)
        }
    ]}
    async with ClientSession() as session:
        async with session.post(KEYPHRASE_URL, data=json.dumps(body), headers=HEADERS ) as response:
            return await response.json()


async def create_reply_activity(request_activity, text) -> Activity:
    return Activity(
        type=ActivityTypes.message,
        channel_id=request_activity.channel_id,
        conversation=request_activity.conversation,
        recipient=request_activity.from_property,
        from_property=request_activity.recipient,
        text=text,
        service_url=request_activity.service_url)


async def handle_message(context: BotContext) -> web.Response:
    sentiment = await fetch_sentiment(context.request.text)
    keyphrases = await fetch_keyphrases(context.request.text)
    test_for_daisy(keyphrases)
    analyze_sentiment(sentiment)
    message = answer_maker()
    response = await create_reply_activity(
        context.request, message
    )
    await context.send_activity(response)
    return web.Response(status=202)


async def handle_conversation_update(context: BotContext) -> web.Response:
    if context.request.members_added[0].id != context.request.recipient.id:
        msg = 'Welcome to the review aggregator.\n'
        msg += "Please tell me what you thought of Daisy Ridley's\n"
        msg += "performance as \"Rey\" in Star Wars: The Force Awakens"
        response = await create_reply_activity(context.request, msg)
        await context.send_activity(response)
    return web.Response(status=200)


async def unhandled_activity() -> web.Response:
    return web.Response(status=404)


async def request_handler(context: BotContext) -> web.Response:
    if context.request.type == 'message':
        return await handle_message(context)
    elif context.request.type == 'conversationUpdate':
        return await handle_conversation_update(context)
    else:
        return await unhandled_activity()


async def messages(req: web.web_request) -> web.Response:
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers['Authorization'] if 'Authorization' in req.headers else ''
    try:
        return await ADAPTER.process_request(activity, auth_header, request_handler)
    except Exception as e:
        raise e


app = web.Application()
app.router.add_post('/', messages)

try:
    web.run_app(app, host='localhost', port=PORT)
except Exception as e:
    raise e
