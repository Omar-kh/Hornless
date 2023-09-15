import socket

HOST = '127.0.0.1'
PORT = 8080
QUEUE_SIZE = 3

# Create a new socket using the given address family and socket type

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(QUEUE_SIZE)
print(f"Server listening on {HOST}:{PORT}")

while True:
  client_socket, address = server_socket.accept()
  request = client_socket.recv(1024).decode('utf-8')

  if request.startswith("GET"):
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello, World!"
  else:
    response = "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nInvalid request!"

  print(f"Received request:\n{request}")
  response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello, World!"
  client_socket.sendall(response.encode())
  client_socket.close()