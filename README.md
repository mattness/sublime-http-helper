sublime-http-helper
===================

[Sublime Text 2](http://www.sublimetext.com/2) plugin to facilitate testing
of HTTP APIs using raw HTTP.  This is particularly handy when working with JSON
APIs that return large data sets, as sublime has built-in features that make
the JSON more readable.

sublime-http-helper is under the MIT license.

Project url:  https://github.com/mattness/sublime-http-helper

Installation
------------
Drop the files in a package directory of your choice in your sublime packages directory.

If you do a git clone, that would be (in the Packages dir):
`$ git clone https://github.com/mattness/sublime-http-helper.git HttpHelper`

Usage
-----
Open a new file in sublime and paste your raw HTTP request into it.
Wikipedia has a good [example](http://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Example_session):

```
GET /index.html HTTP/1.1
Host: www.example.com


```

Open sublime's console window (`` Ctrl + ` ``), and enter
`view.run_command('http_helper')`. HttpHelper will open a socket to the
host specified in the `Host:` header on port 80 and send the request.  When the
response is received, HttpHelper will open a new window containing the
response body.

You can add the http_helper command to your `*.sublime-keymap` file(s) with the following:

```
{
	"keys": ["ctrl+alt+h"], "command": "http_helper"
}
```

Be sure to choose a keybinding that is convenient and does not interfere with anything
else.