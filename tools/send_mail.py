import socket

PORT = 10006


async def send_mail(msg):
    """
    Sends a mail
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', PORT))
    client.send(msg.encode())
    client.close()
