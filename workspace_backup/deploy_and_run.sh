#!/bin/bash
HOST="coolingtower.local"
USER="max"
PASS="max123"
SCRIPT="remote_setup.sh"

echo "Deploying $SCRIPT to $HOST..."
expect -c "
set timeout 60
spawn scp -o StrictHostKeyChecking=no $SCRIPT $USER@$HOST:/home/$USER/
expect {
  \"*password:*\" { send \"$PASS\r\"; exp_continue }
  eof
}
"

echo "Running $SCRIPT on $HOST..."
expect -c "
set timeout 300
spawn ssh -o StrictHostKeyChecking=no $USER@$HOST \"chmod +x $SCRIPT && ./$SCRIPT\"
expect {
  \"*password:*\" { send \"$PASS\r\"; exp_continue }
  eof
}
"
