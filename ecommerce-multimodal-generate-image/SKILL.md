---
name: ecommerce.multimodal-generate-image
description: AI-driven image generation and editing tool for creating high-quality product images. Triggered when users ask to generate images, create product pictures, edit photos, text-to-image, image-to-image, replace backgrounds, transform styles, composite products into scenes, swap models, or create any type of AI-generated visual content. Even if the user does not explicitly say "AI image," this skill should be triggered whenever the request involves creating, modifying, or transforming images.
---

# AI Image Generation

This skill guides you on how to generate and edit images using the AI image generation service, helping users create high-quality product images, modify existing images, and perform creative visual transformations.

## Core Concepts

The AI Image Generation tool produces new images based on a text prompt and optional reference images. It supports a wide range of use cases:

- **Text-to-image**: Generate a brand-new image purely from a text description.
- **Image-to-image**: Provide one or more reference images and a prompt to generate a new image that preserves elements from the references.
- **Image editing**: Modify specific elements, colors, backgrounds, or styles in an existing image.
- **Product compositing**: Place a product from one image into a scene from another image.
- **Model swapping**: Replace the model or mannequin in a product photo.

**Reference images are strongly recommended** when the user wants the output to closely resemble an existing product or scene. Up to 3 reference image URLs can be provided, separated by commas.

## Parameter Guide

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| prompt | Yes | Text description of the desired image. Supports text-to-image, image-to-image, editing, model swapping, and more. Max 1000 characters. | -- |
| referenceImageUrl | No | URL(s) of reference image(s). Separate multiple URLs with commas. Up to 3 images supported. Max 1000 characters. | -- |
| aspectRatio | No | Aspect ratio of the output image. | 1:1 |

### Supported Aspect Ratios

| Value | Description |
|-------|-------------|
| 1:1 | Square (default) |
| 3:4 | Portrait |
| 4:3 | Landscape |
| 9:16 | Vertical fullscreen |
| 16:9 | Horizontal fullscreen |

### Prompt Writing Tips

1. **Be specific and descriptive**: Clearly describe the subject, scene, lighting, style, and mood you want.
2. **Reference images by number**: When using reference images, refer to them as "image 1," "image 2," etc., in the order they appear in `referenceImageUrl`.
3. **State the operation explicitly**: Use clear action verbs like "replace," "change," "put," "combine," "generate."
4. **Keep within 1000 characters**: Prompts have a maximum length of 1000 characters.

### Prompt Examples by Scenario

**Object replacement**:
```
Replace the vase on the table in image 1 with a potted plant
```

**Background color change**:
```
Change the background color of image 1 to pure white
```

**Product compositing**:
```
Place the product from image 2 onto the marble countertop in image 1
```

**Style transfer**:
```
Transform image 1 into the artistic style shown in image 2
```

**Text-to-image (no reference)**:
```
A professional product photo of a sleek black wireless headphone on a gradient blue background, studio lighting, 8K quality
```

**Model swapping**:
```
Replace the model in image 1 with a different model while keeping the same clothing and pose
```

## Usage

- **API Endpoint**: `POST /multimodal/generateImage` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/multimodal_generate_image.py '<JSON parameters>'`

**Output strategy (script default behavior)**:
- Prints the full JSON response to stdout

**Data reading tip**: Use `jq` or `ConvertFrom-Json` to extract specific fields from the response as needed.

## Display Rules

1. **Show the generated image**: When the response contains image content in the `text` field, display it directly to the user using markdown image syntax.
2. **Status reporting**: Check the `status` and `finished` fields. If image generation is still in progress, inform the user and advise waiting.
3. **Prompt transparency**: Briefly describe what prompt and parameters were sent so the user understands what was requested.
4. **Aspect ratio confirmation**: If the user does not specify dimensions, use the default 1:1 ratio but mention it so they can request a different ratio if needed.
5. **Reference image guidance**: If the user wants a result close to an existing image but did not provide a reference URL, proactively suggest they provide one for better fidelity.
6. **Error handling**: When generation fails, explain the issue based on the response `status` field and suggest adjustments (e.g., simplify the prompt, check reference image URLs, try a different aspect ratio).

## Important Limitations

- **Reference image limit**: A maximum of 3 reference image URLs can be provided per request.
- **Prompt length**: The prompt must not exceed 1000 characters.
- **URL validity**: Reference image URLs must be publicly accessible. Private or expired URLs will cause failures.
- **Aspect ratio options**: Only 1:1, 3:4, 4:3, 9:16, and 16:9 are supported.

## User Expression & Scenario Quick Reference

**Applicable** -- Requests involving image generation or editing:

| User Says | Scenario |
|-----------|----------|
| "Generate an image," "Create a picture" | Text-to-image generation |
| "Edit this photo," "Modify the image" | Image editing |
| "Change the background," "Make it white background" | Background replacement |
| "Put the product on this scene" | Product compositing |
| "Make it look like this style" | Style transfer |
| "Swap the model," "Change the person" | Model swapping |
| "Create a product photo" | Product image generation |
| "Make a vertical/landscape version" | Aspect ratio adjustment |

**Not applicable** -- Needs beyond image generation:

- Image analysis or recognition (reading text from images, identifying objects)
- Video generation or editing
- Image file format conversion
- Batch processing of hundreds of images
- Image hosting or storage

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
