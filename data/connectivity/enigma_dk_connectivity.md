# ENIGMA Toolbox: DK-Atlas Structural Connectivity from HCP

## Access Method

The ENIGMA Toolbox (https://enigma-toolbox.readthedocs.io/) provides preprocessed structural
(DTI) and functional (resting-state fMRI) connectivity matrices parcellated to the
Desikan-Killiany (DK) atlas, derived from a cohort of unrelated healthy adults in the
Human Connectome Project (HCP).

### Installation

Standard pip installation may fail (no pre-built wheel). Install from GitHub source:

```bash
git clone https://github.com/MICA-MNI/ENIGMA.git
cd ENIGMA
pip install -e .
```

This has been tested and works with numpy 1.24.3 and scipy 1.10.1.

### Loading Structural Connectivity in Python

```python
from enigmatoolbox.datasets import load_sc
sc_ctx, sc_ctx_labels, sc_sctx, sc_sctx_labels = load_sc()
```

- `sc_ctx`: 68x68 float matrix, cortico-cortical structural connectivity (log-transformed
  streamline counts, distance-dependent thresholded, SIFT2-filtered)
- `sc_ctx_labels`: 68 cortical region labels (34 left, 34 right hemisphere)
- `sc_sctx`: 14x68 float matrix, subcortico-cortical structural connectivity
- `sc_sctx_labels`: 14 subcortical region labels (7 left, 7 right)

DK-subcortical regions: L/R accumbens, amygdala, caudate, hippocampus, pallidum, putamen, thalamus.

A combined matrix can be loaded with `load_sc_as_one()` (82x82: 68 cortical + 14 subcortical).

### Functional Connectivity

```python
from enigmatoolbox.datasets import load_fc
fc_ctx, fc_ctx_labels, fc_sctx, fc_sctx_labels = load_fc()
```

Returns Pearson correlation z-transformed connectivity for the same parcellation.

### Data Summary

| Metric | Value |
|--------|-------|
| Matrix shape (cortico-cortical) | 68 x 68 |
| Number of cortical nodes | 68 (34 LH + 34 RH) |
| Number of subcortical nodes | 14 (7 LH + 7 RH) |
| Edge density (nonzero/total) | ~30.1% |
| Total nonzero edges | 1394 (out of 4624 possible symmetric pairs) |
| Connectivity metric | Log-transformed streamline count |
| Preprocessing | MRtrix3 ACT, CSD, SIFT2, distance-dependent thresholding |
| Source | HCP unrelated healthy adults |

### Saved Data Files

In `/home/dog/game/data/connectivity/`:

- `enigma_sc_ctx_matrix.npy` — 68x68 structural connectivity matrix (numpy binary)
- `enigma_sc_ctx_labels.npy` — 68 cortical labels
- `enigma_sc_sctx_matrix.npy` — 14x68 subcortico-cortical matrix
- `enigma_sc_sctx_labels.npy` — 14 subcortical labels
- `enigma_sc_summary.json` — metadata summary
- `enigma_all_connections.csv` — complete edge list (697 edges, only upper triangle non-zero)
- `enigma_top200_connections.csv` — top 200 strongest connections

### Limitations

- The matrix is a group-average connectome, not individual-subject data
- Binary HCP structural connectome (presence/absence) is also available via the
  R `dTBM` package (`data(HCP)` gives a 68x68x136 binary tensor for 136 individuals)
- The distance-dependent thresholding procedure preserves edge length distributions but
  removes some weak/long-distance connections that may be meaningful

### References

- Lariviere et al. (2021). The ENIGMA Toolbox: multiscale neural contextualization of
  multisite neuroimaging datasets. Nature Methods, 18:698–700.
- ENIGMA Toolbox docs: https://enigma-toolbox.readthedocs.io/en/stable/pages/05.HCP/index.html
- GitHub: https://github.com/MICA-MNI/ENIGMA
- Desikan et al. (2006). An automated labeling system for subdividing the human cerebral
  cortex on MRI scans into gyral based regions of interest. NeuroImage, 31(3):968–980.
