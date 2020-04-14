#!/usr/bin/env bash
#
# Generates "README.md" with last 3 years' latest top 50 movies
#
# Variables
DATE="$(date +%m/%d/%y)"

# Main Script
git remote remove origin
git remote add origin https://"${GH_REF}"
git fetch --all
echo ""
echo "Generating 'README.md' file"
echo ""
echo -e "# Top IMDB 50 Movies Data Scrapper\n" > README.md
echo -e "Top 50 Movies as of: **$(date +%m/%d/%Y)**\n" >> README.md
./IMDB.py >> README.md
echo "'README.md' file generated"
echo ""
if [[ -z $(git status --porcelain) ]]; then
    echo "Nothing to Update"
else
    echo "Adding Changes to 'README.md' file"
    echo ""
    git config user.email "49350241+crazyuploader@users.noreply.github.com"
    git config user.name "crazyuploader"
    git add .
    git commit -m "Travis CI ${DATE} [skip travis]"
    git push https://crazyuploader:"${GITHUB_TOKEN}"@"${GH_REF}" HEAD:"${TRAVIS_BRANCH}"
    echo ""
    echo "Changes pushed to 'https://github.com/crazyuploader/IMDB_TOP_50'"
fi
