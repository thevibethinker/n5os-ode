#!/bin/bash
set -e
cd /home/workspace/calcom
echo "Installing dependencies..."
yarn install 2>&1 | tee /dev/shm/yarn-install-full.log
echo "Running migrations..."
yarn workspace @calcom/prisma db-deploy
echo "Building..."
yarn build
echo "✓ Done!"
