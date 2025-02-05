# Stable Diffusion From Zero

This repository contains a zero-to-hero implementation of the Stable Diffusion model. It includes various components such as:

- **Self-attention mechanisms**: Used for processing sequential and spatial data
- **Variational Autoencoders (VAE)**: For efficient representation learning
- **CLIP Encoder**: A transformer-based encoder for understanding visual content

## File Descriptions

### clip_encoder.ipynb
This notebook contains code for implementing a CLIP (Contrastive Language–Image Preprocessing) encoder. It includes:
- Import statements for PyTorch and its neural network module
- Definition of a self-attention class (`selfAttention`), which is crucial for processing sequence data efficiently

### VAE.ipynb
This notebook focuses on implementing a Variational Autoencoder (VAE). It includes:
- Code for building an encoder-decoder architecture
- Implementation details for training and inference in a VAE framework

### README_gen.py
This script contains the function `generate_readme(directory)` that generates a README.md file. It does the following:
1. Lists all files in a given directory
2. Truncates large content to avoid sending too much data
3. Uses this summarized content to generate a markdown-formatted project description

The README will be used to document and describe these components, their functionalities, and how they work together in the complete implementation of Stable Diffusion from scratch.

