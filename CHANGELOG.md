# Changelog

Notable changes to EmbedCrate are documented here.

## 2026-10-24

Release: `2026.10.1`

### Changed

- Established the first tagged source release. Docker images continue to update
  independently through existing moving tags.

## 2026-10-09

### Changed

- Rebranded as EmbedCrate (formerly `docker-embeddings`); the Docker image
  name remains `hwdsl2/embeddings-server`.

## 2026-07-09

### Added

- Added anonymous aggregate deployment/upgrade counts. Opt out with
  `EMBED_DISABLE_USAGE_COUNTS=1`.

## 2026-06-20

### Added

- Added automatic API-key generation by default for fresh installs with
  persistent storage. Retrieve the key with `embed_manage --getkey`.
  Existing volumes without a key retain their previous authentication behavior.

## 2026-05-25

### Added

- Added native ARM64 images alongside AMD64 images.

## 2026-05-24

### Added

- Added reranking support using a separate model and endpoint.

## Earlier notable changes

- Added OpenAI-compatible embeddings backed by Text Embeddings Inference,
  persistent model caching, and model-management commands.
