
import asyncio
from networking.protocol import decode_message, create_message, encode_message


class UDPServer(asyncio.DatagramProtocol):

    def connection_made(self, transport):
        self.transport = transport
        address = transport.get_extra_info("sockname")
        print(f"MeshWeaver UDP Server running at {address}")

    def datagram_received(self, data, addr):
        try:
            message = decode_message(data)

            print(f"Received from {addr}: {message}")

            message_type = message.get("message_type")

            if message_type == "PING":
                response = create_message(
                    sender_id="server",
                    message_type="PONG",
                    payload={"status": "alive"}
                )

                self.transport.sendto(
                    encode_message(response),
                    addr
                )

        except Exception as error:
            print(f"Error processing message: {error}")

    def error_received(self, error):
        print(f"UDP server error: {error}")


async def start_server(host="127.0.0.1", port=9999):

    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        UDPServer,
        local_addr=(host, port)
    )

    try:
        await asyncio.Future()
    finally:
        transport.close()


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\nMeshWeaver UDP Server stopped")
