FROM python:3.5
ENV PYTHONBUFFERED 1
COPY /docker-entrypoint.sh /docker-entrypoint.sh
RUN mkdir /config
ADD /config/requirements.txt /config/
RUN pip install -r /config/requirements.txt
RUN mkdir /src;
WORKDIR /src
ENTRYPOINT ["/docker-entrypoint.sh"]