#!/usr/bin/env bash
#
# Generates "README.md" with IMDb top 50 movies
#
# Variables
DATE="$(date +%m/%d/%y)"
GH_REF="github.com/crazyuploader/IMDb_Top_50.git"

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
# echo -e "# Top IMDb 50 Movies Data Scrapper\n" > README.md
# echo -e "Top 50 Movies as of: **$(date +%m/%d/%Y)**\n" >> README.md
./IMDb.py 1> /dev/null
ERROR_CODE="$?"
if [[ "${ERROR_CODE}" != "0" ]]; then
    echo -e "${RED}Python program failed${NC}"
    echo -e "${RED}Exiting...${NC}"
    exit 1
fi
echo -e "${GREEN}'README.md' file generated${NC}"
echo ""
echo -e "${GREEN}'Data/data.json' file generated${NC}"
echo ""
cd Data/T50 || exit 1
csvtojson data.csv > data.json
echo ""
cd ..
cd T250 || exit 1
csvtojson data.csv > data.json
echo ""
cd "${GITHUB_WORKSPACE}" || exit 1
echo "Prettify..."
prettier --write .
if [[ -z $(git status --porcelain) ]]; then
    echo -e "${GREEN}Nothing to Update${NC}"
else
    echo -e "${YELLOW}File(s) changed -${NC}"
    git diff --name-only
    git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
    git config user.name "github-actions"
    git add .
    git commit -m "CI ${DATE} [skip ci]"
    git push https://crazyuploader:"${GITHUB_TOKEN}"@"${GH_REF}" HEAD:"${GITHUB_REF}"
    echo -e "${YELLOW}Changes pushed to${NC} ${GREEN}'https://github.com/crazyuploader/IMDb_Top_50'${NC}"
fi
