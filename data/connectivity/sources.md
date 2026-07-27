# Sources and References

## 1. ENIGMA Toolbox — Structural Connectivity (DK Atlas, HCP)

- **Toolbox**: Lariviere S, et al. (2021). The ENIGMA Toolbox: multiscale neural contextualization of multisite neuroimaging datasets. *Nature Methods*, 18:698-700. doi:10.1038/s41592-021-01186-6
- **Documentation**: https://enigma-toolbox.readthedocs.io/en/stable/pages/05.HCP/index.html
- **GitHub**: https://github.com/MICA-MNI/ENIGMA
- **Methodology Paper**: Lariviere S, et al. (2020). The ENIGMA Toolbox: multiscale neural contextualization of multisite neuroimaging datasets. *bioRxiv* 2020.12.21.423838. doi:10.1101/2020.12.21.423838
- **HCP Data Reference**: Van Essen DC, et al. (2013). The WU-Minn Human Connectome Project: an overview. *NeuroImage*, 80:62-79.

### Alternative HCP Structural Connectome Source (R package)

- **dTBM Package**: Hu J, Wang M (2023). dTBM: Multi-Way Spherical Clustering via Degree-Corrected Tensor Block Models. R package version 3.0. CRAN.
- Contains binary 68x68x136 tensor of DK-parcellated HCP structural connectivity.
- https://search.r-project.org/CRAN/refmans/dTBM/html/HCP.html

## 2. Yeo 7-Network Parcellation and DK Mapping

- **Original Yeo 7-Network Paper**: Yeo BT, Krienen FM, Sepulcre J, Sabuncu MR, Lashkari D, Hollinshead M, Roffman JL, Smoller JW, Zöllei L, Polimeni JR, Fischl B, Liu H, Buckner RL (2011). The organization of the human cerebral cortex estimated by intrinsic functional connectivity. *Journal of Neurophysiology*, 106(3):1125-1165. PMID: 21653723. doi:10.1152/jn.00338.2011
- **FreeSurfer Download**: ftp://surfer.nmr.mgh.harvard.edu/pub/data/Yeo_JNeurophysiol11_FreeSurfer.zip
- **FreeSurfer Wiki**: https://surfer.nmr.mgh.harvard.edu/fswiki/CorticalParcellation_Yeo2011

### DK-to-Yeo Overlap Data Sources

- **Park et al. (2022)**: Park BY, et al. (2022). Remapping the Yeo-7 parcellation to DK subparcellation. *PNAS*, 119(36):e2116673119. doi:10.1073/pnas.2116673119
- **Table 2 (PMC11480971)**: Published DK-to-Yeo assignments for DMN and FPN regions. https://pmc.ncbi.nlm.nih.gov/articles/PMC11480971/
- **Lim et al. (2019)**: Lim S, et al. (2019). 68-region DK atlas with Yeo 7 subnetworks for multiplex network analysis. *Scientific Reports*, 9:6393555. doi:10.1038/s41598-019-39243-x
- **OQS (OHBM) Overlap Data**: Percentage overlap mapping between DK parcels and Yeo networks (partial data). https://ohbm.github.io/

### Tools for Computing Full Mapping

- **FreeSurfer**: Overlay Yeo2011_7Networks_N1000.annot on aparc.annot, majority vote per DK region.
- **AFNI**: https://afni.nimh.nih.gov/
- **PANDA**: https://www.nitrc.org/projects/panda/
- **R brainGraph package**: https://rdrr.io/cran/brainGraph/ (Yeo labels available for Brainnetome, not DK directly)
- **Python osl-dynamics**: https://osl-dynamics.readthedocs.io/en/latest/parcellations/dk68.html (DK68 coordinates, no Yeo labels)

## 3. Kroell / Dugré & Potvin — Functional Networks

### Kroell et al. (2024) — 14 Functional Networks

- **Manuscript**: Kroell JP, Eickhoff SB, et al. (2024). Definition of 14 canonical functional networks from meta-analytic coactivation data. Research Centre Juelich (INM-1).
- **Juelich Record**: https://juser.fz-juelich.de/record/1006698/files/Manuscript_Kroell.pdf

### Dugré & Potvin (2023/2024) — 13 Co-Activation Networks

- **Preprint**: Dugré JR, Potvin S (2023). Towards a Neurobiologically-driven Ontology of Mental Functions: A Data-driven Summary of the Twenty Years of Neuroimaging Meta-Analyses. *bioRxiv* 2023.03.29.534795. doi:10.1101/2023.03.29.534795
- **Full Text**: https://www.biorxiv.org/content/10.1101/2023.03.29.534795v1
- **NeuroVault Collection**: https://www.neurovault.org/collections/13769/

