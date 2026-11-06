ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VIRTUAL_ENV=/opt/pni-venv \
    PYTHONPATH="/workspace:/workspace/src" \
    PATH="/opt/pni-venv/bin:$PATH"

RUN if [ -n "${EXTRA_APT_PACKAGES}" ]; then \
      apt-get update \
      && apt-get install -y --no-install-recommends ${EXTRA_APT_PACKAGES} \
      && rm -rf /var/lib/apt/lists/*; \
    fi \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && python3 -m venv /opt/pni-venv \
    && mkdir -p /workspace /out \
    && chown -R pni:pni /workspace /out /opt/pni-venv \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

RUN for req in requirements.txt requirements-dev.txt dev-requirements.txt test-requirements.txt; do \
      if [ -f "$req" ]; then /opt/pni-venv/bin/pip install --no-cache-dir -r "$req"; fi; \
    done \
    && if [ -f pyproject.toml ] || [ -f setup.py ]; then \
         /opt/pni-venv/bin/pip install --no-cache-dir --no-build-isolation -e . \
         || /opt/pni-venv/bin/pip install --no-cache-dir -e . \
         || true; \
       fi \
    && /opt/pni-venv/bin/pip install --no-cache-dir pytest pytest-cov httpx uvicorn \
    && chown -R pni:pni /workspace /opt/pni-venv \
    && chmod -R a+rwX /workspace /opt/pni-venv

USER pni
CMD ["pytest"]
