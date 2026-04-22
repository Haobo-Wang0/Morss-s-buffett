---
name: responses-image-generation
description: Generate images via OpenAI-compatible Responses API with the built-in image_generation tool, streaming SSE, and base64 extraction from response.output_item.done.
metadata:
  {"openclaw":{"emoji":"🖼️"}}
---

# Responses Image Generation

Use this skill when the user asks to create, generate, render, or produce an image and you need an OpenAI-compatible API flow that prefers the **Responses API** over legacy image generation endpoints.

## What this skill does

Default to:

- `POST {baseUrl}/openai/v1/responses`
- `stream: true`
- outer `model: "gpt-5.4"`
- built-in tool `image_generation` with explicit `model: "gpt-image-2"`

Do **not** prefer `/v1/images/generations` unless the user explicitly asks for that older route or the Responses path is unavailable.

## Required request shape

Build the request in this structure:

```json
{
  "model": "gpt-5.4",
  "stream": true,
  "input": [
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "<user prompt here>"
        }
      ]
    }
  ],
  "tools": [
    {
      "type": "image_generation",
      "model": "gpt-image-2"
    }
  ]
}
```

If the compatible provider needs extra fields such as size, background, quality, moderation, or output format, include them only when supported and only if the user asked.

## Endpoint construction

Assume an OpenAI-compatible base URL.

If the configured upstream base is:

- `https://api.asxs.top/`

then the full endpoint becomes:

- `https://api.asxs.top/openai/v1/responses`

In general:

1. start from the actual configured base URL for the target provider
2. normalize away duplicate slashes
3. append `/openai/v1/responses` unless the configured base already includes the OpenAI path

Examples:

- `https://api.asxs.top/` → `https://api.asxs.top/openai/v1/responses`
- `https://api.asxs.top` → `https://api.asxs.top/openai/v1/responses`
- `https://example.com/openai/v1` → `https://example.com/openai/v1/responses`
- `https://example.com/openai/v1/` → `https://example.com/openai/v1/responses`

## Authentication

Use the local configured API key for the target upstream. Do not ask the user to paste it into chat, and do not reveal it back to the user.

If you need to implement code for this skill, read the key from the local configuration or environment and send it as a bearer token.

```http
Authorization: Bearer <api-key>
Content-Type: application/json
Accept: text/event-stream
```

## Streaming and SSE parsing

You must send the request with `stream: true` and parse the Server-Sent Events stream.

Watch for SSE events carrying response items. The critical extraction rule is:

- inspect `response.output_item.done`
- when `item.type == "image_generation_call"` and `item.result` exists
- then `item.result` is the image **base64** payload

Treat that base64 string as the generated image bytes.

### Extraction algorithm

1. Read SSE incrementally.
2. Ignore keepalives and empty lines.
3. For each JSON event payload, inspect the event type.
4. When the event is `response.output_item.done`:
   - read `item`
   - if `item.type === "image_generation_call"` and `item.result` is truthy
   - capture `item.result` as the final image base64
5. If multiple image items appear, collect all of them in order.
6. Only fall back to other response shapes if no matching `response.output_item.done` image item exists.

Pseudocode:

```js
for await (const sseEvent of stream) {
  if (sseEvent.type !== "response.output_item.done") continue;
  const item = sseEvent.item;
  if (item?.type === "image_generation_call" && item.result) {
    images.push(item.result);
  }
}
```

## Output handling

After extracting base64:

1. decode the base64 into bytes
2. write each image to a file such as `out/generated-<timestamp>-<index>.png`
3. return the saved file path(s) or attach the image(s), depending on the calling environment

Assume PNG unless the provider explicitly signals another format.

## Failure handling

If the stream completes without any matching `response.output_item.done` image item:

- report that no image payload was found in the SSE stream
- include the event types seen if useful for debugging
- suggest checking provider compatibility with the Responses API built-in tool `image_generation`

If the provider rejects `image_generation`:

- report the provider error clearly
- do not silently switch to `/v1/images/generations` unless the user asked for fallback behavior

## Implementation notes

- Prefer fewer larger writes and avoid noisy per-line updates.
- Be explicit about `model: "gpt-image-2"` inside the tool object.
- Keep the outer model as `gpt-5.4` unless the caller explicitly changes it.
- Keep `stream: true` always for this workflow.
- If you are writing helper code, make the SSE parser resilient to:
  - `event:` lines
  - multi-line `data:` payloads
  - `[DONE]`
  - blank line separators

## Minimal curl example

```bash
curl -N -X POST "https://api.asxs.top/openai/v1/responses" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "model": "gpt-5.4",
    "stream": true,
    "input": [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "A cinematic red panda astronaut floating in low earth orbit, highly detailed"
          }
        ]
      }
    ],
    "tools": [
      {
        "type": "image_generation",
        "model": "gpt-image-2"
      }
    ]
  }'
```

## Trigger hints

This skill is especially relevant for requests like:

- “创建一张图”
- “生图”
- “generate an image”
- “用 Responses API 出图”
- “不要走 /images/generations”
- “用 image_generation tool”
- “从 SSE 里拿 base64 图”
