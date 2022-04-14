#!/bin/sh -l
echo "installing git"
apt install git

echo "Cloning destination git repository"
git config --global user.email "$INPUT_USER_EMAIL"
git config --global user.name "$INPUT_USER_NAME"

# clone grypi
git clone --single-branch --branch master "https://x-access-token:$API_TOKEN_GITHUB@github.com/ow-gryphon/grypi.git" "grypi"

# clone actions
git clone --single-branch --branch master "https://x-access-token:$API_TOKEN_GITHUB@github.com/ow-gryphon/update-grypy-action.git" "actions"

# clone the template repo
git clone --single-branch --branch master "https://x-access-token:$API_TOKEN_GITHUB@github.com/${GITHUB_REPOSITORY}.git" "template"

# run the python files
pip install beautifulsoup4
python ./actions/src/update_index_html.py
python ./actions/src/update_metadata_json.py

# send to index
#   clone destination repo (index)
git clone --single-branch --branch master "https://x-access-token:$API_TOKEN_GITHUB@github.com/ow-gryphon/grypi.git" "destination"

# copy the new files to index
cp "grypi/index.html" "destination/index.html"
cp "grypi/${GITHUB_REPOSITORY#*/}/index.html" "destination/${GITHUB_REPOSITORY#*/}/index.html"
cp "template/metadata.json" "destination/${GITHUB_REPOSITORY#*/}/metadata.json"

#   commit and push
# shellcheck disable=SC2164
cd "destination"
git add .
if git status | grep -q "Changes to be committed"
then
  git commit --message "Update from https://github.com/${GITHUB_REPOSITORY}/commit/${GITHUB_SHA}"
  echo "Pushing git commit"
  git push -u origin HEAD:master
else
  echo "No changes detected"
fi