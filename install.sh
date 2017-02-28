#!/usr/bin/env bash

echo "Cloning fusepy (to allow the email to be mounted)"
git clone https://github.com/terencehonles/fusepy.git

echo "#init" > fusepy/__init__.py

echo "Maybe run?"
echo "mkdir mnt"
echo "python fuse.py mnt"
