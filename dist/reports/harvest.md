# Harvest report (S3)

Built from the cache under `data/raw/` only; rebuild offline with `python py/step_harvest.py --report`.

## Zenodo

- records referenced in content/: 212
- cached: 198
- not available: 14

| Record | Status | Used in |
|---|---|---|
| 10774878 | 410 | 6(3) #2 |
| 13332508 | 404 | 6(4) #9 |
| 13734161 | 404 | 6(4) #10 |
| 13734380 | 404 | 6(4) #11 |
| 13803736 | 404 | 6(4) #15 |
| 13803957 | 404 | 6(4) #16 |
| 15039154 | 404 | 7(1) λ2 |
| 15332813 | 404 | 7(3) λ11 |
| 15332827 | 404 | 7(3) λ12 |
| 15332866 | 404 | 7(3) λ13 |
| 15332910 | 404 | 7(3) λ14 |
| 15332927 | 404 | 7(3) λ15 |
| 18901062 | 404 | 8(3) §7 |
| 18901176 | 404 | 8(3) §8 |

### Title check

Entries whose title in content/ differs clearly from the Zenodo title (similarity < 0.6) - the usual sign of a DOI copied from a neighbouring entry.

| Record | Used in | Similarity | content/ | Zenodo |
|---|---|---|---|---|
| 2540522 | 1(3) #4 | 0.34 | The Labeling System - A New Approach to Overcome the Vocabulary Bottleneck | Linking periods: Modeling and utilizing spatio-temporal concepts in the chronOntology project |
| 7337817 | 4(1) #5 | 0.58 | Software Review for the Software PointSamplingTool (Archäologische Informationen 44, Early View, published online 18 Nov 2022) | Software Review for the Software PointSamplingTool |
| 8190763 | 5(2) #5 | 0.53 | SPARQL Unicorn Ontology Documentation | sparqlunicorn/sparqlunicornGoesGIS-ontdoc: Version 0.17 |
| 10260778 | 5(3) #6 | 0.05 | Semantic Modelling using LOD techniques of Uncertainty, Vagueness and Ambiguities in the Archaeological Domain | Sharing (Linked) Open Data with domain-specific data-driven community hubs on the example of the German National Research Data Infrastructure (NFDI) consortium NFDI4Objects and the data hub archaeology.link |
| 10260778 | 5(5) #4 | 0.05 | Semantic Modelling using LOD techniques of Uncertainty, Vagueness and Ambiguities in the Archaeological Domain | Sharing (Linked) Open Data with domain-specific data-driven community hubs on the example of the German National Research Data Infrastructure (NFDI) consortium NFDI4Objects and the data hub archaeology.link |
| 10369624 | 5(2) #4 | 0.35 | Croton Geo Locations | Research-Squirrel-Engineers/croton-geo: v0.1 |
| 10780476 | 6(2) #2 | 0.53 | SPARQL Unicorn Ontology Documentation | sparqlunicorn/sparqlunicornGoesGIS-ontdoc: Version 0.17 |
| 13897159 | 6(4) #17 | 0.34 | Interdisziplinäre Knowledge Graphen? Wieso man eine gemeinsame Object-Ontologie und ein Minimal-Metadatenset benötigt, um FDM in einem Knowledge Graphen zum Leben zu erwecken | Digitale Services in der Archäologie Aktuelle Entwicklungen und Angebote aus den NFDI4Objects Arbeitsbereichen Collecting und Protecting |
| 14893860 | 7(4) λ2 | 0.54 | NFDI4Objects TWG - N4O ObjectMetaDataSet (N4O OMDS) & N4O ObjectOntology (N4O OO) | NFDI4Objects TWG – Object Core Metadata Profile (OCMDP) & Material Cultural Heritage Crosswalk Ontology (MaCHeCO) |
| 14906708 | 7(2) λ2 | 0.35 | GrapHNR2023 - Supplementary Material | Supplementary Materials to "Dating Dated Sites: Using Correspondence Analysis to handle Chronologies as Graphs" (leiza-scit/GrapHNR-2023-supplementary-material: v1.0) |
| 16875678 | 7(4) λ5 | 0.41 | Brückenbau zwischen LOD und RSE: Von CIDOC CRM bis Jupyter4NFDI - Ein interdisziplinäres federated Knowledge Graph Ecosystem | Brückenbau zwischen LOD und RSE |
| 16931832 | 7(5) 𝒬8 | 0.45 | RDM within Computational Archaeology: The Role of RDM in Archaeological RSE for Data FAIRification while creating FAIR4RS Code | RDM within Computational Archaeology |
| 16931907 | 7(5) 𝒬9 | 0.43 | Distributed Research Data Knowledge Graphs - Challenges of federated queries using the Wikiverse and OpenStreetMap within the NFDI Knowledge Graph Ecosystem | Distributed Research Data Knowledge Graphs |
| 16931909 | 7(5) 𝒬10 | 0.47 | RSE 4 Research Data Infrastructures The Role of Research Software Engineers in creating FAIR Data with FAIR4RS Code | RSE 4 Research Data Infrastructures |
| 18441772 | 8(1) §1 | 0.41 | From Tables to Gazetteers: Reproducible Place Alignment for Archaeological Data with STL-PA | From Packaged Research Artefacts to RDF: A Reference Implementation for FAIR Digital Objects into the Federated Knowledge Graph Ecosystem |

