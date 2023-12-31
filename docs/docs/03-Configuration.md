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
- `EMIRECORDER__EMIARCHIVE__HOST` -
  host to connect to
  (default: `localhost`)
- `EMIRECORDER__EMIARCHIVE__PORT` -
  port to connect to
  (default: `30000`)
- `EMIRECORDER__EMIARCHIVE__USER` -
  username to connect with
  (default: `readwrite`)
- `EMIRECORDER__EMIARCHIVE__PASSWORD` -
  password to connect with
  (default: `password`)
- `EMIRECORDER__EMIARCHIVE__BUCKET` -
  name of the bucket to use for uploads
  (default: `live`)
- `EMIRECORDER__EMISHOWS__HOST` -
  host to connect to
  (default: `localhost`)
- `EMIRECORDER__EMISHOWS__PORT` -
  port to connect to
  (default: `35000`)
