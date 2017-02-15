import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)
api_key = "AIzaSyDdGWh2QwcYHLEJOQGwKejtHY-PUC_5znc"

base_url_radar      = "https://maps.googleapis.com/maps/api/place/radarsearch/json"
base_url_details    = "https://maps.googleapis.com/maps/api/place/details/json"

oslo_latlng = "59.913869,10.752245"
radius      = "4000" #4km

def _initialise(bot):
    plugins.register_user_command(["whereto"])

def get_map(bot, latlng):
    url = "https://maps.googleapis.com/maps/api/staticmap"
    url += "?center=" + str(latlng["lat"]) + "," + str(latlng["lng"]) + "&zoom=18"
    url += "&size=400x400"
    url += "&markers=color:red%7Clabel:%7C" + str(latlng["lat"]) + "," + str(latlng["lng"])
    url += "&key=" + api_key

    filename = os.path.basename(url)
    r = yield from aiohttp.request('get', url)
    raw = yield from r.read()
    image_data = io.BytesIO(raw)
    img_id = yield from bot._client.upload_image(image_data, filename=filename)
    return img_id

def query(bot, event, qtype, args):
    url = base_url_radar
    url += '?location=' + oslo_latlng
    url += '&radius=' + radius
    url += '&type=' + qtype
    url += '&opennow=true'
    url += '&key=' + api_key

    r = yield from aiohttp.request("get", url)
    r_json = yield from r.json()

    if len(r_json["results"]) == 0:
        yield from bot.coro_send_message(event.conv_id, "No hits.")
        return

    place = r_json["results"][random.randint(0,len(r_json["results"])-1)]

    url = base_url_details
    url += '&placeid=' + place["place_id"]
    url += '&key=' + api_key

    r = yield from aiohttp.request("get", url)
    r_json = yield from r.json()
    place = r_json["results"]

    link = place["url"]
    name = place["name"]
    addr = place["vicinity"]

    image_id = get_map(bot, place["geometry"]["location"])
    yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)
    yield from bot.coro_send_message(event.conv_id, "We go to " + name + " at " + addr + ". Find it here: " + link )

def whereto(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 0:
        return

    what = args[0].lower().trim()
    if what is "drunk":
        query(bot, event, 'bar', args[-1:])
    else if what is "food":
        query(bot, event, 'restaurant', args[-1:])
    else:
        yield from bot.coro_send_message(event.conv_id, "I don't know where to " + what)