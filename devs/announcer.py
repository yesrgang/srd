import asyncio
import socket
import sys

feeds = {}
messages = {}

def consume(data):
    parts = data.partition(b' ')
    return parts[0].decode(), parts[2]

async def handle_request(reader, writer):
    read = await reader.read(1024)
    method, arg = consume(read)
    print(method, arg)

    if method.upper() == 'LISTEN':
        feed = arg.decode()
        if feed not in feeds:
            feeds[feed] = asyncio.Event()
        await feeds[feed].wait()
        writer.write(messages[feed])
        await writer.drain()
    if method.upper() == 'ANNOUNCE':
        feed, message = consume(arg)
        if feed not in feeds:
            feeds[feed] = asyncio.Event()
        messages[feed] = message
        writer.write(messages[feed])
        await writer.drain()
        feeds[feed].set()

async def main():
    server = await asyncio.start_server(handle_request, '0.0.0.0', 0)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'announcer serving on {addrs}')

    if len(sys.argv) == 2:
        pid = sys.argv[1]
        port = server.sockets[0].getsockname()[1]
        stmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stmp.connect(("localhost", 42922))
        stmp.send(f"PORT {pid} {port}".encode())

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main(), debug=False)
