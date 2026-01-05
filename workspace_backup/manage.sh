#!/bin/bash
# Helper script to manage the cooling tower control system

HOST="coolingtower.local"
USER="max"
PASS="max123"

case "$1" in
  deploy)
    echo "Deploying code to $HOST..."
    expect -c "
    spawn scp -o StrictHostKeyChecking=no vfd_controller.py sensor_manager.py main_control.py $USER@$HOST:/home/$USER/
    expect {
      \"*password:*\" { send \"$PASS\r\"; exp_continue }
      eof
    }
    "
    ;;
  
  run)
    echo "Running control system on $HOST..."
    expect -c "
    spawn ssh $USER@$HOST \"source venv/bin/activate && python3 main_control.py\"
    expect {
      \"*password:*\" { send \"$PASS\r\"; exp_continue }
      eof
    }
    "
    ;;
  
  test)
    echo "Running 10-second test on $HOST..."
    expect -c "
    set timeout 20
    spawn ssh $USER@$HOST \"source venv/bin/activate && timeout 10s python3 main_control.py\"
    expect {
      \"*password:*\" { send \"$PASS\r\"; exp_continue }
      eof
    }
    "
    ;;
  
  logs)
    echo "Fetching logs from $HOST..."
    expect -c "
    spawn ssh $USER@$HOST \"cat system.log\"
    expect {
      \"*password:*\" { send \"$PASS\r\"; exp_continue }
      eof
    }
    "
    ;;
  
  shell)
    echo "Opening SSH shell to $HOST..."
    expect -c "
    spawn ssh $USER@$HOST
    expect {
      \"*password:*\" { send \"$PASS\r\"; interact }
    }
    "
    ;;
  
  *)
    echo "RaspCoolingTower Management Script"
    echo ""
    echo "Usage: $0 {deploy|run|test|logs|shell}"
    echo ""
    echo "  deploy  - Deploy code to Raspberry Pi"
    echo "  run     - Run control system (interactive)"
    echo "  test    - Run 10-second test"
    echo "  logs    - View system logs"
    echo "  shell   - Open SSH shell"
    exit 1
    ;;
esac
