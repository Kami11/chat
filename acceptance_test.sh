#!/bin/sh

# The acceptance tests for kisschat

# Test a WebSocket using curl.
curl --include \
--no-buffer \
--header "Connection: Upgrade" \
--header "Upgrade: websocket" \
--header "Host: $1" \
--header "Origin: http://$1" \
--header "Sec-WebSocket-Key: WyY0MFyJCeTSmEhThCHLuQ==" \
--header "Sec-WebSocket-Version: 13" \
http://$1/ 2> acceptance_test_err 1> acceptance_test_result

if grep '200 OK' acceptance_test_result > /dev/null
then
	rm acceptance_test_result
	rm acceptance_test_err
	echo 'The acceptance tests is successful'
	exit 0

else 
	echo 'The acceptance tests is failed, WebSocket did not work ' 
	exit 1 
fi
