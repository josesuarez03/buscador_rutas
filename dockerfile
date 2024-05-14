# Stage 1: Compilación de dirb
FROM alpine:3.19.1 AS dirb-builder

RUN apk add --no-cache gcc make curl-dev musl-dev libcurl

RUN mkdir /build && cd /build

RUN wget -q https://downloads.sourceforge.net/project/dirb/dirb/2.22/dirb222.tar.gz -O - | tar -xz --strip-components=1 -f -

RUN chmod -R a+x wordlists configure

RUN ./configure CFLAGS="-O2 -g -fcommon"

RUN make && make install

RUN mkdir -p /usr/share/dirb && cp -aR wordlists /usr/share/dirb

RUN cd / && apk del --no-cache gcc make curl-dev musl-dev && rm -rf /build

RUN install -d -m 0700 -o nobody -g nobody /.cache

# Stage 2: Aplicación Python
FROM python:3.12.1-alpine

RUN pip install Flask pymongo requests

# Copiar el ejecutable de dirb
COPY --from=dirb-builder /usr/local/bin/dirb /usr/local/bin/dirb

WORKDIR /app

COPY . /app

EXPOSE 5000

CMD ["python", "app.py"]

