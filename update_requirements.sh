#!/bin/sh

packages=$(cat requirements.txt | cut -d '=' -f 1)

. ./venv/bin/activate

for package in $packages
do
    pip install --upgrade $package
done

pip freeze > requirements.txt