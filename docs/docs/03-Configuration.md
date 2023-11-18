---
slug: /configuration
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMIRECORDER__SERVER__HOST` -
  host to run the app on
  (default: `0.0.0.0`)
- `EMIRECORDER__SERVER__PORT` -
  port to run the app on
  (default: `31000`)
- `EMIRECORDER__RECORDING__TIMEOUT` -
  number of seconds to wait for a connection
  (default: `60`)
- `EMIRECORDER__RECORDING__FORMAT` -
  format to record in
  (default: `ogg`)
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
