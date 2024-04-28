---
slug: /configuration
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMIRECORDER__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `EMIRECORDER__SERVER__PORT` -
  port to run the server on
  (default: `31000`)
- `EMIRECORDER__RECORDER__HOST` -
  host to listen for connections on
  (default: `0.0.0.0`)
- `EMIRECORDER__RECORDER__PORTS` -
  ports to select from when listening for connections
  (default: `31000`)
- `EMIRECORDER__RECORDER__TIMEOUT` -
  time after which a stream will be stopped if no connections are made
  (default: `PT1M`)
- `EMIRECORDER__RECORDER__WINDOW` -
  time window to search for event instances around the current time
  (default: `PT1H`)
- `EMIRECORDER__EMIARCHIVE__S3__SECURE` -
  whether to use secure connections for the S3 API of the emiarchive service
  (default: `false`)
- `EMIRECORDER__EMIARCHIVE__S3__HOST` -
  host of the S3 API of the emiarchive service
  (default: `localhost`)
- `EMIRECORDER__EMIARCHIVE__S3__PORT` -
  port of the S3 API of the emiarchive service
  (default: `30000`)
- `EMIRECORDER__EMIARCHIVE__S3__USER` -
  username to authenticate with the S3 API of the emiarchive service
  (default: `readwrite`)
- `EMIRECORDER__EMIARCHIVE__S3__PASSWORD` -
  password to authenticate with the S3 API of the emiarchive service
  (default: `password`)
- `EMIRECORDER__EMIARCHIVE__S3__BUCKET` -
  name of the bucket to use for uploads
  (default: `live`)
- `EMIRECORDER__EMISHOWS__HTTP__SCHEME` -
  scheme of the HTTP API of the emishows service
  (default: `http`)
- `EMIRECORDER__EMISHOWS__HTTP__HOST` -
  host of the HTTP API of the emishows service
  (default: `localhost`)
- `EMIRECORDER__EMISHOWS__HTTP__PORT` -
  port of the HTTP API of the emishows service
  (default: `35000`)
- `EMIRECORDER__EMISHOWS__HTTP__PATH` -
  path of the HTTP API of the emishows service
  (default: ``)