### Kröll & Eickhoff (2024) — Test-Retest Reliability

- **Preprint**: Kröll JP, Eickhoff SB, Weis S, et al. (2024). Test-Retest Reliability of Meta Analytic Networks During Naturalistic Viewing. *bioRxiv* 2024.05.15.594266. doi:10.1101/2024.05.15.594266
- https://www.biorxiv.org/content/10.1101/2024.05.15.594266v1

### Component Networks Referenced by Kroell

- **Extended Multiple Demand (eMDN)**: Camilleri JA, et al. (2016). Definition and characterization of an extended social-affective default network. *NeuroImage*, 127:420-432.
- **Extended Socio-Affective Default (eSAD)**: Amft M, et al. (2015). Definition and characterization of an extended social-affective default network. *Brain Structure & Function*, 220:1031-1049.
- **Semantic Memory**: Binder JR, et al. (2009). Where is the semantic system? A critical review and meta-analysis of 120 functional neuroimaging studies. *Cerebral Cortex*, 19(12):2767-2796.
- **Theory of Mind / Mentalizing**: Schurz M, et al. (2021). Toward a hierarchical model of social cognition: A neuroimaging meta-analysis and integrative review of empathy and theory of mind. *Psychological Bulletin*, 147(3):293-327.
- **Autobiographical Memory**: Spreng RN, Mar RA, Kim AS (2008). The common neural basis of autobiographical memory, prospection, navigation, theory of mind, and the default mode: a quantitative meta-analysis. *Journal of Cognitive Neuroscience*, 21(3):489-510.

## 4. White Matter Tracts

### Major References

- **Catani M, Thiebaut de Schotten M** (2008). A diffusion tensor imaging tractography atlas for virtual in vivo dissections. *Cortex*, 44(8):1105-1132. doi:10.1016/j.cortex.2008.05.004
- **Catani M, Thiebaut de Schotten M** (2012). *Atlas of Human Brain Connections*. Oxford University Press. ISBN: 9780199541164
- **Wakana S, et al.** (2007). Reproducibility of quantitative tractography methods applied to cerebral white matter. *NeuroImage*, 36(3):630-644.
- **Mori S, et al.** (2005). *MRI Atlas of Human White Matter*. 2nd Edition. Elsevier.
- **Yeh FC, et al.** (2018). Population-averaged atlas of the macroscale human structural connectome and its network topology. *NeuroImage*, 178:57-68. doi:10.1016/j.neuroimage.2018.05.027

### Review Articles

- **Table 1 (PMC11392420)**: White matter tracts in aging and disease. https://pmc.ncbi.nlm.nih.gov/articles/PMC11392420/
- **Table 1 (PMC8247240)**: Association fiber tracts. https://pmc.ncbi.nlm.nih.gov/articles/PMC8247240/
- **Table 2 (PMC7318131)**: Fiber pathways. https://pmc.ncbi.nlm.nih.gov/articles/PMC7318131/
- **Table 4 (Nature 2024)**: 73 anatomical fiber tracts. https://www.nature.com/articles/s41597-024-03058-w

### Clinical References

- **O'Donnell LJ** (Thesis). White matter tract anatomy. https://www.na-mic.org/w/img_auth.php/9/9c/LaurenODonnellThesis.pdf
- **Kartum TA, et al.** (2023). White matter tract segmentation. https://pmc.ncbi.nlm.nih.gov/articles/PMC10363610/

## 5. Desikan-Killiany Atlas

- **Original Paper**: Desikan RS, Ségonne F, Fischl B, et al. (2006). An automated labeling system for subdividing the human cerebral cortex on MRI scans into gyral based regions of interest. *NeuroImage*, 31(3):968-980. doi:10.1016/j.neuroimage.2006.01.021

### DK Atlas Resources

- **FreeSurfer**: https://surfer.nmr.mgh.harvard.edu/ (built-in aparc.annot)
- **OSL Dynamics DK68**: https://osl-dynamics.readthedocs.io/en/latest/parcellations/dk68.html (MNI coordinates for 68 DK regions)
- **ggseg R package**: https://ggseg.r-universe.dev/ (visualization of DK atlas)
- **brainGraph R package**: https://search.r-project.org/CRAN/refmans/brainGraph/ (DK atlas coordinates)
- **ResearchGate Table**: https://www.researchgate.net/figure/Regions-in-the-Desikan-Killiany-DK-atlas_tbl2_348518431
