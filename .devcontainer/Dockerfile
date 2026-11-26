# Partimos de Python 3.12 para ejecutar las actividades y el proyecto final.
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Retiramos la fuente heredada de Yarn cuya firma GPG ya no es válida.
RUN rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn*.list
