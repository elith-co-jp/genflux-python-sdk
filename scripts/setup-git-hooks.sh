#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up git hooks...${NC}"

# Get the git root directory
GIT_ROOT=$(git rev-parse --show-toplevel)

# Check if .githooks directory exists
if [ ! -d "$GIT_ROOT/.githooks" ]; then
  echo -e "${RED}.githooks directory not found in the git root.${NC}"
  exit 1
fi

# Set the hooks path
git config core.hooksPath .githooks

# Make the hooks executable
chmod +x $GIT_ROOT/.githooks/*

echo -e "${GREEN}Git hooks set up successfully!${NC}"
echo -e "${YELLOW}The following hooks are now active:${NC}"
ls -la $GIT_ROOT/.githooks | grep -v "README.md" | grep -v "^d" | grep -v "total" | awk '{print $9}' 