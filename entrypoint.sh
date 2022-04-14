echo "Cloning destination git repository"
git config --global user.email "$INPUT_USER_EMAIL"
git config --global user.name "$INPUT_USER_NAME"

# clone grypi
git clone --single-branch --branch master "https://x-access-token:$API_TOKEN_GITHUB@ow-gryphon/grypi.git" "grypi"

# clone the template repo
git clone --single-branch --branch master "https://x-access-token:$API_TOKEN_GITHUB@$INPUT_GITHUB_REPOSITORY.git" "template"

# run the python files
pip install beautifulsoup4
python src/update_index_html.py
python src/update_metadata_json.py

# send to index
#   clone destination repo (index)
git clone --single-branch --branch master "https://x-access-token:$API_TOKEN_GITHUB@ow-gryphon/grypi.git" "destination"

# copy the new files to index
cp "grypi/index.html" "destination/index.html"
cp "grypi/$INPUT_GITHUB_REPOSITORY/index.html" "destination/$INPUT_GITHUB_REPOSITORY/index.html"
cp "template/metadata.json" "destination/$INPUT_GITHUB_REPOSITORY/metadata.json"

#   commit and push
# shellcheck disable=SC2164
cd "destination"
git add .
if git status | grep -q "Changes to be committed"
then
  git commit --message "Update from https://github.com/${INPUT_GITHUB_REPOSITORY}/commit/${GITHUB_SHA}"
  echo "Pushing git commit"
  git push -u origin HEAD:master
else
  echo "No changes detected"
fi