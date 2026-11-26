# Partimos de Python 3.12 para ejecutar las actividades y el proyecto final.
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Retiramos la fuente heredada de Yarn y aseguramos pip para instalar dependencias.
RUN rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn*.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/*
