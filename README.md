mdwiki-pyng
===========

Small Python / AngularJS powered Markdown wiki

## Python dependencies
- [Flask](http://flask.pocoo.org/) web framework ```~# pip install flask```
- [Misaka](http://misaka.61924.nl/) Markdown parser ```~# pip install misaka```
- [Pygments](http://pygments.org/) syntax highlighter ```~# pip install pygments```

## Webserver configuration
Sample nginx configuration with uWSGI upstream server. If a file is found in the *public* directory it sould be served, otherwise the request should be passed upstream.
```nginx
server {
    listen 80;
    server_name hostname.tld;
    root /path/to/document_root;
    error_log /var/log/nginx/mdwiki-error.log;
    access_log /var/log/nginx/mdwiki-access.log;

    location / {
        try_files /public$uri /public$uri/index.html @mdwiki;
    }

    location @mdwiki {
        include /etc/nginx/uwsgi_params;
        uwsgi_param UWSGI_MODULE mdwiki;
        uwsgi_param UWSGI_CALLABLE "app";
        uwsgi_param UWSGI_PYHOME $document_root;
        uwsgi_param UWSGI_CHDIR $document_root;
        uwsgi_modifier1 30;
        uwsgi_pass 127.0.0.1:9001;
    }
}
```
