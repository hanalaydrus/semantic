FROM python:2.7

RUN apt-get update && \
	apt-get install -y build-essential

RUN pip install --upgrade pip
RUN pip install Flask grpcio grpcio-tools mysql-connector requests numpy

COPY . /app
WORKDIR /app

RUN make build

EXPOSE 50049

CMD ["make","run"]