import http.server
import socketserver
import json
import os
import uuid
from urllib.parse import parse_qs, urlparse

BASE_DIR = r'D:\trae\site'
CHARACTERS_DIR = os.path.join(BASE_DIR, 'characters')

if not os.path.exists(CHARACTERS_DIR):
    os.makedirs(CHARACTERS_DIR)

class APIHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/characters':
            self.get_all_characters()
        elif parsed_path.path.startswith('/api/character/'):
            char_id = parsed_path.path.split('/')[-1]
            self.get_character(char_id)
        else:
            super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/character':
            self.save_character()
        elif parsed_path.path == '/api/import':
            self.import_characters()
        else:
            self.send_error(404)

    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/api/character/'):
            char_id = parsed_path.path.split('/')[-1]
            self.delete_character(char_id)
        else:
            self.send_error(404)

    def do_PUT(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/api/character/'):
            char_id = parsed_path.path.split('/')[-1]
            self.update_character(char_id)
        elif parsed_path.path.startswith('/characters/') and parsed_path.path.endswith('.json'):
            char_id = parsed_path.path.split('/')[-1].replace('.json', '')
            self.update_character(char_id)
        else:
            self.send_error(404)

    def get_all_characters(self):
        characters = []
        try:
            for filename in os.listdir(CHARACTERS_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(CHARACTERS_DIR, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        characters.append(json.load(f))
        except Exception as e:
            self.send_error(500, str(e))
            return
        
        self.send_json_response(characters)

    def get_character(self, char_id):
        filepath = os.path.join(CHARACTERS_DIR, f'{char_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                character = json.load(f)
            self.send_json_response(character)
        else:
            self.send_error(404, 'Character not found')

    def save_character(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 50 * 1024 * 1024:
                self.send_error(413, 'Request too large')
                return
            
            post_data = self.rfile.read(content_length)
            character = json.loads(post_data.decode('utf-8'))
            
            if 'id' not in character or not character['id']:
                character['id'] = str(int(uuid.uuid4().int >> 64))
            
            char_id = character['id']
            filepath = os.path.join(CHARACTERS_DIR, f'{char_id}.json')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(character, f, ensure_ascii=False, indent=2)
            
            self.send_json_response({'success': True, 'id': char_id})
        except Exception as e:
            self.send_error(500, str(e))

    def update_character(self, char_id):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 50 * 1024 * 1024:
                self.send_error(413, 'Request too large')
                return
            
            post_data = self.rfile.read(content_length)
            character = json.loads(post_data.decode('utf-8'))
            
            filepath = os.path.join(CHARACTERS_DIR, f'{char_id}.json')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(character, f, ensure_ascii=False, indent=2)
            
            self.send_json_response({'success': True, 'id': char_id})
        except Exception as e:
            self.send_error(500, str(e))

    def delete_character(self, char_id):
        filepath = os.path.join(CHARACTERS_DIR, f'{char_id}.json')
        
        if os.path.exists(filepath):
            os.remove(filepath)
            self.send_json_response({'success': True})
        else:
            self.send_error(404, 'Character not found')

    def import_characters(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 100 * 1024 * 1024:
                self.send_error(413, 'Request too large')
                return
            
            post_data = self.rfile.read(content_length)
            characters = json.loads(post_data.decode('utf-8'))
            
            if not isinstance(characters, list):
                self.send_error(400, 'Expected array of characters')
                return
            
            for char in characters:
                if 'id' in char:
                    char_id = char['id']
                    filepath = os.path.join(CHARACTERS_DIR, f'{char_id}.json')
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(char, f, ensure_ascii=False, indent=2)
            
            self.send_json_response({'success': True, 'count': len(characters)})
        except Exception as e:
            self.send_error(500, str(e))

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

os.chdir(BASE_DIR)

PORT = 8000

print(f"Server running at http://localhost:{PORT}")
print(f"Characters will be saved to: {CHARACTERS_DIR}")
print("Press Ctrl+C to stop the server")

with socketserver.ThreadingTCPServer(("", PORT), APIHandler) as httpd:
    httpd.serve_forever()