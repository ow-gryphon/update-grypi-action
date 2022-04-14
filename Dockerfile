FROM python:3.9.12-alpine3.15

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh \

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]