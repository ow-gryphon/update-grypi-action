import json
import os
import re
from pathlib import Path

VERSION_PATTERN = re.compile(
    "^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    "(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


TEMPLATE_FOLDER = Path("template")

# check template minimal structure

try:
    assert (TEMPLATE_FOLDER / "gryphon_requirements.txt").is_file()
    requirements_file = TEMPLATE_FOLDER / "gryphon_requirements.txt"
except:
    assert (TEMPLATE_FOLDER / "requirements.txt").is_file()
    requirements_file = TEMPLATE_FOLDER / "requirements.txt"

assert (TEMPLATE_FOLDER / "setup.py").is_file()
assert (TEMPLATE_FOLDER / "metadata.json").is_file()
assert (TEMPLATE_FOLDER / "README.md").is_file()

assert (TEMPLATE_FOLDER / "template").is_dir()


with open(TEMPLATE_FOLDER / "metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# check mandatory fields
required_fields = ["command", "display_name"]
faulting_fields = []
for field in required_fields:
    if field not in metadata:
        faulting_fields.append(field)


if len(faulting_fields):
    raise AttributeError(f"Some required fields are not present in the metadata.json file: {faulting_fields}")


# check field formats
assert type(metadata["command"]) == str


if "dependencies" in metadata:
    assert type(metadata["dependencies"]) == list

if "topic" in metadata:
    assert type(metadata["topic"]) == list

if "methodology" in metadata:
    assert type(metadata["methodology"]) == list

if "keywords" in metadata:
    assert type(metadata["keywords"]) == list


# check possible values of command field
assert metadata["command"] in ["init", "generate"]


def clear_data(raw_str):
    _data = list(filter(lambda x: len(x.strip()), raw_str.split("'")))[0].strip()
    return list(filter(lambda x: len(x.strip()), _data.split("\"")))[0].strip()


context = json.loads(os.environ["GITHUB_CONTEXT"])
repo_name = context["repository"].split("/")[-1]
tag_name = context["event"]["ref"].split("/")[-1]


def execute_command(command) -> tuple:
    from subprocess import PIPE, Popen

    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return stderr.decode(), stdout.decode()


    with open(requirements_file, "r", encoding="utf-8") as f:
        contents = f.read()
        libraries = contents.strip().split("\n")
        for lib_name in libraries:
            if not len(lib_name):
                continue

            lib_name = lib_name.strip().split('>=')[0].split('<')[0].split('==')[0]
            pip_command = f"pip index versions {lib_name} --index-url https://ow-gryphon.github.io/grypi/"

            error_out, std_out = execute_command(pip_command)

            assert "Available versions" in std_out, f"Required template \"{lib_name}\" was not found on GryPi index."
            assert "ERROR" not in error_out, f"Required template \"{lib_name}\" was not found on GryPi index."


with open(TEMPLATE_FOLDER / "setup.py", "r", encoding="UTF-8") as f:
    raw_text = f.read()
    version = clear_data(raw_text.split("version=")[1].strip().split(',')[0].strip())
    name = clear_data(raw_text.split("name=")[1].strip().split(',')[0].strip())
    # TODO: Make this logic a bit more robust

try:
    # check if repository name is equal to the package name on setup.py
    assert repo_name == name, f"Repo name \"{repo_name}\" doesn't match the package name \"{name}\" from setup.py"

    # check if version on setup.py is equal to tag
    assert tag_name == version, f"Tag name \"{tag_name}\" doesn't match the version \"{version}\" from setup.py"

    # check if version is in the right format
    assert VERSION_PATTERN.match(version), f"Version on setup.py \"{tag_name}\" is not in the format 0.0.0 (X.X.X)"
    assert VERSION_PATTERN.match(tag_name), f"Tag name \"{tag_name}\" is not in the format 0.0.0 (X.X.X)"

except Exception as e:
    if VERSION_PATTERN.match(tag_name) and tag_name != version:
        # delete tag
        os.system(f"cd {TEMPLATE_FOLDER} && git tag -d {tag_name} && git push --tags")
        os.system(f"cd {TEMPLATE_FOLDER} && git push --delete origin {tag_name}")

        print(f"Use the command: \"git tag -d {tag_name}\" to remove the tag from your local repository.")

    raise e
