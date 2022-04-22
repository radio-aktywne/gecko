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

# install poetry
COPY ./requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

# create new environment
# see: https://jcristharif.com/conda-docker-tips.html
# warning: for some reason conda can hang on "Executing transaction" for a couple of minutes
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.pyc' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

# "activate" environment for all commands (note: ENTRYPOINT is separate from SHELL)
SHELL ["conda", "run", "--no-capture-output", "-n", "emirecorder", "/bin/bash", "-c"]

# add poetry files
COPY ./emirecorder/pyproject.toml ./emirecorder/poetry.lock /tmp/emirecorder/
WORKDIR /tmp/emirecorder

ENV EMIRECORDER_PORT=31000 \
    EMIRECORDER_TARGET_HOST=localhost \
    EMIRECORDER_TARGET_PORT=30000 \
    EMIRECORDER_TARGET_USER=readwrite \
    EMIRECORDER_TARGET_PASSWORD=password

EXPOSE 31000
EXPOSE 31000/udp

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "emirecorder"]

FROM base AS test

# install dependencies only (notice that no source code is present yet) and delete cache
RUN poetry install --no-root --extras test && \
    rm -rf ~/.cache/pypoetry

# add source, tests and necessary files
COPY ./emirecorder/src/ /tmp/emirecorder/src/
COPY ./emirecorder/tests/ /tmp/emirecorder/tests/
COPY ./emirecorder/LICENSE ./emirecorder/README.md /tmp/emirecorder/

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emirecorder

CMD ["pytest"]

FROM base AS production

# install dependencies only (notice that no source code is present yet) and delete cache
RUN poetry install --no-root && \
    rm -rf ~/.cache/pypoetry

# add source and necessary files
COPY ./emirecorder/src/ /tmp/emirecorder/src/
COPY ./emirecorder/LICENSE ./emirecorder/README.md /tmp/emirecorder/

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emirecorder

CMD ["emirecorder", "--port", "31000"]
