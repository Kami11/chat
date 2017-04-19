#!/bin/sh
# 
# Start with script befor first commit
ln -s -f ../../hooks/pre-commit ../.git/hooks/pre-commit
echo "symbolic link is created"
