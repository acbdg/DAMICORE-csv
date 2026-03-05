#./bashrc
#!/usr/bin/env bash


# 1. Exit current env if active
deactivate

# 2. Remove the incompatible env
rm -rf damicore_env

# 3. Create a NEW env using Python 3.10 or 3.11
# (If you don't have 3.10, install it via 'brew install python@3.10')
python3.10 -m venv damicore_env

# 4. Activate it
source damicore_env/bin/activate

# 5. Install from the requirements file
pip install --upgrade pip
pip install -r requirements.txt

