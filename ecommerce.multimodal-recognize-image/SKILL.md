---
name: ecommerce.multimodal-recognize-image
description: Analyze and extract information from images using multimodal AI recognition. Triggered when users want to analyze, describe, or extract information from an image URL — image recognition, image analysis, image description, visual content understanding, OCR text recognition, or visual Q&A. When a user provides an image URL and asks questions about its visual content, this skill should be triggered even if they do not explicitly say "image recognition."
---

# Image Recognition

This skill guides you on how to use the multimodal image recognition API to analyze images from URLs and extract meaningful information based on user intent.

## Core Concepts

The Image Recognition tool accepts an image URL and an optional natural-language requirement describing what the user wants to know about the image. The backend uses a multimodal AI model to interpret the visual content and return a textual description or analysis.

**Supported formats**: JPG, JPEG, PNG, GIF, WebP, BMP.

**How it works**: You provide a publicly accessible image URL and a requirement (what you want to learn from the image). The service downloads the image, runs multimodal analysis, and returns a text-based result.

## Parameter Guide

| Parameter | Required | Description |
|-----------|----------|-------------|
| imageUrl | Yes | A publicly accessible URL pointing to the image. Must be JPG, JPEG, PNG, GIF, WebP, or BMP. Maximum 1000 characters. |
| requirement | No | A natural-language description of what to identify or analyze in the image. Defaults to "Describe the content of this image" when omitted. Maximum 1000 characters. |

### Tips for Writing the requirement Parameter

1. **Be specific**: Instead of "analyze this image," say "List all products visible on the shelf and estimate their category."
2. **State the goal**: If you need text extraction, say "Extract all visible text from the image." If you need object identification, say "Identify the main objects and their colors."
3. **Provide context when helpful**: For product images, mention "This is an e-commerce product listing image" so the model can tailor its analysis.

## Usage Examples

**1. General Image Description**
- User says: "What is in this picture?"
- Set `imageUrl` to the provided URL, leave `requirement` as default.

**2. Product Image Analysis**
- User says: "Analyze this Amazon product image and list the key selling points shown."
- Set `requirement` to: "This is an Amazon product listing image. Identify the product, key features, and selling points visible in the image."

**3. Text Extraction from an Image**
- User says: "Read the text in this screenshot."
- Set `requirement` to: "Extract all visible text from this image, preserving layout where possible."

**4. A+ Page Image Review**
- User says: "Describe what this A+ content image communicates."
- Set `requirement` to: "This is an Amazon A+ product description image. Describe the visual content, key messaging, and branding elements."

**5. Comparison / Detail Inspection**
- User says: "What differences can you spot between the product and its packaging?"
- Set `requirement` to: "Identify and describe any differences between the product and its packaging shown in the image."

## Usage

- **API Endpoint**: `POST /multimodal/recognizeImage` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/multimodal_recognize_image.py '<JSON parameters>'`

**Output strategy (script default behavior)**:
- Prints the full JSON response to stdout

**Data reading tip**: Use `jq` or `ConvertFrom-Json` to extract specific fields from the response as needed.

## Display Rules

1. **Show the analysis result clearly**: Present the returned text analysis in a readable format. Use bullet points or paragraphs as appropriate for the content.
2. **No fabrication**: Only relay information that the API actually returned. Do not add visual details that were not in the response.
3. **Format support**: If the image URL is invalid or the format is unsupported, explain the limitation and list the supported formats (JPG, JPEG, PNG, GIF, WebP, BMP).
4. **Error handling**: When the API returns an error status, explain the issue based on the response and suggest corrective actions (e.g., check that the URL is publicly accessible, verify the image format).
5. **Cost transparency**: If the user asks about cost, you may mention the `costToken` value from the response.

## User Expression & Scenario Quick Reference

**Applicable** -- Image analysis tasks:

| User Says | Scenario |
|-----------|----------|
| "What's in this image/picture/photo" | General image description |
| "Analyze this product image" | Product visual analysis |
| "Read the text in this image" | OCR / text extraction |
| "Describe the A+ page images" | E-commerce content review |
| "What does this screenshot show" | Screenshot interpretation |
| "Identify objects in this photo" | Object detection / listing |

**Not applicable** -- Needs beyond image recognition:

- Generating or editing images
- Video analysis
- Image search or reverse image lookup

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
