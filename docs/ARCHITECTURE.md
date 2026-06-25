# Architecture

This repository deliberately separates **camera data engineering** from
**radiance-field training**.

## Layers

```text
Layer 1: raw acquisition
  - DISC3D images
  - CamPos.txt
  - Metashape XML
  - scan information PDF or text metadata

Layer 2: UCDS
  - normalized JSON records
  - explicit intrinsics
  - explicit extrinsics
  - stable coordinate notes

Layer 3: exporters
  - COLMAP TXT
  - Nerfstudio transforms.json
  - future trainer-specific formats

Layer 4: experiments
  - external repository
  - disposable trainer commands
  - benchmark metrics
```

## Design rule

Do not import a Gaussian Splatting trainer into this repository.

The camera representation should remain usable even if a trainer package
changes CLI flags, data parsers, or output directory conventions.
