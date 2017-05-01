#!/bin/bash

PRODUCTION=146.148.12.163
PREPRODUCTION=104.199.46.184

#deploy to preproduction
ssh-keyscan -t rsa -H $PREPRODUCTION >> ~/.ssh/known_hosts
ssh -oStrictHostKeyChecking=no -i secret travis@$PREPRODUCTION << EOF

hostname
rm -r chat/
git clone https://github.com/Kami11/chat.git
cd chat/
sudo -H ./setup.py install
kisschat -a 0.0.0.0 -p 80

EOF
