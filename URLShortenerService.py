import http.server
import requests
from urllib.parse import quote, parse_qs, urlparse

url_dictionary = {}

form = '''<!DOCTYPE html>
<title>URL Shortener Service</title>
<form method="POST">
    <label>Long URI:
        <input name="longuri">
    </label>
    <br>
    <label>Short name:
        <input name="shorturi">
    </label>
    <br>
    <button type="submit">Submit</button>
</form>
<p>Shortened URIs:
<pre>
{}
</pre>
'''

class Shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        short_url = self.path[1:] # Removing the prefixed '/'

        if short_url: # Non-empty short url
            if short_url in url_dictionary: # short url in url_dictionary, redirect to associated long url
                self.send_response(303)
                self.send_header('Location', url_dictionary[short_url])
                self.end_headers()
            else: # short url not in url_dictionary, respond with error 
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("Short URI '{}' not found.".format(short_url).encode())

        else: # Empty short url, send the form for entering urls and show url_dictionary
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            serialised_url_dictionary = ["{} : {}".format(key, url_dictionary[key]) for key in sorted(url_dictionary.keys())]
            self.wfile.write(form.format(serialised_url_dictionary).encode())

    def do_POST(self): 
        request_length = int(self.headers.get('Content-length', 0))
        request_body = self.rfile.read(request_length).decode()
        params = parse_qs(request_body)
        long_url = params.get('longuri', 0)
        short_url = params.get('shorturi', 0)

        if long_url == 0 or short_url == 0: # Invalid form input, return error
            self.send_response(400)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("Please enter both long and short URIs!".encode())

        # Long URI in the form is invalid (does not meet the URI syntax), return error
        elif (urlparse(long_url[0]).scheme == '') or (urlparse(long_url[0]).netloc == ''):
            self.send_response(400)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("The long URI {} is invalid (invalid syntax)".format(long_url[0]).encode())            

        # Long URI in the form is invalid (returns a non-200 status code), return error
        elif (requests.get(long_url[0], timeout=5).status_code != 200): 
            self.send_response(400)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("The long URI {} is invalid (returns a non-200 status code)".format(long_url[0]).encode())

        else: # Valid entry made into url_dictionary, redirect to root path (PRG pattern)
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers() 
            url_dictionary[quote(short_url[0])] = long_url[0] # Quote before saving so it can be used as a short url

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, Shortener)
    httpd.serve_forever()
