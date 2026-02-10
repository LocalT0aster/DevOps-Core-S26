# LAB02 — Multi-Stage Docker Build (Go)

## Multi-Stage Build Strategy

The Go service is built with a two-stage Dockerfile:

1. **Build stage (`golang:1.25-alpine`)**
- Compiles the application binary with `CGO_ENABLED=0 GOOS=linux`.
- Keeps compiler/toolchain in the build environment only.

2. **Runtime stage (`scratch`)**
- Copies only `devops-info-service.out` from the build stage.
- Runs as non-root with `USER 10001:10001`.
- Contains no package manager, shell, or compiler.

Dockerfile used: `app_go/Dockerfile`

```dockerfile
FROM golang:1.25-alpine AS build
WORKDIR /app
COPY go.mod *.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -o devops-info-service.out

FROM scratch
COPY --from=build /app/devops-info-service.out /
USER 10001:10001
CMD ["/devops-info-service.out"]
```

Also, `.dockerignore` keeps context minimal:

```dockerignore
*
!go.mod
!go.sum
!*.go
```

## Technical Explanation of Each Stage

- **`FROM golang:1.25-alpine AS build`**
  Provides Go toolchain and Alpine userspace needed to compile.
- **`WORKDIR /app` + `COPY go.mod *.go ./`**
  Copies only build inputs (module file and source files).
- **`RUN CGO_ENABLED=0 GOOS=linux go build ...`**
  Produces a Linux static binary suitable for `scratch` runtime.
- **`FROM scratch`**
  Starts an empty runtime image.
- **`COPY --from=build ...`**
  Transfers only the compiled artifact, not compilers or source.
- **`USER 10001:10001`**
  Drops root privileges in runtime.

## Build Process (Terminal Output)

<details>
<summary>🔨 Build target</summary>

```log
$ docker build --no-cache --progress=plain --target build -t lab02-go:builder .
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 424B 0.0s done
#1 DONE 0.1s

#2 [internal] load metadata for docker.io/library/golang:1.25-alpine
#2 DONE 1.0s

#3 [internal] load .dockerignore
#3 transferring context: 64B 0.0s done
#3 DONE 0.0s

#4 [internal] load build context
#4 DONE 0.0s

#5 [build 1/4] FROM docker.io/library/golang:1.25-alpine@sha256:f6751d823c26342f9506c03797d2527668d095b0a15f1862cddb4d927a7a4ced
#5 resolve docker.io/library/golang:1.25-alpine@sha256:f6751d823c26342f9506c03797d2527668d095b0a15f1862cddb4d927a7a4ced 0.0s done
#5 DONE 0.1s

#6 [build 2/4] WORKDIR /app
#6 CACHED

#4 [internal] load build context
#4 transferring context: 54B done
#4 DONE 0.0s

#7 [build 3/4] COPY go.mod *.go ./
#7 DONE 0.1s

#8 [build 4/4] RUN CGO_ENABLED=0 GOOS=linux go build -o devops-info-service.out
#8 DONE 62.8s

#9 exporting to image
#9 exporting layers
#9 exporting layers 7.4s done
#9 exporting manifest sha256:f3e73461dd53d9f346f612d14a5d7db25b865b7aab912ba8d3cb89a098da0546
#9 exporting manifest sha256:f3e73461dd53d9f346f612d14a5d7db25b865b7aab912ba8d3cb89a098da0546 0.0s done
#9 exporting config sha256:06ba3662b02750d25c0817c4d26a4d0f77805f722bb6d60fa2b8c04b4308e480 0.0s done
#9 exporting attestation manifest sha256:844a56a9b83102a634becbc82128fa16fd1c41bba4fd9f5c56cf7ed84ec0b2ad 0.0s done
#9 exporting manifest list sha256:f2f7690814f0d4b01954394858a41285da9b7a2a425a2525c36f4f7dfe1577aa done
#9 naming to docker.io/library/lab02-go:builder 0.0s done
#9 unpacking to docker.io/library/lab02-go:builder
#9 unpacking to docker.io/library/lab02-go:builder 1.7s done
#9 DONE 9.4
```

</details>

<details>
<summary>🔨 Final multi-stage target</summary>

