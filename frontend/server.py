# server.py
# This file is needed to correctly serve the static PWA files on deployment.

import subprocess
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Define the host and port
HOST = '0.0.0.0'
PORT = 8000

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve files from the 'static' directory
        super().__init__(*args, directory='static', **kwargs)

def run_streamlit():
    # Command to run the Streamlit app
    # Make sure 'app.py' is the name of your main Streamlit file
    command = "streamlit run app.py --server.port {}".format(PORT)
    subprocess.Popen(command, shell=True)

if __name__ == '__main__':
    # Start the Streamlit app in a separate process
    run_streamlit()

    # Start the simple HTTP server to serve the static files
    httpd = HTTPServer((HOST, PORT), CustomHandler)
    print(f"Serving static files from /static at http://{HOST}:{PORT}")
    httpd.serve_forever()
