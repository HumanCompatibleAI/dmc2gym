PATH_TO_VENV=$1

virtualenv -p python3.9 ${PATH_TO_VENV}
source ${PATH_TO_VENV}/bin/activate
python -m pip install --upgrade pip
pip install ".[test]"