```log
$ docker build --no-cache --progress=plain -t lab02-go:final .
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 424B 0.0s done
#1 DONE 0.0s

#2 [internal] load metadata for docker.io/library/golang:1.25-alpine
#2 DONE 0.9s

#3 [internal] load .dockerignore
#3 transferring context: 64B done
#3 DONE 0.0s

#4 [internal] load build context
#4 DONE 0.0s

#5 [build 1/4] FROM docker.io/library/golang:1.25-alpine@sha256:f6751d823c26342f9506c03797d2527668d095b0a15f1862cddb4d927a7a4ced
#5 resolve docker.io/library/golang:1.25-alpine@sha256:f6751d823c26342f9506c03797d2527668d095b0a15f1862cddb4d927a7a4ced 0.0s done
#5 DONE 0.0s

#6 [build 2/4] WORKDIR /app
#6 CACHED

#4 [internal] load build context
#4 transferring context: 54B done
#4 DONE 0.0s

#7 [build 3/4] COPY go.mod *.go ./
#7 DONE 0.1s

#8 [build 4/4] RUN CGO_ENABLED=0 GOOS=linux go build -o devops-info-service.out
#8 DONE 67.4s

#9 [stage-1 1/1] COPY --from=build /app/devops-info-service.out /
#9 DONE 0.1s

#10 exporting to image
#10 exporting layers
#10 exporting layers 1.0s done
#10 exporting manifest sha256:b3ddddd75de1b8fe87ecf287b479ae5804ae9b73e3c8c88b58553ae1e949d209
#10 exporting manifest sha256:b3ddddd75de1b8fe87ecf287b479ae5804ae9b73e3c8c88b58553ae1e949d209 0.0s done
#10 exporting config sha256:65c1bd7c8937841b2bb1e5d455bd1ec37dab85a4e0ac4eab15bf50d1fb61d19a done
#10 exporting attestation manifest sha256:2c7f952e05e64da351b651ceb30a12d35c0304ef9fb21d7dd5089b365862464e 0.0s done
#10 exporting manifest list sha256:2d3f56459e956a745bfe802d54a7f652677a6a993406ec23d7d0334f9ec99af5 0.0s done
#10 naming to docker.io/library/lab02-go:final done
#10 unpacking to docker.io/library/lab02-go:final
#10 unpacking to docker.io/library/lab02-go:final 0.2s done
#10 DONE 1.4s
```

</details>

## Working Containerized Application (Terminal Output)

<details>
<summary>Server</summary>

```bash
$ docker run --rm -p 5000:5000 lab02-go:final
2026/02/10 20:02:11 Application starting on 0.0.0.0:5000
2026/02/10 20:02:27 Request: GET /
2026/02/10 20:03:55 Request: GET /health
```

</details>

<details>
<summary>Client</summary>

```json
$ curl -sS 127.0.0.1:5000 | jq
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "Go net/http"
  },
  "system": {
    "hostname": "1208319f6a92",
    "platform": "Linux",
    "platform_version": "linux",
    "architecture": "amd64",
    "cpu_count": 1,
    "python_version": "go1.25.7"
  },
  "runtime": {
    "seconds": 15,
    "human": "0 hours, 0 minutes"
  },
  "request": {
    "client_ip": "172.17.0.1",
    "user_agent": "curl/8.14.1",
    "method": "GET",
    "path": "/"
  },
  "endpoints": [
    {
      "path": "/",
      "method": "GET",
      "description": "Service information."
    },
    {
      "path": "/health",
      "method": "GET",
      "description": "Health check endpoint."
    }
  ]
}
```

```json
$ curl -sS 127.0.0.1:5000/health | jq
{
  "status": "healthy",
  "timestamp": "2026-02-10T20:03:55.538319+00:00",
  "uptime_seconds": 104
}
```

</details>

## Image Size Comparison and Analysis


| Image                                | Image size   |
| ------------------------------------ | ------------ |
| Builder (`lab02-go:builder`)         | **85.50MiB** |
| Final multi-stage (`lab02-go:final`) | **4.41MiB**  |

<details>
<summary>⚖️ Measuring command</summary>

```bash
docker inspect -f "{{ .Size }}" <image> | numfmt --to=iec-i --format="%.2f"
```
</details>

Reduction from builder to final:
- **94.84%** smaller
- **19.39x** smaller runtime image

These metrics come from the same `docker inspect` size source, so they are directly comparable.

## Why Multi-Stage Builds Matter for Compiled Languages

For Go (and similarly Rust/C/C++), the compiler and build toolchain are large and needed only at build time. Multi-stage builds let us:

- Keep full SDK only in builder stage.
- Ship only the compiled binary in runtime.
- Reduce registry transfer and startup pull time.
- Reduce operational footprint and patch surface in production.

Without multi-stage, runtime image carries unnecessary build dependencies, increasing size and risk.

## Security Implications (Smaller Attack Surface)

Security improvements in this implementation:

- `scratch` runtime has no shell/package manager/toolchain.
- Non-root runtime user via `USER 10001:10001`.
- Fewer filesystem artifacts (only binary), reducing exposure.

Practical impact:

- Fewer components to scan/patch.
- Lower chance of post-exploitation tooling availability inside container.
- Simpler SBOM/runtime dependency graph.

## Trade-Offs and Decisions

### Decisions made

- **Chose `scratch`** for maximal size/security reduction.
- **Used static build (`CGO_ENABLED=0`)** so binary runs in empty base image.
- **Used numeric UID:GID (`10001:10001`)** because `scratch` has no user-management tools.

### Trade-offs

- `scratch` is harder to debug (no shell utilities).
- No bundled CA certs/timezone data by default (important if app adds outbound TLS or timezone-sensitive logic later).
- Builder-stage caching is currently simple; if dependencies grow, splitting module download and source copy can improve cache efficiency further.

## Summary

The multi-stage approach in `app_go/Dockerfile` produces a working, non-root runtime image and achieves major size reduction compared with keeping the full Go toolchain in the final image. The result is a materially smaller and safer production artifact while preserving application functionality.
