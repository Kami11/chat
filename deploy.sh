#!/bin/bash

PRODUCTION=104.199.24.157
PREPRODUCTION=104.199.24.157

#deploy to prep
ssh-keyscan -t rsa -H $PRODUCTION >> ~/.ssh/known_hosts
ssh -oStrictHostKeyChecking=no -i secret travis@$PRODUCTION << EOF

pwd
ls -a
hostname
echo "I'm inside Google. Here you can run chef or deploy"

EOF
