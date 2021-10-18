# wol
A Python app to wake computers with Wake on Lan

## Project dependencies

    pip install --upgrade pip
    pip install --upgrade wakeonlan python-consul pulsar-client fastavro
    pip freeze > requirements.txt
    sed -i '/pkg_resources/d' requirements.txt

