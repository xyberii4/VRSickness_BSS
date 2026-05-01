# VR-Based Beta Sensory Stimulation for Cybersickness Mitigation

**Author:** Jin Xuan Lim  
**Institution:** The University of Bath (BSc Computer Science, 2025-2026)

## Overview

This repository contains the software implementation for a technology development and validation pilot study. The project investigates a novel, non-invasive neuromodulation technique to mitigate cybersickness in Virtual Reality (VR) using an 18Hz random-phase audio-visual flicker.

The repository is divided into two primary components: the **Unity VR Simulation** and the **Data Analysis Pipeline**.

## Repository Structure

```text
├── [Unity Project Root]/       # The core Unity application for Meta Quest 3
│   ├── Assets/
│   │   ├── Scripts/            # Core C# scripts (Stimulation, FMS, Audio routing)
│   │   ├── Shaders/            # HLSL Procedural Noise shader
│   │   └── ...                 # Rollercoaster environment assets
├── data_analysis/              # Python-based statistical and EEG analysis pipeline
└── README.md                   # This file
```

## Acknowledgements

Original Benchmark System: This repository is a fork of the VR Sickness Benchmark System developed by Rouhani et al. (2024).
