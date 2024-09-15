# Model Configuration Documentation

This document describes how the 3D model generation is configured and executed using the `run.py` script, along with the crucial `save_gif` function from `utils.py`.

## Overview

The `run.py` script is responsible for processing input images, running the TripoSR model, and generating 3D meshes and renders. It utilizes the TSR (TripoSR) system and various utility functions.

## Key Components

### 1. Imports and Setup

```python
from tsr.system import TSR
from tsr.utils import remove_background, resize_foreground, save_gif
from tsr.bake_texture import bake_texture
```

- The script imports necessary modules, including the TSR system and utility functions.
- A `Timer` class is defined for performance monitoring.

### 2. Command-line Arguments

The script accepts various command-line arguments to configure the model execution:

- `image`: Path to input image(s)
- `device`: Device to use (default: 'cuda:0')
- `pretrained-model-name-or-path`: Path to the pretrained model (default: 'stabilityai/TripoSR')
- `chunk-size`: Evaluation chunk size (default: 8192)
- `mc-resolution`: Marching cubes grid resolution (default: 256)
- `no-remove-bg`: Flag to disable automatic background removal
- `foreground-ratio`: Ratio of foreground size to image size (default: 0.85)
- `output-dir`: Output directory (default: 'output/')
- `model-save-format`: Format to save the extracted mesh (default: 'obj')
- `bake-texture`: Flag to bake a texture atlas
- `texture-resolution`: Texture atlas resolution (default: 2048)
- `render`: Flag to save a NeRF-rendered gif

### 3. Model Initialization

```python
model = TSR.from_pretrained(
    args.pretrained_model_name_or_path,
    config_name="config.yaml",
    weight_name="model.ckpt",
)
model.renderer.set_chunk_size(args.chunk_size)
model.to(device)
```

- The TSR model is initialized with the specified pretrained weights.
- The chunk size for rendering is set.
- The model is moved to the specified device.

### 4. Image Processing

```python
if args.no_remove_bg:
    image = np.array(Image.open(image_path).convert("RGB"))
else:
    image = remove_background(Image.open(image_path), rembg_session)
    image = resize_foreground(image, args.foreground_ratio)
    # ... (additional processing)
```

- Input images are processed, optionally removing the background and resizing the foreground.

### 5. Model Execution

```python
with torch.no_grad():
    scene_codes = model([image], device=device)
```

- The model generates scene codes from the input image.

### 6. Rendering (Optional)

```python
if args.render:
    render_images = model.render(scene_codes, n_views=n_views, return_type="pil")
    for ri, render_image in enumerate(render_images[0]):
        render_image.save(os.path.join(output_dir, f"render_{ri:03d}.png"))
    save_gif(render_images[0], os.path.join(output_dir, f"render.gif"), fps=24)
```

- If the `render` flag is set, the model renders multiple views of the 3D object.
- Individual frames are saved as PNG files.
- A GIF is created using the `save_gif` function from `utils.py`.

### 7. Mesh Extraction

```python
meshes = model.extract_mesh(
    scene_codes, not args.bake_texture, resolution=args.mc_resolution
)
```

- A 3D mesh is extracted from the scene codes using marching cubes.

### 8. Texture Baking (Optional)

```python
if args.bake_texture:
    bake_output = bake_texture(
        meshes[0], model, scene_codes[0], args.texture_resolution
    )
    # ... (export mesh and texture)
else:
    meshes[0].export(out_mesh_path)
```

- If the `bake_texture` flag is set, a texture atlas is baked for the mesh.
- Otherwise, the mesh is exported directly.

## The `save_gif` Function

The `save_gif` function from `utils.py` is crucial for displaying the rendered object. It takes a list of PIL images, an output path, and an optional frame rate (fps) to create an animated GIF of the rendered views.

## Usage

To use this script:

1. Prepare your input image(s).
2. Run the script with desired arguments, e.g.:
   ```
   python run.py input_image.jpg --render --bake-texture
   ```
3. The script will process the image, generate a 3D mesh, and optionally create renders and textures.

## Output

The script generates the following outputs in the specified directory:

- Processed input image (if background removal is applied)
- 3D mesh file (OBJ or GLB format)
- Texture atlas (if texture baking is enabled)
- Rendered PNG frames and GIF (if rendering is enabled)

This configuration allows for flexible 3D model generation from single images, with options for high-quality rendering and texture baking.
