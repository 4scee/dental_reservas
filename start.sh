#!/bin/bash

# Salir si hay algún error
set -e

# Instalar dependencias usando pip3
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Ejecutar la app Flask en el puerto asignado por Railway
python3 app.py