### Shared DOIs

One DOI cited by several entries; at most one of them can be right. Similarity to the Zenodo title is shown for each, whatever its value.

| Record | Zenodo title | Used in | Similarity | content/ |
|---|---|---|---|---|
| 2540522 | Linking periods: Modeling and utilizing spatio-temporal concepts in the chronOntology project | 1(3) #4 | 0.34 | The Labeling System - A New Approach to Overcome the Vocabulary Bottleneck |
| 2540522 | Linking periods: Modeling and utilizing spatio-temporal concepts in the chronOntology project | 1(5) #2 | 1.00 | Linking periods: Modeling and utilizing spatio-temporal concepts in the chronOntology project |
| 5642976 | African Red Slip Ware Digital (ARS3D) - How to create a Feature? | 3(1) #4 | 1.00 | African Red Slip Ware Digital (ARS3D) - How to create a Feature? |
| 5642976 | African Red Slip Ware Digital (ARS3D) - How to create a Feature? | 3(1) #12 | 0.71 | African Red Slip Ware Digital (ARS3D) - Comparison Videos |
| 10260778 | Sharing (Linked) Open Data with domain-specific data-driven community hubs on the example of the German National Research Data Infrastructure (NFDI) consortium NFDI4Objects and the data hub archaeology.link | 5(3) #6 | 0.05 | Semantic Modelling using LOD techniques of Uncertainty, Vagueness and Ambiguities in the Archaeological Domain |
| 10260778 | Sharing (Linked) Open Data with domain-specific data-driven community hubs on the example of the German National Research Data Infrastructure (NFDI) consortium NFDI4Objects and the data hub archaeology.link | 5(5) #4 | 0.05 | Semantic Modelling using LOD techniques of Uncertainty, Vagueness and Ambiguities in the Archaeological Domain |
| 18441772 | From Packaged Research Artefacts to RDF: A Reference Implementation for FAIR Digital Objects into the Federated Knowledge Graph Ecosystem | 8(1) §1 | 0.41 | From Tables to Gazetteers: Reproducible Place Alignment for Archaeological Data with STL-PA |
| 18441772 | From Packaged Research Artefacts to RDF: A Reference Implementation for FAIR Digital Objects into the Federated Knowledge Graph Ecosystem | 8(1) §4 | 1.00 | From Packaged Research Artefacts to RDF: A Reference Implementation for FAIR Digital Objects into the Federated Knowledge Graph Ecosystem |

### Other observations

