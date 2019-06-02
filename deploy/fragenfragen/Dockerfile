FROM python:alpine 

LABEL maintainer="olf42"

COPY 100hackerfragen /src
COPY requirements_fragenfragen.txt /src
COPY entrypoint_fragenfragen.sh /src

WORKDIR /src

RUN pip install -r requirements_fragenfragen.txt

EXPOSE 5000

ENTRYPOINT ["./entrypoint_fragenfragen.sh"]

