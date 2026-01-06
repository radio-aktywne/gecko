---
slug: /config
title: Configuration
---

## Environment variables

You can configure the service at runtime using various environment variables:

- `GECKO__BEAVER__HTTP__HOST` -
  host of the HTTP API of the beaver service
  (default: `localhost`)
- `GECKO__BEAVER__HTTP__PATH` -
  path of the HTTP API of the beaver service
  (default: ``)
- `GECKO__BEAVER__HTTP__PORT` -
  port of the HTTP API of the beaver service
  (default: `10500`)
- `GECKO__BEAVER__HTTP__SCHEME` -
  scheme of the HTTP API of the beaver service
  (default: `http`)
- `GECKO__DEBUG` -
  enable debug mode
  (default: `true`)
- `GECKO__EMERALD__S3__HOST` -
  host of the S3 API of the emerald database
  (default: `localhost`)
- `GECKO__EMERALD__S3__PASSWORD` -
  password to authenticate with the S3 API of the emerald database
  (default: `password`)
- `GECKO__EMERALD__S3__PORT` -
  port of the S3 API of the emerald database
  (default: `10710`)
- `GECKO__EMERALD__S3__SECURE` -
  whether to use secure connections for the S3 API of the emerald database
  (default: `false`)
- `GECKO__EMERALD__S3__USER` -
  user to authenticate with the S3 API of the emerald database
  (default: `readwrite`)
- `GECKO__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `GECKO__SERVER__PORT` -
  port to run the server on
  (default: `10700`)
- `GECKO__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
