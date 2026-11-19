
import asyncio
from networking.protocol import create_message, encode_message, decode_message


class UDPClient(asyncio.DatagramProtocol):

    def __init__(self, message):
        self.message = message
        self.transport = None
        self.response_received = asyncio.get_running_loop().create_future()

    def connection_made(self, transport):
        self.transport = transport

        data = encode_message(self.message)
        self.transport.sendto(data)

        print("Message sent successfully")

    def datagram_received(self, data, addr):
        try:
            response = decode_message(data)
            print(f"Response received from {addr}: {response}")

            if not self.response_received.done():
                self.response_received.set_result(response)

        except Exception as error:
            print(f"Error decoding response: {error}")

    def error_received(self, error):
        print(f"UDP client error: {error}")


async def send_message(
    peer_host,
    peer_port,
    sender_id,
    message_type,
    payload=None
):
    loop = asyncio.get_running_loop()

    message = create_message(
        sender_id=sender_id,
        message_type=message_type,
        payload=payload
    )

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPClient(message),
        remote_addr=(peer_host, peer_port)
    )

    try:
        response = await asyncio.wait_for(
            protocol.response_received,
            timeout=5
        )
        return response

    except asyncio.TimeoutError:
        print("Peer did not respond within 5 seconds.")
        return None

    finally:
        transport.close()


async def main():
    response = await send_message(
        peer_host="127.0.0.1",
        peer_port=9999,
        sender_id="peer_1",
        message_type="PING",
        payload={"status": "checking"}
    )

    print("Final response:", response)


if __name__ == "__main__":
    asyncio.run(main())
