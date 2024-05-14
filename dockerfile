#Dirb

FROM alpine:3.19.1 AS dirb-builder

RUN apk add --no-cache gcc make curl-dev musl-dev libcurl

RUN mkdir /build && cd /build && \
    wget -q https://downloads.sourceforge.net/project/dirb/dirb/2.22/dirb222.tar.gz -O - | tar -xz --strip-components=1 -C /build && \
    chmod -R a+x wordlists configure && \
    ./configure CFLAGS="-O2 -g -fcommon" && \
    make && make install && \
    mkdir -p /usr/share/dirb && cp -aR wordlists /usr/share/dirb && \
    cd / && apk del --no-cache gcc make curl-dev musl-dev && rm -rf /build

RUN install -d -m 0700 -o nobody -g nobody /.cache

#Python

FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el ejecutable de dirb
COPY --from=dirb-builder /usr/local/bin/dirb /usr/local/bin/
COPY --from=dirb-builder /usr/share/dirb /usr/share/dirb


CMD ["python", "app.py"]