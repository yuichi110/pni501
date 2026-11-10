ARG GO_VERSION=1.22
FROM golang:${GO_VERSION}-bookworm

WORKDIR /workspace

ENV CGO_ENABLED=0 \
    GOFLAGS="-buildvcs=false"

COPY . /workspace

# Pre-download module dependencies during image build so Stage 2/3 can run with --network=none
RUN if [ -f go.mod ]; then go mod download || true; fi

CMD ["go", "version"]
