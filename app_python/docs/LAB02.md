# LAB02 - Docker Containerization (Python)

## Docker Best Practices Applied

1. **Pinned base image version** - guarantees repeatable builds and avoids unexpected upstream changes.

```Dockerfile
FROM python:3.14-alpine
```

2. **Non-root user** - reduces blast radius if the app is compromised.

```Dockerfile
RUN addgroup appgroup && adduser --disabled-password --gecos "" --no-create-home -s /bin/sh appuser -G appgroup
USER appuser
```

3. **Layer caching for dependencies** - installing requirements before copying the full app keeps rebuilds fast when only code changes.

```Dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

4. **Minimal build context via .dockerignore** - avoids sending unrelated files (venv, git, docs) to the build context.

```dockerignore
*
!app.py
!requirements.txt
!tests/*
```

5. **No pip cache** - prevents leaving package download caches in the image.

```Dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

6. **Explicit workdir** - ensures all app files live under a single predictable path.

```Dockerfile
WORKDIR /app
```

## Image Information & Decisions

**Base image chosen:** `python:3.14-alpine`

**Why:**

- Pinned Python version for reproducibility.
- Alpine variant keeps the runtime small and reduces attack surface.
- The app is pure-Python, so musl vs glibc compatibility is not an issue here.

**Final image size:**

```bash
$ docker inspect -f "{{ .Size }}" localt0aster/devops-app-py:lab.2 | numfmt --to=iec-i --format="%.2f"
22.82Mi
```

**Layer structure (top to bottom):**

- Base image: Python runtime on Alpine.
- User/group creation: creates `appuser` and drops root privileges.
- Workdir: standardizes file locations.
- Dependency layer: copy `requirements.txt`, then install dependencies.
- App layer: copy remaining files into `/app`.
- Cleanup: remove `requirements.txt` (runtime tidiness).
- Runtime config: set `HOST` and `PORT` env vars.
- Switch to non-root user and start app.

**Optimization choices:**

- Used Alpine for smaller base image.
- Copied `requirements.txt` separately to maximize build cache hits.
- Used `pip --no-cache-dir` to avoid cached wheel files.
- `.dockerignore` reduces context size and speeds up builds.
- Note: `RUN rm requirements.txt` in a separate layer does not reduce image size; it only removes it from the final filesystem view.

## Build & Run Process

<details>
<summary>🔨 Build output</summary>

```log
$ docker build --no-cache --progress=plain -t localt0aster/devops-app-py .
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 369B done
#1 DONE 0.0s

#2 [internal] load metadata for docker.io/library/python:3.14-alpine
#2 DONE 0.5s

#3 [internal] load .dockerignore
#3 transferring context: 77B done
#3 DONE 0.0s

#4 [1/7] FROM docker.io/library/python:3.14-alpine@sha256:faee120f7885a06fcc9677922331391fa690d911c020abb9e8025ff3d908e510
#4 resolve docker.io/library/python:3.14-alpine@sha256:faee120f7885a06fcc9677922331391fa690d911c020abb9e8025ff3d908e510 0.0s done
#4 CACHED

#5 [internal] load build context
#5 transferring context: 123B done
#5 DONE 0.0s

#6 [2/7] RUN addgroup appgroup && adduser --disabled-password --gecos "" --no-create-home -s /bin/sh appuser -G appgroup
#6 DONE 0.3s

#7 [3/7] WORKDIR /app
#7 DONE 0.1s

#8 [4/7] COPY requirements.txt .
#8 DONE 0.1s

#9 [5/7] RUN pip install --no-cache-dir -r requirements.txt
#9 4.545 Collecting blinker==1.9.0 (from -r requirements.txt (line 1))
#9 4.736   Downloading blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
#9 4.814 Collecting certifi==2026.1.4 (from -r requirements.txt (line 2))
#9 4.855   Downloading certifi-2026.1.4-py3-none-any.whl.metadata (2.5 kB)
#9 5.098 Collecting charset-normalizer==3.4.4 (from -r requirements.txt (line 3))
#9 5.140   Downloading charset_normalizer-3.4.4-cp314-cp314-musllinux_1_2_x86_64.whl.metadata (37 kB)
#9 5.229 Collecting click==8.3.1 (from -r requirements.txt (line 4))
#9 5.270   Downloading click-8.3.1-py3-none-any.whl.metadata (2.6 kB)
#9 5.417 Collecting Flask==3.1.2 (from -r requirements.txt (line 5))
#9 5.458   Downloading flask-3.1.2-py3-none-any.whl.metadata (3.2 kB)
#9 5.517 Collecting idna==3.11 (from -r requirements.txt (line 6))
#9 5.560   Downloading idna-3.11-py3-none-any.whl.metadata (8.4 kB)
#9 5.608 Collecting itsdangerous==2.2.0 (from -r requirements.txt (line 7))
#9 5.648   Downloading itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
#9 5.711 Collecting Jinja2==3.1.6 (from -r requirements.txt (line 8))
#9 5.752   Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
#9 5.877 Collecting MarkupSafe==3.0.3 (from -r requirements.txt (line 9))
#9 5.928   Downloading markupsafe-3.0.3-cp314-cp314-musllinux_1_2_x86_64.whl.metadata (2.7 kB)
#9 6.003 Collecting requests==2.32.5 (from -r requirements.txt (line 10))
#9 6.048   Downloading requests-2.32.5-py3-none-any.whl.metadata (4.9 kB)
#9 6.120 Collecting urllib3==2.6.3 (from -r requirements.txt (line 11))
#9 6.160   Downloading urllib3-2.6.3-py3-none-any.whl.metadata (6.9 kB)
#9 6.251 Collecting Werkzeug==3.1.5 (from -r requirements.txt (line 12))
#9 6.296   Downloading werkzeug-3.1.5-py3-none-any.whl.metadata (4.0 kB)
#9 6.399 Downloading blinker-1.9.0-py3-none-any.whl (8.5 kB)
#9 6.440 Downloading certifi-2026.1.4-py3-none-any.whl (152 kB)
#9 6.530 Downloading charset_normalizer-3.4.4-cp314-cp314-musllinux_1_2_x86_64.whl (154 kB)
#9 6.577 Downloading click-8.3.1-py3-none-any.whl (108 kB)
#9 6.620 Downloading flask-3.1.2-py3-none-any.whl (103 kB)
#9 6.662 Downloading idna-3.11-py3-none-any.whl (71 kB)
#9 6.704 Downloading itsdangerous-2.2.0-py3-none-any.whl (16 kB)
#9 6.743 Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
#9 6.792 Downloading markupsafe-3.0.3-cp314-cp314-musllinux_1_2_x86_64.whl (23 kB)
#9 6.831 Downloading requests-2.32.5-py3-none-any.whl (64 kB)
#9 6.871 Downloading urllib3-2.6.3-py3-none-any.whl (131 kB)
#9 6.915 Downloading werkzeug-3.1.5-py3-none-any.whl (225 kB)
#9 6.985 Installing collected packages: urllib3, MarkupSafe, itsdangerous, idna, click, charset-normalizer, certifi, blinker, Werkzeug, requests, Jinja2, Flask
#9 8.701 
#9 8.709 Successfully installed Flask-3.1.2 Jinja2-3.1.6 MarkupSafe-3.0.3 Werkzeug-3.1.5 blinker-1.9.0 certifi-2026.1.4 charset-normalizer-3.4.4 click-8.3.1 idna-3.11 itsdangerous-2.2.0 requests-2.32.5 urllib3-2.6.3
#9 8.710 WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
#9 9.000 
#9 9.000 [notice] A new release of pip is available: 25.3 -> 26.0.1
#9 9.000 [notice] To update, run: pip install --upgrade pip
#9 DONE 9.4s

#10 [6/7] COPY . .
#10 DONE 0.1s

#11 [7/7] RUN rm requirements.txt
#11 DONE 0.3s

#12 exporting to image
#12 exporting layers
#12 exporting layers 1.4s done
#12 exporting manifest sha256:0e08d9c814e82ba9bfc64ab9bffca15d59c52f63d1b9db264e10723bf23c2daf
#12 exporting manifest sha256:0e08d9c814e82ba9bfc64ab9bffca15d59c52f63d1b9db264e10723bf23c2daf 0.0s done
#12 exporting config sha256:89b3883bbcb401b8bc8aa815aef1cde31083c25f245921185ce4acae286a51fb 0.0s done
#12 exporting attestation manifest sha256:fbcf722602c9bb0c149874e7052029e55cebf067e88f7448a0282f3b3fb1b926 0.0s done
#12 exporting manifest list sha256:24ce3d2f1f6270cedba6257c73fd1b5105b821025b9e38f87798ca75fba493d7
#12 exporting manifest list sha256:24ce3d2f1f6270cedba6257c73fd1b5105b821025b9e38f87798ca75fba493d7 0.0s done
#12 naming to docker.io/localt0aster/devops-app-py:latest done
#12 unpacking to docker.io/localt0aster/devops-app-py:latest
#12 unpacking to docker.io/localt0aster/devops-app-py:latest 0.5s done
#12 DONE 2.1s

 1 warning found (use docker --debug to expand):
 - CopyIgnoredFile: Attempting to Copy file "." that is excluded by .dockerignore (line 6)
```

</details>

<details>
<summary>🏃 Run output</summary>

```log
$ docker run -p 5000:5000 --rm localt0aster/devops-app-py
2026-02-10 16:52:32,232 - __main__ - INFO - Application starting...
 * Serving Flask app 'app'
 * Debug mode: off
2026-02-10 16:52:32,238 - werkzeug - INFO - WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.2:5000
2026-02-10 16:52:32,239 - werkzeug - INFO - Press CTRL+C to quit
2026-02-10 16:53:49,498 - werkzeug - INFO - 172.17.0.1 - - [10/Feb/2026 16:53:49] "GET / HTTP/1.1" 200 -
```

</details>

<details>
<summary>🛰️ Endpoint test output</summary>

```json
$ curl -Ss 127.0.0.1:5000 | jq
{
  "endpoints": [
    {
      "description": "Service information",
      "method": "GET",
      "path": "/"
    },
    {
      "description": "Health check",
      "method": "GET",
      "path": "/health"
    }
  ],
  "request": {
    "client_ip": "172.17.0.1",
    "method": "GET",
    "path": "/",
    "user_agent": "curl/8.14.1"
  },
  "runtime": {
    "human": "0 hours, 1 minutes",
    "seconds": 86
  },
  "service": {
    "description": "DevOps course info service",
    "framework": "Flask",
    "name": "devops-info-service",
    "version": "1.0.0"
  },
  "system": {
    "architecture": "x86_64",
    "cpu_count": 1,
    "hostname": "bd45062076fd",
    "platform": "Linux",
    "platform_version": "Alpine Linux v3.23",
    "python_version": "3.14.3"
  }
}
```

</details>

Docker Hub repository URL: <https://hub.docker.com/r/localt0aster/devops-app-py>

## Technical Analysis

**Why this Dockerfile works:**

- Dependencies are installed before application code, enabling Docker cache reuse.
- Environment variables set defaults that match the Flask app’s config.
- The `CMD` runs the app with `python app.py`, which is the same startup command as local development.
- `USER appuser` prevents the Flask process from running as root.

**What happens if you change the layer order:**

- If `COPY . .` comes before `pip install`, any code change will invalidate the cache and force a full dependency reinstall.
- If you install dependencies after copying everything, small edits trigger slower rebuilds.

**Security considerations implemented:**

- Non-root user for runtime.
- Minimal base image reduces available tooling and attack surface.
- Pinned base image version reduces supply-chain drift.

**How .dockerignore improves the build:**

- Less data sent to the Docker daemon means faster builds.
- Prevents accidental inclusion of venvs, git history, and local artifacts.

## Challenges & Solutions

- **Debian to Alpine command differences.**
  - Issue: `python:3.14-slim` (Debian) lab examples use `useradd/groupadd`, which don’t exist in `python:3.14-alpine`.
  - Fix: use `addgroup` & `adduser`
