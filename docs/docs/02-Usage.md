---
slug: /usage
title: Usage
---

## Listing records

You can list records using the `/records/:event` endpoint.
For example, you can use `curl` to list all records for an event:

```sh
curl --request GET http://localhost:10700/records/0f339cb0-7ab4-43fe-852d-75708232f76c
```

## Uploading and downloading records

You can upload and download records using the `/records/:event/:start` endpoint.
To upload a record, you can use `curl`
to send a `PUT` request streaming the content from a file:

```sh
curl \
    --request PUT \
    --header "Content-Type: audio/ogg" \
    --header "Transfer-Encoding: chunked" \
    --upload-file record.ogg \
    http://localhost:10700/records/0f339cb0-7ab4-43fe-852d-75708232f76c/2024-01-01T00:00:00
```

To download a record, you can use `curl`
to send a `GET` request and save the response body to a file:

```sh
curl --request GET --output record.ogg http://localhost:10700/record/0f339cb0-7ab4-43fe-852d-75708232f76c/2024-01-01T00:00:00
```

## Deleting records

You can delete records using the `/record/:event/:start` endpoint.
For example, you can use `curl` to delete a record:

```sh
curl --request DELETE http://localhost:10700/records/0f339cb0-7ab4-43fe-852d-75708232f76c/2024-01-01T00:00:00
```

## Ping

You can check the status of the service by sending
either a `GET` or `HEAD` request to the `/ping` endpoint.
The service should respond with a `204 No Content` status code.

For example, you can use `curl` to do that:

```sh
curl --request HEAD --head http://localhost:10700/ping
```

## Server-Sent Events

You can subscribe to
[`Server-Sent Events (SSE)`](https://developer.mozilla.org/docs/Web/API/Server-sent_events)
by sending a `GET` request to the `/sse` endpoint.
The service should send you the events as they happen.

For example, you can use `curl` to do that:

```sh
curl --request GET --no-buffer http://localhost:10700/sse
```

## OpenAPI

You can view the [`OpenAPI`](https://www.openapis.org)
documentation made with [`Scalar`](https://scalar.com)
by navigating to the `/openapi` endpoint in your browser.

You can also download the specification in JSON format
by sending a `GET` request to the `/openapi/openapi.json` endpoint.

For example, you can use `curl` to do that:

```sh
curl --request GET http://localhost:10700/openapi/openapi.json
```