- records without a PDF file (no preview possible): 39 — 2540709, 3786814, 4305708, 4305709, 4314355, 4765603, 4765604, 4849646, 5642750, 5642891, 5645179, 5645236, 5645253, 5647827, 5647864, 5722941, 5767082, 5767083, 5779053, 7143094, 7143098, 7353771, 7377740, 8190763, 10361309, 10362777, 10369624, 10779466, 10780476, 11064284, 11064526, 13828632, 14874994, 14906708, 15095413, 15477358, 15721469, 18404885, 18901448
- cited by concept DOI (Zenodo answers with the latest version): 169 — 775019 -> 292975, 1200111 -> 1202168, 1293990 -> 1293991, 1402509 -> 1402510, 1410516 -> 1410517, 1421690 -> 1421691, 1469298 -> 1469299, 1494175 -> 1494176, 2222237 -> 2222238, 2540228 -> 2540229, 2540373 -> 2540374, 2540477 -> 2540478, 2540522 -> 2540523, 2540530 -> 2540531, 2540709 -> 11064526, 2620929 -> 2620930, 2629595 -> 2635487, 2635490 -> 2635491, 2643469 -> 2643470, 2648202 -> 2648216, 2648210 -> 2648217, 3237306 -> 3237307, 3252392 -> 3252393, 3403029 -> 3403030, 3403057 -> 3403058, 3471404 -> 3471932, 3567911 -> 3567912, 3567928 -> 3567929, 3688792 -> 3688793, 3719127 -> 3719128, 3742185 -> 3742186, 3786814 -> 17987883, 4305708 -> 13832255, 4765603 -> 4849646, 5642750 -> 5642751, 5642891 -> 5642892, 5642976 -> 5642977, 5645179 -> 5645180, 5645236 -> 5645237, 5645253 -> 5645254, 5646897 -> 5646898, 5647827 -> 6372679, 5647864 -> 6372674, 5722941 -> 5722942, 5767082 -> 7143098, 5779053 -> 6604565, 5788378 -> 5788379, 5810310 -> 6676192, 5942833 -> 5942834, 6043048 -> 6043049, 6386603 -> 7711130, 6534661 -> 6534662, 6976136 -> 6976137, 6976175 -> 6976176, 6976193 -> 6976194, 6976311 -> 6979739, 7105005 -> 7105006, 7142170 -> 7142171, 7179955 -> 7179956, 7337817 -> 7337818, 7353771 -> 7353772, 7361759 -> 7361760, 7361811 -> 7598649, 7377740 -> 15477358, 7544117 -> 7544118, 7558880 -> 7558881, 7617764 -> 7617765, 7624870 -> 7624871, 7629765 -> 7629766, 7629861 -> 7629862, 7870480 -> 7870481, 7915197 -> 7915198, 7915364 -> 7915365, 8089448 -> 8104046, 8154700 -> 8154701, 8154844 -> 8154845, 8190763 -> 10780476, 8333763 -> 8333764, 8334735 -> 8334736, 8334767 -> 8334768, 10114894 -> 10114895, 10255259 -> 10255260, 10260778 -> 10260779, 10262720 -> 10262721, 10291889 -> 10291890, 10361309 -> 10362227, 10362777 -> 10362778, 10369624 -> 10369625, 10512531 -> 10512532, 10512603 -> 10512604, 10515269 -> 10515270, 10515288 -> 10515289, 10580308 -> 10580309, 10756823 -> 10756824, 10790939 -> 10790940, 10805071 -> 10805072, 10840999 -> 10841000, 10841046 -> 10841047, 10906911 -> 10906912, 10992401 -> 10992402, 13132293 -> 13132294, 13364444 -> 13364445, 13364535 -> 13364536, 13364680 -> 13364681, 13373890 -> 13373891, 13627274 -> 13627275, 13734484 -> 13734485, 13739143 -> 13739144, 13897159 -> 13897160, 13897231 -> 13897232, 13927753 -> 13927754, 13980905 -> 13980906, 13980966 -> 13980967, 14017594 -> 14017595, 14055698 -> 14055699, 14055804 -> 14055805, 14055855 -> 14055856, 14130517 -> 14130518, 14167106 -> 14167107, 14217957 -> 14217958, 14524577 -> 14524578, 14524614 -> 14524615, 14707872 -> 14707873, 14789260 -> 14789261, 14789264 -> 14789265, 14886032 -> 14886033, 14893826 -> 14893827, 14893860 -> 17159183, 14898291 -> 14898292, 14898391 -> 14898392, 14906708 -> 14906709, 14914287 -> 14925718, 14914309 -> 14914310, 14916966 -> 14916967, 14920034 -> 14920035, 14976365 -> 14976366, 15040308 -> 15040309, 15065874 -> 15065875, 15074382 -> 15074383, 15310723 -> 15310724, 15401536 -> 15401537, 15667685 -> 15667686, 15721469 -> 15721470, 15721553 -> 15721554, 16353592 -> 16353593, 16735267 -> 16735268, 16735847 -> 16735848, 16736041 -> 16736042, 16736047 -> 16736048, 16736077 -> 16736078, 16736089 -> 16736090, 16736221 -> 16736222, 16875678 -> 16875679, 16931832 -> 16931833, 16931907 -> 16931908, 16931909 -> 16931910, 17150583 -> 17150584, 17475014 -> 17475015, 18404885 -> 22676190, 18441001 -> 18441002, 18441544 -> 18441545, 18441772 -> 18441773, 18726192 -> 18726193, 18726246 -> 18726247, 18803485 -> 18803486, 18803727 -> 18803728, 18803954 -> 18803955, 18826868 -> 18885415, 19200628 -> 19200629

## Places

- places in `content/places.yaml`: 55, with QID: 52
- QID not found on Wikidata: 0
- QID without coordinates: 0

### Suggestions for places without a QID

| Place | Proposed | Alternatives |
|---|---|---|
| Alte Universität Heidelberg | Q436344 Alte Universität - building in Heidelberg, Karlsruhe Government Region, Bade-Württemberg, Germany (49.411, 8.706) | Q2966 Heidelberg - large city in Baden-Württemberg, Germany (49.409, 8.695); Q20754305 Alte Universität (47.799, 13.042) |
| DBM Bochum, Germany | Q896952 German Mining Museum - museum (51.489, 7.217) | Q2103 Bochum - city in North Rhine-Westphalia, Germany (51.483, 7.217); Q31916839 Bochum (51.480, 7.218) |
| RGK, Frankfurt am Mainz | Q1794 Frankfurt - most populated city of Hesse, Germany (50.111, 8.682) | Q28739191 Römisch-Germanische Kommission des Deutschen Archäologischen Instituts, Bibliothek - library in Germany (50.121, 8.657); Q881481 Frankfurt Main Cemetery - cemetery in Frankfurt am Main, Hesse, Germany (50.136, 8.685) |
