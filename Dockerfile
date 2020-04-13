FROM python:2.7

ENV DEPLOY_PATH /xueer

RUN mkdir -p $DEPLOY_PATH
WORKDIR $DEPLOY_PATH


ADD requirements.txt requirements.txt

RUN apt-get install libssl-dev libmariadb-dev-compat \
    && pip install mysql-connector-python \
    && pip install --index-url http://pypi.doubanio.com/simple/ -r requirements.txt --trusted-host=pypi.doubanio.com

ADD . .
