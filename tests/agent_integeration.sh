#!/bin/bash

# Load env vars from .env
set -a
source .env
set +a

# Check required env vars
if [ -z "$PATH_TO_VM_PEM" ]; then
  echo "VM key not loaded"
  exit 1
else
  echo "VM key loaded"
fi

if [ -z "$VM_ADDR" ]; then
  echo "VM address not loaded"
  exit 2
else
  echo "VM address loaded"
fi

if [ -z "$EXCEL_FILE_PATH" ]; then
  echo "Excel file path not loaded"
  exit 3
else
  echo "Excel file path loaded"
fi

# Start Docker if needed
if ! systemctl is-active --quiet docker; then
  echo "Starting Docker daemon..."
  sudo systemctl start docker || { echo "Failed to start Docker daemon"; exit 10; }
fi

# Navigate to project directory
cd ../docker || { echo "Project directory not found"; exit 11; }

# Start containers
docker-compose up -d || { echo "Failed to start containers"; exit 12; }

# Define tests array
tests=(
  "Log a transaction of fifty dollars at rate of 0.212 reference id 2224 for today to EXCEL_FILE_PATH:$EXCEL_FILE_PATH"
  "Append transaction id 3421, amount of 100 USD at rate 0.921, transaction was yesterday $EXCEL_FILE_PATH"
  "Delete transaction 2224"
  "Delete 3421"
  "Add a transaction of 100 AED at rate 3.67 id 201 for 02/10/2024 at $EXCEL_FILE_PATH"
)

# Run tests
for i in "${!tests[@]}"; do
  echo "Executing test $((i+1))"
  curl -X POST http://localhost:5005/your_endpoint \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"${tests[i]}\"}"
done
if [ -s "$EXCEL_FILE_PATH" ]; then
  echo "Tests passed"
else
  echo "Tests failed"
  exit 14
fi
exit 0