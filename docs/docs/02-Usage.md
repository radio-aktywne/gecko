---
slug: /usage
title: Usage
---

## Requesting a recording

You can request a recording by sending a `POST` request to the `/record` endpoint.
The request body should contain the information
about the event associated with the stream.
See the API documentation for more details.

For example, you can use [`curl`](https://curl.se) to do that:

```sh
curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"event": "747c31a8-74d2-497f-ba89-cdd85b243e5d"}' \
    http://localhost:31000/record
```

You should receive a response containing the credentials and port number
that you can use to connect to the stream and start sending audio.
The credentials are only valid for a limited time.

## Sending audio

You can send audio to record using the
[`SRT`](https://www.haivision.com/products/srt-secure-reliable-transport)
protocol.

As the audio codec and container,
by default you should use [`Opus`](https://opus-codec.org) and
[`Ogg`](https://www.xiph.org/ogg) respectively.
They are free and open source, focused on quality and efficiency,
and support embedding metadata into the stream.

Remember to use the token and port you received in the previous step
to connect to the stream.

For example, you can use [`Liquidsoap`](https://www.liquidsoap.info) for that:

```sh
liquidsoap \
    'output.srt(
        host="127.0.0.1",
        port=31000,
        passphrase="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        %ogg(%opus),
        sine()
    )'
```

Alternatively, you can use [`ffmpeg`](https://ffmpeg.org) to do the same:

```sh
ffmpeg \
    -re \
    -f lavfi \
    -i sine \
    -c libopus \
    -f ogg \
    -passphrase "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
    srt://127.0.0.1:31000
```
