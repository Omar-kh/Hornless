import socket
from io import BytesIO
import sys
import importlib
from threading import Thread

response_headers = []


def parse_request(data):
    headers = data.split("\r\n")
    request_line = headers[0].split()
    if not request_line:
        return {
            "REQUEST_METHOD": "UNKNOWN",
            "PATH_INFO": "/",
            "QUERY_STRING": "",
            "wsgi.input": BytesIO(data.encode()),
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "http",
        }
    method = request_line[0]
    path = request_line[1]
    return {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": "",
        "wsgi.input": BytesIO(data.encode()),
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
    }


def start_response(status, headers):
    response_headers[:] = [status, headers]


def wsgi_handler(client_socket, app):
    request_data = client_socket.recv(1024).decode("utf-8")
    environ = parse_request(request_data)
    response_body = app(environ, start_response)
    send_response(client_socket, response_body)
    client_socket.close()


def send_response(client_socket, response_body):
    response = "HTTP/1.1 " + response_headers[0] + "\r\n"
    for header in response_headers[1]:
        response += f"{header[0]}: {header[1]}\r\n"
    response += "\r\n"
    for data in response_body:
        response += data.decode("utf-8")
    client_socket.sendall(response.encode())


def serve(app, host="127.0.0.1", port=8000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Serving on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        Thread(target=wsgi_handler, args=(client_socket, app)).start()  # Use threading here


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python minimal_gunicorn.py <module_name>:<app_instance>")
        sys.exit(1)

    module_name, app_instance_name = sys.argv[1].split(":")
    module = importlib.import_module(module_name)

    if hasattr(module, app_instance_name):
        app_instance = getattr(module, app_instance_name)
        serve(app_instance)
    else:
        print(f"No '{app_instance_name}' found in {module_name}.")
        sys.exit(1)
