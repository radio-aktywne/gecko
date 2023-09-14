---
slug: /configuration
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMIRECORDER_SERVER__HOST` -
  host to run the app on
  (default: `0.0.0.0`)
- `EMIRECORDER_SERVER__PORT` -
  port to run the app on
  (default: `31000`)
- `EMIRECORDER_SERVER__CONCURRENCY` -
  number of concurrent requests to handle
  (default: empty, which means no limit)
- `EMIRECORDER_SERVER__BACKLOG` -
  number of requests to queue
  (default: `2048`)
- `EMIRECORDER_SERVER__KEEPALIVE` -
  number of seconds to keep connections alive
  (default: `5`)
- `EMIRECORDER_RECORDING__TIMEOUT` -
  number of seconds to wait for a connection
  (default: `60`)
- `EMIRECORDER_RECORDING__FORMAT` -
  format to record in
  (default: `ogg`)
- `EMIRECORDER_EMIARCHIVE__HOST` -
  host to connect to
  (default: `localhost`)
- `EMIRECORDER_EMIARCHIVE__PORT` -
  port to connect to
  (default: `30000`)
- `EMIRECORDER_EMIARCHIVE__USER` -
  username to connect with
  (default: `readwrite`)
- `EMIRECORDER_EMIARCHIVE__PASSWORD` -
  password to connect with
  (default: `password`)
- `EMIRECORDER_EMIARCHIVE__BUCKET` -
  name of the bucket to use for uploads
  (default: `live`)
