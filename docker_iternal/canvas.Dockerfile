FROM golang:1.24

WORKDIR /usr/src/app


COPY ./canvas/go.mod ./canvas/go.sum ./
RUN go mod download

COPY ./canvas .
RUN go build -o canvas ./cmd/server


EXPOSE 8004

CMD  go run ./cmd/server/