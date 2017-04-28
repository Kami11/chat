#!/bin/bash

ssh-keyscan -t rsa -H 104.199.24.157 >> ~/.ssh/known_hosts
ssh -oStrictHostKeyChecking=no -i dd travis@104.199.24.157 << EOF

pwd
ls -a

echo "I'm inside Google. Here you can run chef or deploy"

EOF
