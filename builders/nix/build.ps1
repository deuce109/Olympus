#!/bin/sh

pip install -r requirements.txt

pip install PyInstaller

python -m PyInstaller --noconfirm /app/olympus.py