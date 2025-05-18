#!/usr/bin/env python3
"""
Simple HTTP server for viewing Bedrock testing results
"""

import http.server
import socketserver
import os
import json
import re
from urllib.parse import urlparse, parse_qs

# Import configuration
import config

class BedrockResultsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        
        # API endpoint to list JSON files
        if parsed_url.path == '/api/list-files':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Get all JSON files in the outputs directory using config
            output_dir = os.path.join(os.getcwd(), config.output_dir)
            files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            
            self.wfile.write(json.dumps(files).encode())
            return
        
        # API endpoint to get configuration
        if parsed_url.path == '/api/config':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Send relevant configuration to the client
            client_config = {
                'outputDir': config.output_dir
            }
            
            self.wfile.write(json.dumps(client_config).encode())
            return
        
        # Serve the viewer HTML for the root path
        if parsed_url.path == '/' or parsed_url.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            with open('viewer.html', 'rb') as file:
                html_content = file.read().decode('utf-8')
                
                # Inject configuration into the HTML
                config_script = f"""
                <script>
                    // Configuration from server
                    var outputDir = '{config.output_dir}';
                </script>
                """
                
                # Insert the config script right before the first <script> tag
                html_content = re.sub(
                    r'(<script)',
                    f'{config_script}\\1',
                    html_content,
                    count=1
                )
                
                self.wfile.write(html_content.encode())
            return
            
        # Default handler for other paths (like accessing JSON files)
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    PORT = 8000
    
    with socketserver.TCPServer(("", PORT), BedrockResultsHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print(f"Open your browser and navigate to http://localhost:{PORT} to view results")
        print(f"Serving files from the '{config.output_dir}' directory")
        httpd.serve_forever()
