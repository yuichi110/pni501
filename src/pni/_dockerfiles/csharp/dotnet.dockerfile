ARG DOTNET_VERSION=8.0
FROM mcr.microsoft.com/dotnet/sdk:${DOTNET_VERSION}

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 \
    DOTNET_NOLOGO=1 \
    NUGET_PACKAGES="/nuget" \
    DOTNET_CLI_HOME="/dotnet-home"

RUN if [ -n "${EXTRA_APT_PACKAGES}" ]; then \
      apt-get update \
      && apt-get install -y --no-install-recommends ${EXTRA_APT_PACKAGES} \
      && rm -rf /var/lib/apt/lists/*; \
    fi \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /nuget /dotnet-home \
    && chown -R pni:pni /workspace /out /nuget /dotnet-home \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

# Pre-restore NuGet packages and build assemblies so Stage 2/3 can run with --network=none
RUN if ls *.sln *.csproj >/dev/null 2>&1 || find . -maxdepth 3 \( -name '*.sln' -o -name '*.csproj' \) | grep -q .; then \
      dotnet restore --disable-parallel || dotnet restore || true; \
      dotnet build --no-restore || dotnet build || true; \
    fi \
    && chown -R pni:pni /workspace /nuget /dotnet-home \
    && chmod -R a+rwX /workspace /nuget /dotnet-home /out

USER pni
CMD ["dotnet", "--version"]
