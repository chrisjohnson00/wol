# wol
A Python app to wake computers with Wake on Lan

## Project dependencies

    pip install --upgrade pip
    pip install --upgrade wakeonlan python-consul redis
    pip freeze > requirements.txt
    sed -i '/pkg-resources/d' requirements.txt

## Running Redis locally

```
docker run --name redis --rm -d -p 6379:6379 redis redis-server --appendonly yes
```
