import socket

PORT = 10006
mail_storage = {}


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', PORT))
    server.listen(5)
    print('Server started. Waiting for connections...')
    while True:
        client, addr = server.accept()
        print('Got connection from', addr)
        msg = client.recv(1024).decode()
        store_mail("user_0", msg)
        client.close()


def store_mail(identifier, mail):
    """
    Stores the mail in the mail_storage dictionary.
    """
    if identifier in mail_storage:
        mail_storage[identifier].append(mail)
    else:
        mail_storage[identifier] = [mail]
    print(f'Mail stored for {identifier}')


def get_mail(identifier):
    """
    Retrieves stored mails for a given identifier.
    """
    output = mail_storage.get(identifier, [])
    mail_storage[identifier] = []
    return output
