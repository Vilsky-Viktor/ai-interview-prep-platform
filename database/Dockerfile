# The official image plus pgvector, which library uses to find topics similar to a new one.
FROM postgres:18-alpine

ARG PGVECTOR_VERSION=0.8.1

RUN apk add --no-cache --virtual .build-deps git build-base \
    && git clone --depth 1 --branch v${PGVECTOR_VERSION} https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && make -C /tmp/pgvector OPTFLAGS="" with_llvm=no \
    && make -C /tmp/pgvector install with_llvm=no \
    && rm -rf /tmp/pgvector \
    && apk del .build-deps
