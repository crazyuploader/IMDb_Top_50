#!/usr/bin/env bash
#
# Generates "README.md" with IMDb top 50 movies
#

# Colors
NC="\033[0m"
RED="\033[0;31m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"

# Main Script
./IMDb.py 1>/dev/null
ERROR_CODE="$?"
if [[ "${ERROR_CODE}" != "0" ]]; then
	echo -e "${RED}Running Python IMDb.py Program Failed.${NC}"
	echo -e "${RED}Exiting...${NC}"
	exit 1
fi
echo -e "${GREEN}'README.md' file generated.${NC}"
echo ""
echo -e "${GREEN}JSON file(s) are being generated.${NC}"
echo ""
cd data/top50 || exit 1
csvtojson movies.csv >movies.json
csvtojson shows.csv >shows.json
echo ""
cd "${GITHUB_WORKSPACE}" || exit 1
cd ../top250 || exit 1
csvtojson movies.csv >movies.json
csvtojson shows.csv >shows.json
echo ""
echo -e "${GREEN}README.md and JSON file(s) are ready for committing.${NC}"
echo ""
if [[ -z $(git status --porcelain) ]]; then
	echo -e "${GREEN}Nothing to Update${NC}"
else
	echo -e "${YELLOW}File(s) changed -${NC}"
	git diff --name-only
fi
