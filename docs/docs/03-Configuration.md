---
slug: /configuration
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMIRECORDS__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `EMIRECORDS__SERVER__PORTS__HTTP` -
  port to listen for HTTP requests on
  (default: `31000`)
- `EMIRECORDS__SERVER__PORTS__SRT` -
  ports to select from when listening for SRT streams
  (default: `31000`)
- `EMIRECORDS__RECORDER__TIMEOUT` -
  time after which a stream will be stopped if no connections are made
  (default: `PT1M`)
- `EMIRECORDS__RECORDER__WINDOW` -
  time window to search for event instances around the current time
  (default: `PT1H`)
- `EMIRECORDS__DATARECORDS__S3__SECURE` -
  whether to use secure connections for the S3 API of the datarecords service
  (default: `false`)
- `EMIRECORDS__DATARECORDS__S3__HOST` -
  host of the S3 API of the datarecords service
  (default: `localhost`)
- `EMIRECORDS__DATARECORDS__S3__PORT` -
  port of the S3 API of the datarecords service
  (default: `30000`)
- `EMIRECORDS__DATARECORDS__S3__USER` -
  username to authenticate with the S3 API of the datarecords service
  (default: `readwrite`)
- `EMIRECORDS__DATARECORDS__S3__PASSWORD` -
  password to authenticate with the S3 API of the datarecords service
  (default: `password`)
- `EMIRECORDS__DATARECORDS__S3__BUCKET` -
  name of the bucket to use for uploads
  (default: `live`)
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
