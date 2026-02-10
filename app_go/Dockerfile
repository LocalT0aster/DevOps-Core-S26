FROM golang:1.25-alpine AS build
WORKDIR /app
# Uncomment for dependency installation
# COPY go.mod go.sum ./
# RUN go mod download
COPY go.mod *.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -o devops-info-service.out

FROM scratch
COPY --from=build /app/devops-info-service.out /
# Use UID:GID to avoid copying user info (/etc/passwd)
USER 10001:10001
CMD ["/devops-info-service.out"]
