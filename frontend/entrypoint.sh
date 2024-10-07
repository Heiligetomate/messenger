#!/bin/sh

echo "window.env = {" > /usr/share/nginx/html/env.js
echo "  SERVICE_URL: \"${SERVICE_URL}\"" >> /usr/share/nginx/html/env.js
echo "};" >> /usr/share/nginx/html/env.js

nginx -g 'daemon off;'
