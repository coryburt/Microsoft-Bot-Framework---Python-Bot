# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from aiohttp import (web, ClientSession)
from botbuilder.schema import (Activity, ActivityTypes)
from botbuilder.core import (BotFrameworkAdapter, BotFrameworkAdapterSettings, BotContext)
import json


# AZURE services keys withheld here... Git yer own.
SECOND_KEY = ''
AZURE_KEY = ''


SENTIMENT_URL = 'https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment'
HEADERS = {
    'Ocp-Apim-Subscription-Key': AZURE_KEY,
    'content-type': 'application/json'
}

APP_ID = ''
APP_PASSWORD = ''
PORT = 9000
SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


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
            return( await response.json() )

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
    response = await create_reply_activity(
        context.request, 'Sentiment response for: "{}" is:\n{}.'.format(context.request.text, sentiment)
    )
    await context.send_activity(response)
    return web.Response(status=202)


async def handle_conversation_update(context: BotContext) -> web.Response:
    if context.request.members_added[0].id != context.request.recipient.id:
        response = await create_reply_activity(context.request, 'Welcome to Cory\'s sentiment server!')
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
