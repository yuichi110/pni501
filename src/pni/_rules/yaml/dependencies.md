# CI Action, Helm Chart & Image Pinning Standards (YAML)

## Core Principles
1. **SHA-Pinned GitHub Actions & Container Images**: Pin third-party GitHub Actions (`uses: org/repo@<40-hex-sha>`) and Kubernetes/Compose `image:` fields (`repo/app:v1.2.3@sha256:...` — never `:latest`; `ProjectFacts.unpinned_dependencies`).
2. **Pinned Helm Chart Dependencies (`Chart.lock`)**: For Helm charts with external subcharts in `Chart.yaml`, commit `Chart.lock` (`helm dependency update`; `ProjectFacts.lockfiles_found`). Standalone config/CI YAML directories legitimately omit lockfiles.
3. **Automated Dependency Updates**: Configure Renovate or Dependabot (`github-actions`, `docker`, `helm-values` ecosystems) so pinned SHAs and tags stay patched automatically.
4. **Supply-Chain & Policy Auditing**: Scan YAML manifests in CI with `trivy config`, `actionlint`, `zizmor` (GitHub Actions security), or `kube-linter` / `kyverno`.

## Evaluation Thresholds
- **`PASS`**: SHA-pinned third-party Actions, pinned container image versions (zero `:latest`), `Chart.lock` committed for Helm charts, and Dependabot/Renovate enabled.
- **`WARN`**: Major-tag pinned official Actions without commit SHAs or missing automated update config.
- **`FAIL`**: Unpinned `@main`/`@master` third-party Actions, `:latest` production K8s images, or vulnerable unmaintained Helm charts.
