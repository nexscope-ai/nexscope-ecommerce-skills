---
name: ecommerce.tiktok-video-download-url
description: Resolve TikTok video URLs to return no-watermark/watermarked download addresses, playback addresses, and cover image addresses for saving promotional video assets or offline analysis. Trigger when users mention TikTok video download, TikTok watermark-free download, TikTok video save, download TikTok promotional video, TikTok no watermark video, TikTok video download, download TikTok video, no watermark TikTok video, save TikTok video, TikTok video link resolution. Even if the user does not explicitly mention "EchoTik", trigger this skill whenever their need involves extracting downloadable/playable video addresses from a TikTok video link.
---

# EchoTik TikTok Video Download

This skill guides you on how to resolve a TikTok video URL into direct download and playback links, helping sellers save influencer/promotional video assets for offline analysis or reuse.

## Core Concepts

This tool takes a single TikTok video URL and resolves it to direct media addresses: a no-watermark download URL (preferred for clean assets), a watermarked download URL, a playback URL, and cover images (static and dynamic). This is useful when a seller wants to archive a high-performing promotional video found via the product video tool, or reuse a creator's clip without re-recording.

**Required input**: A `url` is mandatory. Two URL formats are accepted:
- Short link: `https://vt.tiktok.com/xxxxxx`
- Full link: `https://www.tiktok.com/@user/video/1234567890`

**Conditional download URLs**: Not every video returns a downloadable address. `noWatermarkDownloadUrl` and `downloadUrl` are returned only when the source video allows it; for some videos (region/privacy/availability restricted) both are absent and only `playUrl` plus cover images come back. Always check presence before presenting a download link, and fall back to `playUrl` for playback when the download fields are missing.

**URL freshness**: The returned download/playback addresses may expire over time. Use them promptly after resolving, and re-resolve if a link stops working.

## Parameter Guide

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| url | string | Yes | TikTok video URL (short link `vt.tiktok.com/xxx` or full link `tiktok.com/@user/video/xxx`). Max length 1000 | - |

## How to Call

- **API Endpoint**: `POST /echotik/getVideoDownloadUrl` (see `references/api.md` for full parameters/response/error codes)
- **Python Script**: `python scripts/echotik_get_video_download_url.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-echotik-get-video-download-url-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Usage Examples

**1. Resolve a full TikTok video link**
```json
{
  "url": "https://www.tiktok.com/@user/video/1234567890"
}
```

**2. Resolve a TikTok short link**
```json
{
  "url": "https://vt.tiktok.com/Z123abc/"
}
```

## Display Rules

1. **Present the no-watermark link first**: When `noWatermarkDownloadUrl` is present, surface it as the primary download option, since clean assets are usually what sellers want
2. **Offer the watermarked variant**: Also list `downloadUrl` (watermarked) when present, in case the user wants the original branding
3. **Handle missing download URLs**: When both `noWatermarkDownloadUrl` and `downloadUrl` are absent (common for some videos), do not fabricate a download link -- tell the user the video has no direct download address and offer `playUrl` for playback/preview instead
4. **Provide playback + cover**: Mention `playUrl` for quick preview and `coverUrl` / `dynamicCoverUrl` for thumbnails
5. **Freshness caveat**: Remind the user that the resolved URLs may expire and should be downloaded promptly
6. **Present data only**: Show the resolved addresses clearly without subjective advice on how to use the video
7. **Error handling**: When resolution fails, explain the reason based on `errcode`/`errmsg` -- `400` means a missing/invalid `url`, `10000` means the link is not a valid/accessible TikTok video; suggest checking the URL format

## User Expression & Scenario Quick Reference

### Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Download this TikTok video" / "Save this TikTok clip" | Resolve a video URL into download links |
| "Get the no-watermark version of this TikTok video" | Prioritize `noWatermarkDownloadUrl` |
| "I want to save this influencer's promo video" | Resolve and archive a creator's video |
| "Give me a playable link for this TikTok video" | Return `playUrl` |
| "Get the cover/thumbnail of this TikTok video" | Return `coverUrl` / `dynamicCoverUrl` |

### Not Applicable Scenarios

- Listing promotional videos associated with a TikTok **product** (use the product video skill instead -- it needs a `productId`, not a video URL)
- Searching for TikTok products (use the product search skill)
- TikTok new product rankings (use the new product rank skill)
- TikTok live-stream data
- Video editing or content creation advice
- Non-TikTok platform video downloads

### Boundary Judgment

When users mention "TikTok video", determine whether they already have a **specific video URL** they want to download (this skill) or want to **discover videos linked to a product** (the product video skill). If the user provides a `tiktok.com` or `vt.tiktok.com` link and asks to save/download/extract it, this skill applies. If they mention a product ID and ask "what videos promote this product", use the product video skill instead.
