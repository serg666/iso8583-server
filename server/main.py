import os
import sys
import logging
import logging.config
import asyncio
import iso8583
import optparse
import server.utils as utils
import server.oct as oct

from server.visa_sms import spec

log = logging.getLogger(__name__)

# @note: count of bytes for message length
MSG_LEN_BYTES = 4
MSG_LEN_BYTES_REAL = 2

class OptionParser(optparse.OptionParser, object):
    def get_default_values(self):
        values = super(OptionParser, self).get_default_values()
        values._seen = values.__dict__.copy()
        return values

    def error(self, msg):
        self.print_help(sys.stderr)
        self.exit(2, "%s: error: %s\n" % (self.get_prog_name(), msg))


class Option(optparse.Option, object):
    def process(self, opt, value, values, parser):
        super(Option, self).process(opt, value, values, parser)
        values._seen[self.dest] = True


class ISO8583Protocol(asyncio.Protocol):
    def __init__(self, options, *args, **kwargs):
        self.options = options
        super(ISO8583Protocol, self).__init__(*args, **kwargs)

    def connection_made(self, transport):
        self.addr = transport.get_extra_info('peername')
        log.debug(f"Connection from {self.addr!r}")
        self.transport = transport

    def connection_lost(self, exc):
        log.debug(f"Connection to {self.addr!r} closed")

    def _encode_message(self, message):
        msg, encoded = iso8583.encode(message, spec)
        msg_length = len(msg)
        msg_length_decoded = msg_length.to_bytes(MSG_LEN_BYTES, 'big')[MSG_LEN_BYTES_REAL:] + \
            msg_length.to_bytes(MSG_LEN_BYTES, 'big')[:MSG_LEN_BYTES_REAL]
        return msg_length_decoded + msg[:3] + msg_length.to_bytes(MSG_LEN_BYTES, 'big')[MSG_LEN_BYTES_REAL:] + msg[3 + MSG_LEN_BYTES_REAL:]

    def message_processed(self, task):
        try:
            encoded_msg = self._encode_message(task.result())
            log.debug(f"Send processed: {encoded_msg.hex()!r} to {self.addr!r}")
            self.transport.write(encoded_msg)

        except Exception as e:
            log.exception(e)
            # @note: bank will get time out
            log.debug("Send nothing")

    def messages_processed(self, task):
        try:
            total_msg = b''
            for message in task.result():
                total_msg += self._encode_message(message)

            log.debug(f"Send processed: {total_msg.hex()!r} to {self.addr!r}")
            self.transport.write(total_msg)

        except Exception as e:
            log.exception(e)
            # @note: bank will get time out
            log.debug("Send nothing")

    def data_received(self, msg):
        log.debug(f"Received hex msg {msg.hex()!r} from {self.addr!r}")
        messages = []

        try:
            while len(msg) > 0:
                # @note: message length (first N bytes)
                msg_len_encoded = msg[:MSG_LEN_BYTES]
                log.debug(f"Message length is {msg_len_encoded!r}")
                if len(msg_len_encoded) < MSG_LEN_BYTES:
                    raise AttributeError("Message length is less {} bytes: {}".format(MSG_LEN_BYTES, len(msg_len_encoded)))

                # @note: use only first REAL bytes as length
                msg_len = int.from_bytes(msg_len_encoded[:MSG_LEN_BYTES_REAL], 'big')
                log.debug(f"Decoded message length is {msg_len!r}")

                msg_itself = msg[MSG_LEN_BYTES: MSG_LEN_BYTES + msg_len]
                decoded, encoded = iso8583.decode(msg_itself, spec)
                log.debug(f"Decoded msg {utils.mask_ddk(decoded)!r} from {self.addr!r}")
                messages.append(decoded)

                asyncio.create_task(oct.process_one_message(decoded, self.options)).add_done_callback(self.message_processed)

                msg = msg[MSG_LEN_BYTES + msg_len:]

            #task = asyncio.create_task(oct.process_messages(messages, self.options))
            #task.add_done_callback(self.messages_processed)
        except Exception as e:
            log.exception(e)
            # @note: bank will get time out
            log.debug("Send nothing")


async def start_server(options):
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: ISO8583Protocol(options),
        options.host, options.port)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    log.debug(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()


def serve():
    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    opts = [Option('--host', metavar='HOST', dest='host',
                   default='127.0.0.1', help='Start serving on host (default: %default)'),
            Option('--port', metavar='PORT', dest='port',
                   default=9999, type=int, help='Start serving on port (default: %default)'),
            Option('--log-config', metavar='PATH', dest='logconfig',
                   default='log.conf', help='Logging configuration file '
                                            '(default: %default)'),
            Option('--api-key', metavar='API_KEY', dest='api_key',
                   default=os.environ.get('API_KEY'),
                   help='API key for OCT service (default: %default)'),
            Option('--secret-key', metavar='SECRET_KEY', dest='secret_key',
                   default=os.environ.get('SECRET_KEY'),
                   help='Secret key for OCT service (default: %default)'),
            Option('--private-key', metavar='PATH', dest='pkey',
                   default=os.environ.get('PRIVATE_KEY'),
                   help='Private key full path for OCT service (default: %default)'),
            Option('--oct-url', metavar='URL', dest='oct_url',
                   default=None, help='OCT service url (default: %default) '
                                      'For example https://some.host'),
            Option('--oct-timeout', metavar='TIMEOUT', dest='oct_timeout',
                   default=90, type=int, help='The maximal number of seconds for the '
                                              'whole operation including connection '
                                              'establishment, request sending and '
                                              'response reading from oct service. '
                                              '(default: %default)'),
            Option('--oct-connect-timeout', metavar='TIMEOUT', dest='oct_connect_timeout',
                   default=5, type=int, help='The maximal number of seconds for connecting '
                                             'to a peer for a new connection (default: %default)'),
            Option('--oct-read-timeout', metavar='TIMEOUT', dest='oct_read_timeout',
                   default=90, type=int, help='The maximal number of seconds allowed for '
                                              'period between reading a new data portion '
                                              'from a peer. (default: %default)'),
            ]
    parser.add_options(opts)
    options, args = parser.parse_args(sys.argv)
    if None in options._seen.values():
        parser.error('all options are mandatory')

    logging.config.fileConfig(options.logconfig)
    asyncio.run(start_server(options))
