# Stage 1: Build dirb
FROM alpine:3.19.1 AS dirb-builder

# Instalar paquetes necesarios para la compilación
RUN apk add --no-cache gcc make curl-dev musl-dev libcurl wget

# Descargar y compilar dirb
RUN mkdir /build && cd /build && \
    wget -q https://downloads.sourceforge.net/project/dirb/dirb/2.22/dirb222.tar.gz -O - | tar -xz --strip-components=1 && \
    chmod -R a+x wordlists configure && \
    ./configure CFLAGS="-O2 -g -fcommon" && \
    make && \
    make install && \
    mkdir -p /usr/share/dirb && \
    cp -aR wordlists /usr/share/dirb

# Eliminar paquetes no necesarios después de la compilación
RUN apk del --no-cache gcc make curl-dev musl-dev && \
    rm -rf /build

# Stage 2: Setup Python environment
FROM python:3.9-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar aplicación
COPY . /app

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el ejecutable de dirb y los wordlists del builder stage
COPY --from=dirb-builder /usr/local/bin/dirb /usr/local/bin/dirb
COPY --from=dirb-builder /usr/share/dirb /usr/share/dirb

# Configurar un directorio para el cache para usuarios sin privilegios
RUN mkdir /.cache && \
    chown nobody:nogroup /.cache && \
    chmod 0700 /.cache

# Correr como usuario nobody
USER nobody

# Comando por defecto
CMD ["python", "app.py"]