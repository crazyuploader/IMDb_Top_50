#!/usr/bin/env bash
#
# Generates "README.md" with last year's latest top 50 movies
#
# Variables
DATE="$(date +%m/%d/%y)"

# Colors
NC="\033[0m"
RED="\033[0;31m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"

# Main Script
git remote remove origin
git remote add origin https://"${GH_REF}"
git fetch --all
echo ""
# echo -e "# Top IMDB 50 Movies Data Scrapper\n" > README.md
# echo -e "Top 50 Movies as of: **$(date +%m/%d/%Y)**\n" >> README.md
./IMDB.py 1> /dev/null
ERROR_CODE="$?"
if [[ "${ERROR_CODE}" != "0" ]]; then
    echo -e "${RED}Python program failed${NC}"
    echo -e "${RED}Exiting...${NC}"
    exit 1
fi
echo -e "${GREEN}'README.md' file generated${NC}"
echo ""
if [[ -z $(git status --porcelain) ]]; then
    echo -e "${GREEN}Nothing to Update${NC}"
else
    echo -e "${YELLOW}Adding Changes to 'README.md' file${NC}"
    echo ""
    git config user.email "49350241+crazyuploader@users.noreply.github.com"
    git config user.name "crazyuploader"
    git add .
    git commit -m "Travis CI ${DATE} [skip travis]"
    git push https://crazyuploader:"${GITHUB_TOKEN}"@"${GH_REF}" HEAD:"${TRAVIS_BRANCH}"
    echo ""
    echo -e "${YELLOW}Changes pushed to${NC} ${GREEN}'https://github.com/crazyuploader/IMDB_TOP_50'${NC}"
fi
echo ""
echo ""
echo -e "${YELLOW}------O-U-T-P-U-T------"
echo ""
csvtomd Data/data.csv
echo ""
