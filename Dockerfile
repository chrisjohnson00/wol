FROM python:3.9.5-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

#    echo "temporary1" && pip install kafka-python jsonpickle && \
#    pip install -i https://test.pypi.org/simple/ kme

COPY . .

CMD [ "python", "./app.py" ]
