FROM nginx:alpine

COPY infra/nginx/nginx.prod.conf /etc/nginx/nginx.conf
COPY infra/nginx/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
