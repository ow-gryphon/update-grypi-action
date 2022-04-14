FROM python:3.9.12-alpine3.15

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]