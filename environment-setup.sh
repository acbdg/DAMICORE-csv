#./bashrc
#!/usr/bin/env bash

# Create the virtual environment
python3 -m venv damicore_env

# Activate it
# On Windows: damicore_env\Scripts\activate
# On Mac/Linux:
source damicore_env/bin/activate

# Install dependencies
pip install pandas toytree toyplot numpy

