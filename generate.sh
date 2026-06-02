#!/usr/bin/env bash
#
# Generates IMDb data JSON files and README.md
#

NC="\033[0m"
RED="\033[0;31m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"

PYTHONUNBUFFERED=1 ./IMDb.py
ERROR_CODE="$?"
if [[ "${ERROR_CODE}" != "0" ]]; then
	echo -e "${RED}Running Python IMDb.py Program Failed.${NC}"
	echo -e "${RED}Exiting...${NC}"
	exit 1
fi

echo -e "${GREEN}Data files generated.${NC}"
echo ""
if [[ -z $(git status --porcelain) ]]; then
	echo -e "${GREEN}Nothing to Update${NC}"
else
	echo -e "${YELLOW}File(s) changed -${NC}"
	git diff --name-only
fi
