# Agnes AI Model Reference

Text/image limits and legacy quota snapshot: 2026-07-30 Asia/Singapore. Video model and retrieval routing checked against official documentation on 2026-10-03 Asia/Shanghai; this does not revalidate the historical rate-limit or subscription tables below.

These values are public reference values. Model availability, rate limits, pricing, context windows, and quota rules may change. Confirm production-critical values in the official docs or Agnes Platform console.

## Base URLs

| Use case | Base URL |
| --- | --- |
| International service (primary) | `https://apihub.agnes-ai.com/v1` |
| International service (alternate) | `https://apihub.agnes-ai.cn/v1` |
| China service | `https://api.agnes-ai.cn/v1` |
| International video result polling (2.5 / 2.5 Flash) | `https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>&model_name=<SUBMITTED_MODEL>` |

Use the international alternate route only when the international primary route cannot connect because of a network, DNS, TLS, or timeout issue. Do not change routes to resolve request, authentication, permission, or rate-limit responses. For China service video polling, use the matching service documentation.

## Models

| Model | Type | Endpoint | Use cases |
| --- | --- | --- | --- |
| `agnes-2.5-flash` | Text and vision-language | `/v1/chat/completions` | Chat, coding, reasoning, tools, streaming, image understanding, agent workflows |
| `agnes-image-2.1-flash` | Image generation and editing | `/v1/images/generations` | Higher quality image generation and editing |
| `agnes-video-2.5-flash` | Video generation | `/v1/videos` | Text, keyframe and image/audio-reference modes; use the dedicated current contract |
| `agnes-video-2.5` | Video generation | `/v1/videos` | Text, keyframe and multimodal-reference modes; use the dedicated current contract |

Official video sources: [2.5 Flash](https://wiki.agnes-ai.com/en/docs/agnes-video-25-flash) and [2.5](https://wiki.agnes-ai.com/en/docs/agnes-video-25). Pass the exact submitted model as `model_name` when retrieving tasks. Do not apply the legacy `agnes-video-v2.0` quota column below to these models or select v2.0 by default. Execution limits live in [agnes-generate's contract](../../agnes-generate/references/contracts.md); creative prompting belongs to agnes-video-director.

## Historical Reference Limits (2026-07-30; recheck before use)

| Model type | User type | Public request RPM | Actual executable RPM |
| --- | --- | ---: | ---: |
| Text models | Free / default | 30 | 20 |
| Text models | Enterprise | 60 | 40 |
| Text models | Token Plan | 1,000 | 1,000 |
| Video models | Free / default | 2 | 1 |
| Video models | Enterprise | 2 | 2 |
| Video models | Token Plan | 6 | 5 |

Image model RPM is resolution-specific:

| User type | 1K actual RPM | 2K actual RPM | 3K actual RPM | 4K actual RPM |
| --- | ---: | ---: | ---: | ---: |
| Free / default | 20 | 10 | 1 | 1 |
| Enterprise | 40 | 20 | 1 | 1 |
| Token Plan | 100 | 80 | 1 | 1 |

## Historical Token Plan Quotas (includes legacy v2.0; recheck before use)

| Plan | `agnes-2.5-flash` | `agnes-image-2.1-flash` | `agnes-video-v2.0` |
| --- | --- | --- | --- |
| Starter | 1,500 requests per 5 hours; 15,000 requests per week | 4,000 images per day | 500 seconds per day |
| Plus | 7,500 requests per 5 hours; 75,000 requests per week | 4,000 images per day | 500 seconds per day |
| Pro | 30,000 requests per 5 hours; 300,000 requests per week | 4,000 images per day | 500 seconds per day |

Token Plan users are subject to both RPM limits and subscription quotas.
