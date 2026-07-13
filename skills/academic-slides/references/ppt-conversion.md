# Phase 4: PPT Conversion(自 SKILL.md 拆出,內容原樣)

## Phase 4: PPT Conversion

When converting PowerPoint files:

### Step 4.1: Extract Content

Use Python with `python-pptx` to extract:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
import json
import os
import base64

def extract_pptx(file_path, output_dir):
    """
    Extract all content from a PowerPoint file.
    Returns a JSON structure with slides, text, images, and equation objects.
    """
    prs = Presentation(file_path)
    frames_data = []

    # Create assets directory.
    assets_dir = os.path.join(output_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)

    for frame_num, slide in enumerate(prs.slides):
        frame_data = {
            'number': frame_num + 1,
            'title': '',
            'content': [],
            'images': [],
            'equations': [],
            'notes': ''
        }

        for shape in slide.shapes:
            # Extract title.
            if shape.has_text_frame:
                if shape == slide.shapes.title:
                    frame_data['title'] = shape.text
                else:
                    frame_data['content'].append({
                        'type': 'text',
                        'content': shape.text
                    })

            # Extract images.
            if shape.shape_type == 13:  # Picture.
                image = shape.image
                image_bytes = image.blob
                image_ext = image.ext
                image_name = f"frame{frame_num + 1}_img{len(frame_data['images']) + 1}.{image_ext}"
                image_path = os.path.join(assets_dir, image_name)

                with open(image_path, 'wb') as f:
                    f.write(image_bytes)

                frame_data['images'].append({
                    'path': f"assets/{image_name}",
                    'width': shape.width,
                    'height': shape.height
                })

            # Detect equation objects (OLE or EMF).
            # PowerPoint equations are often embedded as OLE objects.
            # Flag these for manual KaTeX conversion.
            if hasattr(shape, 'ole_format') or (hasattr(shape, 'image') and shape.image and shape.image.ext == 'emf'):
                frame_data['equations'].append({
                    'type': 'equation_object',
                    'note': 'Detected equation object. Convert to KaTeX manually.'
                })

        # Extract notes.
        if slide.has_notes_slide:
            notes_frame = slide.notes_slide.notes_text_frame
            frame_data['notes'] = notes_frame.text

        frames_data.append(frame_data)

    return frames_data
```

### Step 4.2: Confirm Content Structure

Present the extracted content to the user:

```text
I have extracted the following from your PowerPoint:

**Frame 1: [Title]**
- [Content summary]
- Images: [count]
- Equations detected: [count, if any]

**Frame 2: [Title]**
- [Content summary]
- Images: [count]

...

All images have been saved to the assets folder.
Note: [N] equation objects were detected. These will need manual conversion to KaTeX syntax.

Does this look correct? Should I proceed with theme selection?
```

### Step 4.3: Theme Selection

Proceed to Phase 2 (Style Discovery) with the extracted content in mind.

### Step 4.4: Generate HTML

Convert the extracted content into the chosen theme, preserving:
- All text content
- All images (referenced from assets folder)
- Frame order
- Any speaker notes (as HTML comments or separate file)
- Convert detected equations to KaTeX `$...$` or `$$...$$` syntax where possible

### Step 4.5: Content Quality and Focus

After extraction and confirmation, proceed to:
1. **Phase 0.5** (Essential Content Questions) -- Ask about audience, takeaway, and narrative arc
2. **Phase 1P** (Paper Focus Discovery) -- Ask what aspects of the paper to emphasize and what to skip
3. **Phase 2** (Style Discovery) -- Select theme

Then proceed to Phase 3 (Generate) with all directives applied.

---

