import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)
client_id = 'b144351ffb05838'
url = 'https://api.imgur.com/3/gallery/random/random/0'
headers = {'Authorization': 'Client-ID ' + client_id, 'Accept': 'application/json'}

def _initialise(bot):
    plugins.register_handler(on_msg, type="message", priority=5)
    plugins.register_user_command(["imgur"])


def on_msg(bot, event, command):
    if "#imgur" in event.text:
        yield from fetch(bot, event)
		
def imgur(bot, event, *args):
	yield from fetch(bot, event)
		
def fetch(bot, event):
    r = yield from aiohttp.request('get', url, headers=headers)
    r_json = yield from r.json()

    if len(r_json['data']) == 0:
        yield from bot.coro_send_message(event.conv_id, 'No hits.')
        return


    var number = random.randint(0,len(r_json['data'])-1)
    var nsfw = true;

    while nsfw:
        if (r_json['data'][number]['nswf']):
            number = random.randint(0,len(r_json['data'])-1)
        else:
            image_link = r_json['data'][number]['link']
            nsfw = false

    filename = os.path.basename(image_link)
    r = yield from aiohttp.request('get', image_link)
    raw = yield from r.read()
    image_data = io.BytesIO(raw)
    image_id = yield from bot._client.upload_image(image_data, filename=filename)
    yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)