---
slug: /config
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMIRECORDS__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `EMIRECORDS__SERVER__PORT` -
  port to run the server on
  (default: `31000`)
- `EMIRECORDS__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
- `EMIRECORDS__EMISHOWS__HTTP__SCHEME` -
  scheme of the HTTP API of the emishows service
  (default: `http`)
- `EMIRECORDS__EMISHOWS__HTTP__HOST` -
  host of the HTTP API of the emishows service
  (default: `localhost`)
- `EMIRECORDS__EMISHOWS__HTTP__PORT` -
  port of the HTTP API of the emishows service
  (default: `35000`)
- `EMIRECORDS__EMISHOWS__HTTP__PATH` -
  path of the HTTP API of the emishows service
  (default: ``)
- `EMIRECORDS__MEDIARECORDS__S3__SECURE` -
  whether to use secure connections for the S3 API of the mediarecords database
  (default: `false`)
- `EMIRECORDS__MEDIARECORDS__S3__HOST` -
  host of the S3 API of the mediarecords database
  (default: `localhost`)
- `EMIRECORDS__MEDIARECORDS__S3__PORT` -
  port of the S3 API of the mediarecords database
  (default: `30000`)
- `EMIRECORDS__MEDIARECORDS__S3__USER` -
  user to authenticate with the S3 API of the mediarecords database
  (default: `readwrite`)
- `EMIRECORDS__MEDIARECORDS__S3__PASSWORD` -
  password to authenticate with the S3 API of the mediarecords database
  (default: `password`)
- `EMIRECORDS__DEBUG` -
  enable debug mode
  (default: `false`)
