ARG MINIO_CLIENT_IMAGE_TAG=RELEASE.2022-03-17T20-25-06Z
ARG MINICONDA_IMAGE_TAG=4.10.3-alpine

FROM minio/mc:$MINIO_CLIENT_IMAGE_TAG AS mc

FROM continuumio/miniconda3:$MINICONDA_IMAGE_TAG AS base

COPY --from=mc /usr/bin/mc /usr/bin/mc

# add bash, because it's not available by default on alpine
# and ffmpeg because we need it for streaming
# and ca-certificates for mc
# and git to get pystreams
RUN apk add --no-cache bash ffmpeg ca-certificates git

WORKDIR /app/

# install poetry
COPY ./requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install -r ./requirements.txt

# create new environment
# warning: for some reason conda can hang on "Executing transaction" for a couple of minutes
COPY environment.yaml ./environment.yaml
RUN --mount=type=cache,target=/opt/conda/pkgs \
    conda env create -f ./environment.yaml

# "activate" environment for all commands (note: ENTRYPOINT is separate from SHELL)
SHELL ["conda", "run", "--no-capture-output", "-n", "emirecorder", "/bin/bash", "-c"]

WORKDIR /app/emirecorder/

# add poetry files
COPY ./emirecorder/pyproject.toml ./emirecorder/poetry.lock ./

FROM base AS test

# install dependencies only (notice that no source code is present yet)
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main,test

# add source, tests and necessary files
COPY ./emirecorder/src/ ./src/
COPY ./emirecorder/tests/ ./tests/
COPY ./emirecorder/LICENSE ./emirecorder/README.md ./

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emirecorder

# add entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh", "pytest"]
CMD []

FROM base AS production

# install dependencies only (notice that no source code is present yet)
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main

# add source and necessary files
COPY ./emirecorder/src/ ./src/
COPY ./emirecorder/LICENSE ./emirecorder/README.md ./

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emirecorder

# add entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

ENV EMIRECORDER_HOST=0.0.0.0 \
    EMIRECORDER_PORT=31000 \
    EMIRECORDER_TARGET_HOST=localhost \
    EMIRECORDER_TARGET_PORT=30000 \
    EMIRECORDER_TARGET_USER=readwrite \
    EMIRECORDER_TARGET_PASSWORD=password

EXPOSE 31000
EXPOSE 31000/udp

ENTRYPOINT ["./entrypoint.sh", "emirecorder"]
CMD []
