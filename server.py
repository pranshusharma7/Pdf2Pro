"""
PDF Converter Pro - Local Development Server
Handles static file serving + GitHub OAuth token exchange
"""

import http.server
import json
import urllib.request
import urllib.parse
import os
import sys
import ssl
import base64
import hashlib
import uuid
import time

# Fix SSL certificate issue on macOS
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

PORT = 3000

# =============================================
# GitHub OAuth Credentials
# =============================================
GITHUB_CLIENT_ID = 'Ov23liQ5roaTx7tT7vvS'
GITHUB_CLIENT_SECRET = '370eef722309481a0925b3fba20541f49240d183'

# =============================================
# PhonePe Credentials
# =============================================
PHONEPE_MERCHANT_ID = 'M231F5SB06Y32_2602200226'
PHONEPE_SALT_KEY = 'N2Q5MWJmNDgtNmM1Ny00NTRmLTg2NzUtNWQ3MTY2ZDQ3YmY3'
PHONEPE_SALT_INDEX = '1'

PHONEPE_API_URL = 'https://api.phonepe.com/apis/hermes/pg/v1/pay'
# Use this for sandbox testing if the prod one above says invalid API key
# PHONEPE_API_URL = 'https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay'

# =============================================
# Custom HTTP Request Handler
# =============================================

CONVERTAPI_SECRET      = '63RwmHsSY9g1KGqdhP0WeWSARJcthzIG'    # ConvertAPI key — all tools (backend only)
CONVERTAPI_EXCEL_SECRET = 'jtlnGyk2AjH33GqjoU2myDqLYeIdnvaC'   # ConvertAPI key — PDF to Excel only
CONVERTAPI_MERGE_URL   = 'https://v2.convertapi.com/convert/pdf/to/merge'

class AuthHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests - serve static files + GitHub callback API"""
        
        # GitHub OAuth Token Exchange API
        if self.path.startswith('/api/github/callback'):
            self.handle_github_callback()
            return
        
        # GitHub User Info API
        if self.path.startswith('/api/github/user'):
            self.handle_github_user()
            return
        
        # Converted file download
        if self.path.startswith('/api/download/'):
            self.handle_download()
            return

        # Default: serve static files
        super().do_GET()
    
    def do_POST(self):
        """Handle POST requests - Payment Initiation and Callbacks"""
        if self.path.startswith('/api/payment/initiate'):
            self.handle_payment_initiate()
            return
        
        if self.path.startswith('/api/payment/callback'):
            self.handle_payment_callback()
            return
            
        if self.path.startswith('/api/convert/'):
            # Extract tool ID from path, e.g., /api/convert/pdf-to-word -> pdf-to-word
            tool_id = self.path.split('/')[-1]
            self.handle_conversion(tool_id)
            return
        

            
        self.send_json_response(404, {'error': 'Not found'})

    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
        self.end_headers()
    
    def handle_github_callback(self):
        """Exchange GitHub auth code for access token"""
        # Parse query parameters
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        code = params.get('code', [None])[0]
        
        if not code:
            self.send_json_response(400, {'error': 'No code provided'})
            return
        
        if not GITHUB_CLIENT_SECRET:
            self.send_json_response(500, {
                'error': 'GitHub Client Secret not configured',
                'message': 'Please add your GITHUB_CLIENT_SECRET in server.py'
            })
            return
        
        try:
            # Exchange code for access token
            token_data = urllib.parse.urlencode({
                'client_id': GITHUB_CLIENT_ID,
                'client_secret': GITHUB_CLIENT_SECRET,
                'code': code
            }).encode()
            
            token_req = urllib.request.Request(
                'https://github.com/login/oauth/access_token',
                data=token_data,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            
            with urllib.request.urlopen(token_req, context=ssl_context) as response:
                token_result = json.loads(response.read().decode())
            
            if 'access_token' not in token_result:
                self.send_json_response(400, {
                    'error': 'Token exchange failed',
                    'details': token_result
                })
                return
            
            access_token = token_result['access_token']
            
            # Fetch user profile with the access token
            user_req = urllib.request.Request(
                'https://api.github.com/user',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'PDF-Converter-Pro'
                }
            )
            
            with urllib.request.urlopen(user_req, context=ssl_context) as response:
                user_data = json.loads(response.read().decode())
            
            # Also try to get email if not public
            email = user_data.get('email')
            if not email:
                try:
                    email_req = urllib.request.Request(
                        'https://api.github.com/user/emails',
                        headers={
                            'Authorization': f'Bearer {access_token}',
                            'Accept': 'application/vnd.github.v3+json',
                            'User-Agent': 'PDF-Converter-Pro'
                        }
                    )
                    with urllib.request.urlopen(email_req, context=ssl_context) as response:
                        emails = json.loads(response.read().decode())
                        primary = next((e for e in emails if e.get('primary')), None)
                        if primary:
                            email = primary['email']
                except:
                    email = f"{user_data.get('login', 'user')}@github.com"
            
            # Return user profile
            self.send_json_response(200, {
                'success': True,
                'user': {
                    'name': user_data.get('name') or user_data.get('login', 'GitHub User'),
                    'email': email or f"{user_data.get('login')}@github.com",
                    'picture': user_data.get('avatar_url', ''),
                    'login': user_data.get('login', ''),
                    'bio': user_data.get('bio', ''),
                    'loginMethod': 'github',
                    'type': 'pro'
                }
            })
            
        except Exception as e:
            self.send_json_response(500, {
                'error': 'Server error',
                'message': str(e)
            })

    def handle_payment_initiate(self):
        """Initiate PhonePe Payment Session"""
        print("Handling /api/payment/initiate...", flush=True)
        content_length = int(self.headers.get('Content-Length', 0))
        print(f"Content length: {content_length}", flush=True)
        body = self.rfile.read(content_length)
        print(f"Body read: {body}", flush=True)
        
        try:
            req_data = json.loads(body.decode())
            print(f"Req data: {req_data}", flush=True)
            amount = int(req_data.get('amount', 0)) * 100 # In paise
            plan_name = req_data.get('plan', 'Pro')
            
            if amount <= 0:
                self.send_json_response(400, {'error': 'Invalid amount'})
                return
                
            transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
            merchant_user_id = f"UID{uuid.uuid4().hex[:8].upper()}"
            
            # The host of the server, typically localhost:3000 but if accessed via localtunnel we should use the origin
            origin = self.headers.get('Origin', f'http://localhost:{PORT}')
            redirect_url = f"{origin}/api/payment/callback"
            
            payload = {
                "merchantId": PHONEPE_MERCHANT_ID,
                "merchantTransactionId": transaction_id,
                "merchantUserId": merchant_user_id,
                "amount": amount,
                "redirectUrl": redirect_url,
                "redirectMode": "POST",
                "callbackUrl": redirect_url,
                "mobileNumber": "9999999999",
                "paymentInstrument": {
                    "type": "PAY_PAGE"
                }
            }
            
            payload_json = json.dumps(payload)
            base64_payload = base64.b64encode(payload_json.encode()).decode('utf-8')
            
            # Calculate X-VERIFY
            sign_string = base64_payload + "/pg/v1/pay" + PHONEPE_SALT_KEY
            m = hashlib.sha256()
            m.update(sign_string.encode('utf-8'))
            checksum = m.hexdigest() + "###" + PHONEPE_SALT_INDEX
            
            headers = {
                'Content-Type': 'application/json',
                'X-VERIFY': checksum,
                'X-MERCHANT-ID': PHONEPE_MERCHANT_ID,
                'User-Agent': 'PDF-Converter-Pro'
            }
            
            req = urllib.request.Request(
                PHONEPE_API_URL,
                data=json.dumps({"request": base64_payload}).encode(),
                headers=headers
            )
            print("Sending PhonePe API req...", flush=True)
            with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
                print("PhonePe API success response received", flush=True)
                result = json.loads(response.read().decode())
                
                if result.get('success'):
                    url = result['data']['instrumentResponse']['redirectInfo']['url']
                    self.send_json_response(200, {'success': True, 'url': url})
                else:
                    self.send_json_response(400, {'error': 'Payment init failed', 'details': result})
        except Exception as e:
            print(f"Exception raised in PhonePe auth: {e}", flush=True)
            import traceback
            traceback.print_exc()
            msg = str(e)
            if hasattr(e, 'read'):
                try:
                    msg = e.read().decode()
                except:
                    pass
            self.send_json_response(500, {'error': 'Server error', 'message': msg})

    def handle_payment_callback(self):
        """Handle redirect back from PhonePe"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode()
        
        # We can just redirect the user to a success or failure page
        # The form data usually contains 'code', 'merchantId', 'transactionId'
        params = urllib.parse.parse_qs(post_data)
        code = params.get('code', [''])[0]
        
        # In a real app, you would verify the transaction status S2S here using the Status API
        
        if code == 'PAYMENT_SUCCESS':
            redirect_to = "/subscription.html?payment=success"
        else:
            redirect_to = "/subscription.html?payment=failure"
            
        self.send_response(302)
        self.send_header('Location', redirect_to)
        self.end_headers()
    
    def handle_github_user(self):
        """Get GitHub user info with access token"""
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        token = params.get('token', [None])[0]
        
        if not token:
            self.send_json_response(400, {'error': 'No token provided'})
            return
        
        try:
            user_req = urllib.request.Request(
                'https://api.github.com/user',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'PDF-Converter-Pro'
                }
            )
            
            with urllib.request.urlopen(user_req, context=ssl_context) as response:
                user_data = json.loads(response.read().decode())
            
            self.send_json_response(200, {'user': user_data})
            
        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def handle_download(self):
        """Serve a converted file from /tmp directory"""
        fname    = urllib.parse.unquote(self.path.split('/api/download/')[-1])
        tmp_path = os.path.join('/tmp', fname)

        if not os.path.exists(tmp_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')
            return

        # Detect MIME type
        ext_map = {
            'pdf':'application/pdf', 'docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pptx':'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'jpg':'image/jpeg', 'jpeg':'image/jpeg', 'png':'image/png',
        }
        ext  = fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
        mime = ext_map.get(ext, 'application/octet-stream')

        with open(tmp_path, 'rb') as f:
            data = f.read()

        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Content-Disposition', f'attachment; filename="{fname}"')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(data)

    def handle_conversion(self, tool_id):
        """Proxy request to ConvertAPI - Python 3.13+ compatible (no cgi module)"""
        print(f"Handling /api/convert/{tool_id}...", flush=True)
        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            self.send_json_response(400, {'error': 'Content-Type must be multipart/form-data'})
            return

        # Use dedicated Excel key for pdf-to-excel, otherwise use the general key
        if tool_id == 'pdf-to-excel':
            secret = os.environ.get('CONVERTAPI_EXCEL_SECRET', CONVERTAPI_EXCEL_SECRET)
        else:
            secret = os.environ.get('CONVERTAPI_SECRET', CONVERTAPI_SECRET)
        if not secret:
            self.send_json_response(500, {'error': 'ConvertAPI Secret is not configured on the server.'})
            return

        try:
            import requests

            # ── Read raw body ──────────────────────────────────────────
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length)

            # ── Extract boundary ───────────────────────────────────────
            boundary = None
            for part in content_type.split(';'):
                part = part.strip()
                if part.startswith('boundary='):
                    boundary = part[9:].strip().strip('"')
                    break

            if not boundary:
                self.send_json_response(400, {'error': 'Missing boundary in Content-Type'})
                return

            # ── Manual multipart parser ────────────────────────────────
            def parse_multipart(body, boundary):
                """Parse multipart/form-data body without cgi module."""
                results = []
                delimiter = ('--' + boundary).encode()
                end_delim  = ('--' + boundary + '--').encode()

                # Split by boundary
                parts = body.split(delimiter)
                for part in parts:
                    part = part.strip(b'\r\n')
                    if not part or part == b'--' or part == end_delim.lstrip(b'--' + boundary.encode()):
                        continue
                    if part.startswith(b'--'):   # end delimiter leftover
                        continue

                    # Split headers from content
                    if b'\r\n\r\n' in part:
                        header_block, content = part.split(b'\r\n\r\n', 1)
                    elif b'\n\n' in part:
                        header_block, content = part.split(b'\n\n', 1)
                    else:
                        continue

                    # Strip trailing CRLF from content
                    if content.endswith(b'\r\n'):
                        content = content[:-2]

                    # Parse headers
                    headers = {}
                    for line in header_block.decode('utf-8', errors='replace').splitlines():
                        if ':' in line:
                            k, v = line.split(':', 1)
                            headers[k.strip().lower()] = v.strip()

                    disp = headers.get('content-disposition', '')
                    name = None
                    filename = None
                    for token in disp.split(';'):
                        token = token.strip()
                        if token.startswith('name='):
                            name = token[5:].strip().strip('"')
                        elif token.startswith('filename='):
                            filename = token[9:].strip().strip('"')

                    mime = headers.get('content-type', 'application/octet-stream')
                    results.append({'name': name, 'filename': filename, 'mime': mime, 'data': content})

                return results

            parts = parse_multipart(raw_body, boundary)

            # ── Build files payload for requests ───────────────────────
            files_payload = []
            extra_params = {}
            idx = 0
            for p in parts:
                if p['name'] == 'files' and p['data']:
                    fname = p['filename'] or f'file{idx}.bin'
                    mime  = p['mime'] or 'application/octet-stream'
                    # Merge PDF uses Files[N], all others use 'File'
                    field = f'Files[{idx}]' if tool_id == 'merge-pdf' else 'File'
                    files_payload.append((field, (fname, p['data'], mime)))
                    idx += 1
                elif p['name'] and not p.get('filename'):
                    val = p['data'].decode('utf-8', errors='replace').strip()
                    if val:
                        extra_params[p['name']] = val

            if not files_payload:
                self.send_json_response(400, {'error': 'No files found in the upload.'})
                return

            # Validate required parameters for tools that need extra input.
            if tool_id == 'protect-pdf' and not (extra_params.get('UserPassword') or extra_params.get('OwnerPassword')):
                self.send_json_response(400, {
                    'error': 'Password is required for Protect PDF.',
                    'details': 'Send UserPassword or OwnerPassword as form-data.'
                })
                return

            if tool_id in ('edit-pdf', 'sign-pdf') and not extra_params.get('Text'):
                extra_params['Text'] = 'Signed via PDF2Pro' if tool_id == 'sign-pdf' else 'Edited via PDF2Pro'

            print(f"Sending {len(files_payload)} file(s) to ConvertAPI...", flush=True)

            # ── ConvertAPI endpoint map ────────────────────────────────
            # Office→PDF tools use dedicated OFFICE_API_KEY + 'office' source.
            # All other PDF tools use the standard CONVERTAPI_SECRET.
            OFFICE_TOOLS = {'word-to-pdf', 'excel-to-pdf', 'ppt-to-pdf', 'jpg-to-pdf'}

            api_map = {
                'pdf-to-word'  : 'https://v2.convertapi.com/convert/pdf/to/docx',
                'pdf-to-excel' : 'https://v2.convertapi.com/convert/pdf/to/xlsx',
                'pdf-to-ppt'   : 'https://v2.convertapi.com/convert/pdf/to/pptx',
                'pdf-to-jpg'   : 'https://v2.convertapi.com/convert/pdf/to/jpg',
                'pdf-to-png'   : 'https://v2.convertapi.com/convert/pdf/to/png',
                'word-to-pdf'  : 'https://v2.convertapi.com/convert/office/to/pdf',  # office key
                'excel-to-pdf' : 'https://v2.convertapi.com/convert/office/to/pdf',  # office key
                'ppt-to-pdf'   : 'https://v2.convertapi.com/convert/office/to/pdf',  # office key
                'jpg-to-pdf'   : 'https://v2.convertapi.com/convert/office/to/pdf',  # office key
                'merge-pdf'    : 'https://v2.convertapi.com/convert/pdf/to/merge',
                'split-pdf'    : 'https://v2.convertapi.com/convert/pdf/to/split',
                'compress-pdf' : 'https://v2.convertapi.com/convert/pdf/to/compress',
                'protect-pdf'  : 'https://v2.convertapi.com/convert/pdf/to/encrypt',
                'unlock-pdf'   : 'https://v2.convertapi.com/convert/pdf/to/decrypt',
                'edit-pdf'     : 'https://v2.convertapi.com/convert/pdf/to/watermark',
                'sign-pdf'     : 'https://v2.convertapi.com/convert/pdf/to/watermark',
            }

            base_url = api_map.get(tool_id)
            if not base_url:
                self.send_json_response(400, {'error': f'Tool "{tool_id}" is not supported yet.'})
                return

            # ── Send to ConvertAPI ─────────────────────────────────────
            url = f"{base_url}?Secret={secret}"
            print(f"[{tool_id}] → POST {base_url} | secret ends: ...{secret[-6:]} | files: {len(files_payload)}", flush=True)
            resp = requests.post(url, files=files_payload, data=extra_params, timeout=120)
            print(f"[{tool_id}] ConvertAPI HTTP {resp.status_code}", flush=True)

            # ── Parse ConvertAPI response ──────────────────────────────
            try:
                result = resp.json()
            except Exception:
                result = {}
            print(f"[{tool_id}] Raw response: {str(result)[:300]}", flush=True)

            # ConvertAPI returns HTTP 200 on success, 4xx/5xx on error.
            # Their error body looks like: {"Code": 5001, "Message": "..."}
            if resp.status_code == 200 and result.get('Files'):
                # ConvertAPI returns FileData (base64) instead of a URL
                # Save to /tmp and return a local download link
                processed_files = []
                host = self.headers.get('Host', f'localhost:{PORT}')
                forwarded_proto = (self.headers.get('X-Forwarded-Proto') or '').split(',')[0].strip()
                if forwarded_proto:
                    scheme = forwarded_proto
                elif self.headers.get('Origin', '').startswith('https://'):
                    scheme = 'https'
                else:
                    scheme = 'http'

                for file_info in result.get('Files', []):
                    fname    = file_info.get('FileName', 'converted_file')
                    filedata = file_info.get('FileData', '')
                    fileurl  = file_info.get('Url', '')

                    if filedata:
                        # Decode base64 and save to temp dir
                        try:
                            file_bytes = base64.b64decode(filedata)
                        except Exception as de:
                            print(f"[{tool_id}] base64 decode error: {de}", flush=True)
                            continue
                        tmp_path = os.path.join('/tmp', fname)
                        with open(tmp_path, 'wb') as outf:
                            outf.write(file_bytes)
                        safe_fname = urllib.parse.quote(fname)
                        local_url = f"{host}/api/download/{safe_fname}"
                        processed_files.append({
                            'FileName': fname,
                            'FileSize': len(file_bytes),
                            'Url': f"{scheme}://{local_url}"
                        })
                        print(f"[{tool_id}] Saved {fname} ({len(file_bytes)} bytes)", flush=True)
                    elif fileurl:
                        processed_files.append({
                            'FileName': fname,
                            'FileSize': file_info.get('FileSize', 0),
                            'Url': fileurl
                        })

                if not processed_files:
                    self.send_json_response(500, {
                        'error': 'ConvertAPI returned no output files.',
                        'details': str(result)[:500]
                    })
                    return

                self.send_json_response(200, {'success': True, 'data': {'Files': processed_files}})

            else:
                # Extract the most helpful error message from ConvertAPI
                api_code    = result.get('Code', resp.status_code)
                api_message = result.get('Message', resp.text[:300])
                # Make common errors human-readable
                friendly = {
                    5001: 'PDF has no tables to extract. Please upload a PDF that contains data tables.',
                    4005: 'Unsupported file format. Please upload a valid PDF file.',
                    4000: 'Invalid request. Please check the file and try again.',
                    4001: 'Invalid or expired API key. Please contact support.',
                    5000: 'Conversion timed out. Try with a smaller file.',
                }.get(api_code, api_message)
                print(f"[{tool_id}] ConvertAPI error code={api_code} msg={api_message}", flush=True)
                self.send_json_response(500, {
                    'error': friendly,
                    'details': f'ConvertAPI Code {api_code}: {api_message}'
                })

        except Exception as e:
            import traceback
            print(f"Conversion exception: {e}\n{traceback.format_exc()}", flush=True)
            self.send_json_response(500, {'error': 'Server error during conversion.', 'message': str(e)})




    def send_json_response(self, status_code, data):
        """Send a JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        """Custom log format"""
        try:
            sys.stderr.write(f"[Server] {format % args}\n")
        except:
            sys.stderr.write(f"[Server] {format}\n")


# =============================================
# Start Server
# =============================================
if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    handler = AuthHandler
    try:
        from http.server import ThreadingHTTPServer
        server = ThreadingHTTPServer(('', PORT), handler)
    except ImportError:
        server = http.server.HTTPServer(('', PORT), handler)
    
    print(f"""
╔══════════════════════════════════════════════╗
║     PDF Converter Pro - Dev Server           ║
╠══════════════════════════════════════════════╣
║                                              ║
║  🌐 Server running at:                       ║
║     http://localhost:{PORT}                    ║
║                                              ║
║  📄 Main Page:                               ║
║     http://localhost:{PORT}/index.html         ║
║                                              ║
║  🔐 Auth Page:                               ║
║     http://localhost:{PORT}/auth.html          ║
║                                              ║
║  🔑 GitHub OAuth: {'✅ Configured' if GITHUB_CLIENT_SECRET else '❌ Add CLIENT_SECRET in server.py'}    ║
║                                              ║
╚══════════════════════════════════════════════╝
    """)
    
    if not GITHUB_CLIENT_SECRET:
        print("⚠️  WARNING: GITHUB_CLIENT_SECRET is empty!")
        print("   Edit server.py and paste your GitHub Client Secret")
        print("   on line 19 to enable GitHub login.\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
        server.server_close()
