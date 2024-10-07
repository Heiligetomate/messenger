FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf

COPY src /usr/share/nginx/html

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
