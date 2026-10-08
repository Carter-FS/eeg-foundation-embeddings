# eeg-foundation-embeddings

Reusable Docker images for extracting embeddings from raw EDF files using EEG foundation models.

Each model runs in its own container with the CUDA and PyTorch versions it needs. It takes raw EDF files as input and writes Zarr stores with per-window embeddings and a mean-pooled summary.

**Status:** Active

## Supported models

| Model | Embedding dim | CUDA | PyTorch | Source |
| --- | --- | --- | --- | --- |
| LaBraM | 200 | 11.8 | 2.0.1 | [GitHub](https://github.com/935963004/LaBraM) / [braindecode](https://braindecode.org/) |
| REVE | 512 (base) / 1250 (large) | 12.4 | 2.4.0 | [Hugging Face](https://huggingface.co/brain-bzh/reve-base) |
| BENDR | 512 | 11.8 | 2.0.1 | [GitHub](https://github.com/SPOClab-ca/BENDR) / [braindecode](https://huggingface.co/braindecode/braindecode-bendr) |

## Requirements

- Docker with the NVIDIA Container Toolkit (`--gpus` support)
- An NVIDIA GPU with at least 4 GB of VRAM

## Usage

Build the image for a model, then mount a folder of EDF files and an output folder. The input can be a single `.edf` file or a directory, which is searched recursively.

### LaBraM

```sh
docker build -t labram-embeddings -f labram/Dockerfile .

docker run --gpus all \
  -v /path/to/edfs:/data/input \
  -v /path/to/output:/data/output \
  labram-embeddings /data/input /data/output
```

### REVE

REVE is a gated model. Accept its licence at [huggingface.co/brain-bzh/reve-base](https://huggingface.co/brain-bzh/reve-base), then pass your Hugging Face token:

```sh
docker build -t reve-embeddings -f reve/Dockerfile .

docker run --gpus all \
  -e HF_TOKEN=hf_xxx \
  -v /path/to/edfs:/data/input \
  -v /path/to/output:/data/output \
  reve-embeddings /data/input /data/output
```

### BENDR

BENDR uses the 19 standard 10-20 channels plus a relative amplitude channel. Recordings with fewer than 15 matching channels are skipped, and missing channels are zero-filled. The checkpoint is baked into the image at build time, so it needs no token.

```sh
docker build -t bendr-embeddings -f bendr/Dockerfile .

docker run --gpus all \
  -v /path/to/edfs:/data/input \
  -v /path/to/output:/data/output \
  bendr-embeddings /data/input /data/output
```

## Output format

Each EDF file produces one Zarr store:

```
recording.zarr/
  embeddings/        # (n_windows, emb_dim) float32
  padding_mask/      # (n_windows,) bool
  mean_embedding/    # (emb_dim,) float32
  .zattrs            # metadata: model, preprocessing, channels, timestamps
```

## Configuration

Each image reads defaults from its `config.yaml` (`labram/`, `reve/`, `bendr/`). Override them with your own YAML file, command-line flags, or both:

```sh
docker run --gpus all \
  -v /data:/data \
  labram-embeddings --config /data/config.yaml --batch-size 8 /data/input /data/output
```

Run an image with `--help` to list every flag.

## Development

The tests run without a GPU. They need [uv](https://docs.astral.sh/uv/) and Python 3.11 or later.

```sh
uv sync --extra dev
uv run pytest tests/
```

## Licence

The code in this repository is released under the MIT licence (see `LICENSE`). Model weights are downloaded at runtime and are subject to their own licences.
