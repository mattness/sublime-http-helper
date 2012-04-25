import sublime, sublime_plugin
import socket, re, json

from http_parser.http import HttpStream
from http_parser.reader import StringReader
from http_parser.pyparser import HttpParser

class HttpHelperCommand(sublime_plugin.TextCommand):
	def _output(self, content, content_type="text/plain"):
		# Determine response content-type, and set syntax if we can
		ct = content_type.lower().split(';')[0]
		xml_formats = [ "text/xml", \
		"application/atom+xml", \
		"application/rss+xml", \
		"application/soap+xml" ]

		js_formats = [ "text/javascript", \
		"application/javascript", \
		"application/x-javascript"]

		if ct == "text/html" or ct == "application/xhtml+xml":
			syntax = "Packages/HTML/HTML.tmLanguage"
		elif ct == "application/json":
			syntax = "Packages/JavaScript/JSON.tmLanguage"
			obj = json.loads(content)
			content = json.dumps(obj, sort_keys=True, indent=2)
		elif ct == "text/css":
			syntax = "Packages/CSS/CSS.tmLanguage"
		elif ct in js_formats:
			syntax = "Packages/JavaScript/JavaScript.tmLanguage"
		elif ct in xml_formats:
			syntax = "Packages/XML/XML.tmLanguage"
		else:
			syntax = "Packages/Text/Plain text.tmLanguage"

		# Put the response into a new window
		scratch_window = self.view.window() or sublime.active_window()
		scratch_file = scratch_window.new_file()
		scratch_file.set_scratch(True)
		if syntax is not None:
			scratch_file.set_syntax_file(syntax)
		edit = scratch_file.begin_edit()
		scratch_file.insert(edit, 0, content)
		scratch_file.end_edit(edit)
		scratch_file.set_read_only(True)

	def run(self, edit):
		# Capture the request
		content = self.view.substr(sublime.Region(0, self.view.size()))

		# Make sure it has CRLF, as required by the HTTP spec
		content = re.sub("(?<!\x0D)\x0A", "\x0D\x0A", content)
		
		# Parse the request for the Host: header
		request_len = len(content)
		request_parser = HttpParser()
		request_parser.execute(content, request_len)
		request_headers = request_parser.get_headers()
		host = request_headers.get('host')
		
		if host is None:
			self._output('No Host header specified!  A Host header is required')
			return

		# If POST-ing or PUT-ing, check for Content-Length
		method = request_parser.get_method().upper()
		if method == 'POST' or method == 'PUT':
			if request_headers.get('content-length') is None:
				msg = 'No content-length header specified. Suggested length: %d'
				self._output(msg % len(request_parser.recv_body()))
				return

		# Open a socket to the server and send the content
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		response_body = []
		try:
			s.connect((host, 80))
			s.send(content)
			p = HttpParser()

			# Capture the response
			while True:
				data = s.recv(1024)
				if not data:
					break

				recved = len(data)
				p.execute(data, recved)

				if p.is_partial_body():
					response_body.append(p.recv_body())

				if p.is_message_complete():
					break

		finally:
			s.close()

		content_type = p.get_headers().get('content-type', "").lower()
		self._output("".join(response_body), content_type)
