FROM python:3.5
ADD . /hello
WORKDIR /hello
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]