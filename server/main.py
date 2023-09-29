import os
import sys
import logging
import logging.config
import asyncio
import iso8583
import optparse

from iso8583.specs import default_ascii as spec

log = logging.getLogger(__name__)


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


def build_response_mti(mti):
    """Build response MTI (message type identifier)
    """

    return mti[:2] + str(int(mti[2]) + 1) + mti[3]


class ISO8583Protocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.addr = transport.get_extra_info('peername')
        log.debug(f"Connection from {self.addr!r}")
        self.transport = transport

    def connection_lost(self, exc):
        log.debug(f"Connection to {self.addr!r} closed")

    def data_received(self, msg):
        log.debug(f"Received {msg!r} from {self.addr!r}")

        try:
            decoded, encoded = iso8583.decode(msg, spec)
            log.debug(f"Decoded msg {decoded!r} from {self.addr!r}")

            decoded['t'] = build_response_mti(decoded['t'])
            decoded['39'] = '01'
            decoded.pop('2', None)

            msg, encoded = iso8583.encode(decoded, spec)
        except Exception as e:
            log.exception(e)

        log.debug(f"Send: {msg!r} to {self.addr!r}")
        self.transport.write(msg)

        #print('Close the client socket')
        #self.transport.close()


async def start_server(options):
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: ISO8583Protocol(),
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
            ]
    parser.add_options(opts)
    options, args = parser.parse_args(sys.argv)
    if None in options._seen.values():
        parser.error('all options are mandatory')

    logging.config.fileConfig(options.logconfig)
    asyncio.run(start_server(options))
