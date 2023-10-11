import logging
import aiohttp
import asyncio
import base64
import json
import server.utils as utils

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

log = logging.getLogger(__name__)


async def process_message(message, session, options):
    log.debug(f"process message: {utils.mask_ddk(message)!r}")
    trx = message['37']
    params = {
        "recipient_pan": message['2'],
        "amount": message['4'],
        "transaction": trx,
        "description": "payout_{}".format(trx)
    }

    data = json.dumps(params, separators=(',', ':'), sort_keys=True)

    key = RSA.importKey(open(options.pkey).read())
    digest = SHA256.new('{}{}'.format(data, options.secret_key).encode('utf8'))
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(digest)
    x_signature = base64.b64encode(signature)

    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'x-api-key': options.api_key,
        'x-signature': x_signature.decode('utf8'),
    }

    try:
        async with session.post('/v1/orders/account2card', data=data, headers=headers) as resp:
            log.debug(f"result http code {resp.status!r} for message with trx {trx!r}")

            match resp.status:
                case 200:
                    result = await resp.json()
                    log.debug(f"result {result!r} for message with trx {trx!r}")
                    match result.get('status'):
                        case "completed":
                            message['39'] = '00'
                        case "canceled":
                            message['39'] = '05'
                        case "new":
                            message['39'] = '10'
                        case "processing":
                            message['39'] = '10'
                        case _:
                            message['39'] = '05'
                case 400:
                    result = await resp.text()
                    log.debug(f"result {result!r} for message with trx {trx!r}")
                    message['39'] = '05'
                case 500:
                    result = await resp.text()
                    log.debug(f"result {result!r} for message with trx {trx!r}")
                    message['39'] = '05'
                case _:
                    result = await resp.text()
                    log.debug(f"result {result!r} for message with trx {trx!r}")
                    message['39'] = '10'

    except Exception as e:
        log.exception(e)
        message['39'] = '10'
    finally:
        message['t'] = utils.build_response_mti(message['t'])
        message.pop('2', None)

    return message


async def process_messages(messages, options):
    timeout = aiohttp.ClientTimeout(
        total=options.oct_timeout,
        connect=options.oct_connect_timeout,
        sock_connect=options.oct_connect_timeout,
        sock_read=options.oct_read_timeout
    )
    async with aiohttp.ClientSession(options.oct_url, timeout=timeout, trust_env=True) as session:
        tasks = []
        for message in messages:
            tasks.append(asyncio.ensure_future(process_message(message, session, options)))

        processed_messages = await asyncio.gather(*tasks)

    return processed_messages
