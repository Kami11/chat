#!/bin/bash

PRODUCTION=146.148.12.163
PREPRODUCTION=104.199.46.184

#deploy to preproduction
ssh-keyscan -t rsa -H $PREPRODUCTION >> ~/.ssh/known_hosts
ssh -oStrictHostKeyChecking=no -i secret travis@$PREPRODUCTION << EOF
echo "hostname"
hostname

sudo rm -r chat/

echo "git clone https://github.com/Kami11/chat.git"
git clone https://github.com/Kami11/chat.git

cd chat/
pwd

echo "sudo -H ./setup.py install"
sudo -H  python3 setup.py install

echo "kisschat -a 0.0.0.0 -p 80"
kisschat -a 0.0.0.0 -p 80

EOF
