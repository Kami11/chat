#!/bin/sh
# 
# Start with script befor first commit
ln -s -f ../../hooks/pre-commit ../.git/hooks/pre-commit
ln -s -f ../../hooks/post-push ../.git/hooks/post-push
echo "symbolic link is created"
