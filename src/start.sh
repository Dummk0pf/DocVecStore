export PYTHONPATH="/vector_search/src"
echo "PYTHONPATH is set"
export CONFIG_FILE_PATH="$PYTHONPATH/settings/config.yaml"
echo "CONFIG_FILE_PATH is set"
echo "Starting Application"
python app.py