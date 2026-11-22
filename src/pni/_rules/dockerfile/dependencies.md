# Base Image & OS Package Dependency Standards (Dockerfile)

## Core Principles
1. **Pinned Base Images & Supported OS Releases**: Pin official/verified base images to explicit versions or digests (`python:3.12-slim@sha256:...`; `ProjectFacts.unpinned_dependencies`), and avoid EOL distributions (Debian Buster/Stretch, Alpine `< 3.19`, Ubuntu `< 22.04`).
2. **Minimal OS Packages & Clean Lockfile Caching**: Copy dependency manifests/lockfiles (`pyproject.toml`/`uv.lock`, `package-lock.json`, `go.mod`/`go.sum`, `Cargo.lock`) BEFORE copying application source so Docker caches dependency installs cleanly, and install OS packages with `--no-install-recommends` (Debian) or `--no-cache` (Alpine).
3. **Zero Build-Tools in Runtime Stage**: Keep compilers (`gcc`, `build-essential`, `git`, `curl`) confined to the `builder` stage — never ship them in the final runtime image.
4. **Automated Image Vulnerability & Dependency Updates**: Enable Renovate/Dependabot (`docker` ecosystem) and scan built images with Trivy (`--severity HIGH,CRITICAL`).

## Evaluation Thresholds
- **`PASS`**: Supported non-EOL base images pinned cleanly, lockfile-first layer ordering, minimal runtime packages, and zero build tools in final stage.
- **`WARN`**: Version-tagged (non-digest) base images or minor cache-ordering suboptimality.
- **`FAIL`**: `:latest` tags, EOL OS base images with unpatched CVEs, or compilers/secrets left in final production images.
