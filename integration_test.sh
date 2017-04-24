#!/bin/sh

# The integration tests for kisschat

# Test a WebSocket using curl.

# This line for travis-CI
sudo cp example/kisschat.yml /etc/kisschat.yml

kisschat -a 0.0.0.0 &
sleep 3
curl --include \
--no-buffer \
--header "Connection: Upgrade" \
--header "Upgrade: websocket" \
--header "Host: 127.0.0.1:8888" \
--header "Origin: http://127.0.0.1:8888" \
--header "Sec-WebSocket-Key: sFZC1ndEpSVSx5ijYERYfw==" \
--header "Sec-WebSocket-Version: 13" \
http://127.0.0.1:8888/ 2> /dev/null 1> integration_test_result

if grep '200 OK' integration_test_result > /dev/null
then
	rm integration_test_result
	# Test a database using ping.
	if  ping -c1 35.187.56.13 > /dev/null
	then
		echo 'integration tests is successful'
		exit 0
	else 
 		echo 'The integration tests is failed, database is note conected' 
		exit 1
	fi
else 
	echo 'The integration tests is failed, WebSocket did not work ' 
	exit 1 
fi
