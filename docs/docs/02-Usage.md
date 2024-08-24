---
slug: /usage
title: Usage
---

## Listing records

You can list records using the `/records/:event` endpoint.
For example, you can use `curl` to list all records for an event:

```sh
curl \
    --request GET \
    http://localhost:31000/records/0f339cb0-7ab4-43fe-852d-75708232f76c
```

## Uploading and downloading records

You can upload and download records
using the `/records/:event/:start` endpoint.
To upload a record, you can use
[`curl`](https://curl.se) to send a `PUT` request
streaming the content from a file:

```sh
curl \
    --request PUT \
    --header "Content-Type: audio/ogg" \
    --header "Transfer-Encoding: chunked" \
    --upload-file record.ogg \
    http://localhost:31000/record/0f339cb0-7ab4-43fe-852d-75708232f76c/2024-01-01T00:00:00
```

To download a record, you can use
[`curl`](https://curl.se) to send a `GET` request
and save the response body to a file:

```sh
curl \
    --request GET \
    --output record.ogg \
    http://localhost:31000/record/0f339cb0-7ab4-43fe-852d-75708232f76c/2024-01-01T00:00:00
```

## Deleting records

You can delete records using the `/record/:event/:start` endpoint.
For example, you can use `curl` to delete a record:

```sh
curl \
    --request DELETE \
    http://localhost:31000/record/0f339cb0-7ab4-43fe-852d-75708232f76c/2024-01-01T00:00:00
```

## Ping

You can check the status of the app by sending
either a `GET` or `HEAD` request to the `/ping` endpoint.
The app should respond with a `204 No Content` status code.

For example, you can use `curl` to do that:

```sh
curl \
    --request HEAD \
    --head \
    http://localhost:31000/ping
```
