#!/bin/sh
# Gera os JSON e monta o plugin fcstudio-setup.zip
cd "$(dirname "$0")" && python3 gerar.py && rm -rf fcstudio-setup/paginas && cp -r paginas fcstudio-setup/ && cp kit-settings.json fcstudio-setup/ && rm -f fcstudio-setup.zip && zip -qr fcstudio-setup.zip fcstudio-setup && echo zip ok
