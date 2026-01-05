#!/bin/bash
HOST="coolingtower.local"
USER="max"
PASS="max123"
FILES="vfd_controller.py sensor_manager.py main_control.py config.py pump_failover.py"

echo "Deploying code to $HOST..."
expect -c "
set timeout 60
spawn scp -o StrictHostKeyChecking=no $FILES $USER@$HOST:/home/$USER/
expect {
  \"*password:*\" { send \"$PASS\r\"; exp_continue }
  eof
}
"
