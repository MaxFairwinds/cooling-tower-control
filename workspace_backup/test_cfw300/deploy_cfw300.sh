#!/bin/bash
# Deploy CFW300 test code to Raspberry Pi

HOST="coolingtower.local"
USER="max"
PASS="max123"
FILES="config_cfw300.py vfd_controller_cfw300.py test_suite.py interactive_test.py README_CFW300.md"

echo "Deploying CFW300 test code to $HOST..."
expect -c "
set timeout 60
spawn scp -o StrictHostKeyChecking=no $FILES $USER@$HOST:/home/$USER/test_cfw300/
expect {
  \"*password:*\" { send \"$PASS\r\"; exp_continue }
  eof
}
"

echo "Making scripts executable..."
expect -c "
spawn ssh $USER@$HOST \"chmod +x test_cfw300/*.py\"
expect {
  \"*password:*\" { send \"$PASS\r\"; exp_continue }
  eof
}
"

echo "CFW300 test code deployed successfully!"
echo ""
echo "To run tests on the Pi:"
echo "  ssh max@coolingtower.local"
echo "  cd test_cfw300"
echo "  source ../venv/bin/activate"
echo "  python3 test_suite.py          # Automated tests"
echo "  python3 interactive_test.py    # Manual control"
