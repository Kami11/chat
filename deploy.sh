#!/bin/bash

PRODUCTION=146.148.12.163
PREPRODUCTION=104.199.46.184

#############################
## deploy to preproduction ##
#############################
ssh-keyscan -t rsa -H $PREPRODUCTION >> ~/.ssh/known_hosts
ssh -oStrictHostKeyChecking=no -i secret travis@$PREPRODUCTION << EOF
echo "***** hostname"
hostname

echo "***** sudo rm -r chat/"
sudo rm -r chat/

echo "\n***** git clone https://github.com/Kami11/chat.git"
git clone https://github.com/Kami11/chat.git

cd chat/
pwd

echo "\n***** sudo -H ./setup.py install"
sudo -H  python3 setup.py install

echo "\n***** sudo killall python3"
sudo killall python3
EOF
ssh -i  secret -t travis@$PREPRODUCTION 'sudo kisschat -a 0.0.0.0 -p 80' &

#############################
##  deploy to production   ##
#############################
