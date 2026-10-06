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
| 817469 | 1(6) #2 | 0.28 | Avalanches on Atlantis - Real or Fake? The "true" story! | D2.1 - Semantics for IoT and Cloud resources |
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

### Other observations

- records without a PDF file (no preview possible): 39 — 2540709, 3786814, 4305708, 4305709, 4314355, 4765603, 4765604, 4849646, 5642750, 5642891, 5645179, 5645236, 5645253, 5647827, 5647864, 5722941, 5767082, 5767083, 5779053, 7143094, 7143098, 7353771, 7377740, 8190763, 10361309, 10362777, 10369624, 10779466, 10780476, 11064284, 11064526, 13828632, 14874994, 14906708, 15095413, 15477358, 15721469, 18404885, 18901448
- answered with a different record id (concept DOI -> latest version): 169 — 775019 -> 292975, 1200111 -> 1202168, 1293990 -> 1293991, 1402509 -> 1402510, 1410516 -> 1410517, 1421690 -> 1421691, 1469298 -> 1469299, 1494175 -> 1494176, 2222237 -> 2222238, 2540228 -> 2540229, 2540373 -> 2540374, 2540477 -> 2540478, 2540522 -> 2540523, 2540530 -> 2540531, 2540709 -> 11064526, 2620929 -> 2620930, 2629595 -> 2635487, 2635490 -> 2635491, 2643469 -> 2643470, 2648202 -> 2648216, 2648210 -> 2648217, 3237306 -> 3237307, 3252392 -> 3252393, 3403029 -> 3403030, 3403057 -> 3403058, 3471404 -> 3471932, 3567911 -> 3567912, 3567928 -> 3567929, 3688792 -> 3688793, 3719127 -> 3719128, 3742185 -> 3742186, 3786814 -> 17987883, 4305708 -> 13832255, 4765603 -> 4849646, 5642750 -> 5642751, 5642891 -> 5642892, 5642976 -> 5642977, 5645179 -> 5645180, 5645236 -> 5645237, 5645253 -> 5645254, 5646897 -> 5646898, 5647827 -> 6372679, 5647864 -> 6372674, 5722941 -> 5722942, 5767082 -> 7143098, 5779053 -> 6604565, 5788378 -> 5788379, 5810310 -> 6676192, 5942833 -> 5942834, 6043048 -> 6043049, 6386603 -> 7711130, 6534661 -> 6534662, 6976136 -> 6976137, 6976175 -> 6976176, 6976193 -> 6976194, 6976311 -> 6979739, 7105005 -> 7105006, 7142170 -> 7142171, 7179955 -> 7179956, 7337817 -> 7337818, 7353771 -> 7353772, 7361759 -> 7361760, 7361811 -> 7598649, 7377740 -> 15477358, 7544117 -> 7544118, 7558880 -> 7558881, 7617764 -> 7617765, 7624870 -> 7624871, 7629765 -> 7629766, 7629861 -> 7629862, 7870480 -> 7870481, 7915197 -> 7915198, 7915364 -> 7915365, 8089448 -> 8104046, 8154700 -> 8154701, 8154844 -> 8154845, 8190763 -> 10780476, 8333763 -> 8333764, 8334735 -> 8334736, 8334767 -> 8334768, 10114894 -> 10114895, 10255259 -> 10255260, 10260778 -> 10260779, 10262720 -> 10262721, 10291889 -> 10291890, 10361309 -> 10362227, 10362777 -> 10362778, 10369624 -> 10369625, 10512531 -> 10512532, 10512603 -> 10512604, 10515269 -> 10515270, 10515288 -> 10515289, 10580308 -> 10580309, 10756823 -> 10756824, 10790939 -> 10790940, 10805071 -> 10805072, 10840999 -> 10841000, 10841046 -> 10841047, 10906911 -> 10906912, 10992401 -> 10992402, 13132293 -> 13132294, 13364444 -> 13364445, 13364535 -> 13364536, 13364680 -> 13364681, 13373890 -> 13373891, 13627274 -> 13627275, 13734484 -> 13734485, 13739143 -> 13739144, 13897159 -> 13897160, 13897231 -> 13897232, 13927753 -> 13927754, 13980905 -> 13980906, 13980966 -> 13980967, 14017594 -> 14017595, 14055698 -> 14055699, 14055804 -> 14055805, 14055855 -> 14055856, 14130517 -> 14130518, 14167106 -> 14167107, 14217957 -> 14217958, 14524577 -> 14524578, 14524614 -> 14524615, 14707872 -> 14707873, 14789260 -> 14789261, 14789264 -> 14789265, 14886032 -> 14886033, 14893826 -> 14893827, 14893860 -> 17159183, 14898291 -> 14898292, 14898391 -> 14898392, 14906708 -> 14906709, 14914287 -> 14925718, 14914309 -> 14914310, 14916966 -> 14916967, 14920034 -> 14920035, 14976365 -> 14976366, 15040308 -> 15040309, 15065874 -> 15065875, 15074382 -> 15074383, 15310723 -> 15310724, 15401536 -> 15401537, 15667685 -> 15667686, 15721469 -> 15721470, 15721553 -> 15721554, 16353592 -> 16353593, 16735267 -> 16735268, 16735847 -> 16735848, 16736041 -> 16736042, 16736047 -> 16736048, 16736077 -> 16736078, 16736089 -> 16736090, 16736221 -> 16736222, 16875678 -> 16875679, 16931832 -> 16931833, 16931907 -> 16931908, 16931909 -> 16931910, 17150583 -> 17150584, 17475014 -> 17475015, 18404885 -> 22676190, 18441001 -> 18441002, 18441544 -> 18441545, 18441772 -> 18441773, 18726192 -> 18726193, 18726246 -> 18726247, 18803485 -> 18803486, 18803727 -> 18803728, 18803954 -> 18803955, 18826868 -> 18885415, 19200628 -> 19200629

## Places

- places in `content/places.yaml`: 54, with QID: 0
- QID not found on Wikidata: 0
- QID without coordinates: 0

### Suggestions for places without a QID

| Place | Proposed | Alternatives |
|---|---|---|
| Alte Universität Heidelberg | – | – |
| Aula Convegni CAST - Center for Advanced Studies and Technology Campus Universitario Chieti Scalo, Chieti, Italy | Q13138 Chieti - Italian comune (42.351, 14.167) | Q136671488 Chieti (45.073, 7.713); Q16160 Province of Chieti - province of Italy (42.350, 14.167) |
| Barcelona, Spanien | Q1492 Barcelona - city in Catalonia, Spain (41.383, 2.177) | Q28496610 Barcelona - Parliament of Catalonia constituency (41.450, 2.083); Q174114 Barcelona - municipality of the Philippines in the province of Sorsogon (12.869, 124.142) |
| Bordeaux, France | Q1479 Bordeaux - city and commune in Gironde, New Aquitaine, France (44.838, -0.579) | Q1113532 Bordeaux-Saint-Clair - commune in Seine-Maritime, France (49.701, 0.253); Q37492134 Bordeaux - family name |
| Bordeaux, Germany | Q1479 Bordeaux - city and commune in Gironde, New Aquitaine, France (44.838, -0.579) | Q1113532 Bordeaux-Saint-Clair - commune in Seine-Maritime, France (49.701, 0.253); Q37492134 Bordeaux - family name |
| Bournemouth, England | Q170478 Bournemouth - town and civil parish in Bournemouth, Christchurch and Poole, Dorset, England (50.720, -1.880) | Q20989094 Bournemouth - former district in Dorset, England (50.717, -1.883); Q19568 AFC Bournemouth - association football club in Bournemouth, England |
| DBM Bochum, Germany | – | – |
| Deutsches Bergbau-Museum, Bochum, Germany | Q2103 Bochum - city in North Rhine-Westphalia, Germany (51.483, 7.217) | Q31916839 Bochum (51.480, 7.218); Q20170786 U-Bahnhof Deutsches Bergbau-Museum (51.489, 7.214) |
| Dresden, Germany | Q1731 Dresden - capital city of the Free State of Saxony in Germany (51.049, 13.738) | Q206353 Dresden - town in Tennessee, United States (36.284, -88.698); Q653002 Staatliche Kunstsammlungen Dresden - complex of 15 world famous Museums in Dresden, Germany including the Gemäldegalerie Alte Meister, Galerie Neue Meister, and Dresden Castle (51.053, 13.737) |
| Edinburgh, Scotland, UK | Q23436 Edinburgh - capital city of Scotland, UK (55.953, -3.189) | Q68826067 Edinburgh - Scottish parish (55.935, -3.216); Q2379199 City of Edinburgh - council area in Scotland (55.950, -3.193) |
| Fort Collins, USA | Q490732 Fort Collins - city and county seat of Larimer County, Colorado, United States (40.567, -105.083) | Q27554771 Fort Collins - 6th episode of the twentieth season of South Park; Q25205681 Fort Collins - single by Hopsin |
| Fraunhofer FOKUS – Fraunhofer Institute for Open Communication Systems, Berlin, Germany | Q64 Berlin - federated state, capital and largest city of Germany (52.517, 13.383) | Q821199 Berlin - town in Hartford County, Connecticut, United States (41.614, -72.772); Q1452018 Fraunhofer Institute for Open Communication Systems - research center (52.526, 13.314) |
| Georg-August-Universität Göttingen, Germany | Q152838 University of Göttingen - university in the city of Göttingen, Germany (51.534, 9.938) | Q101248032 Georg-August-Universität Göttingen Universitätsmedizin - academic department; Q101247971 Georg-August-Universitat Gottingen Fakultat fur Biologie und Psychologie - academic department |
| Gesellschaft der Freunde des Römisch-Germanischen Zentralmuseums in Mainz e.V. Mainz, Germany | Q1720 Mainz - capital of the federal state Rhineland-Palatinate, Germany (49.999, 8.274) | Q161982 Johannes Gutenberg University Mainz - public university in Mainz, Germany (49.993, 8.242); Q8569 Mainz-Bingen district - district of Rhineland-Palatinate, Germany (49.920, 8.080) |
| Graz, Austria | Q13298 Graz - capital of Styria, Austria (47.071, 15.439) | Q107377751 Graz - family name; Q746517 Grażyna - female given name |
| Hamburg, Germany | Q1055 Hamburg - city and state in the North of Germany (53.550, 10.000) | Q1626 Hamburg-Mitte - district of Hamburg, Germany (53.550, 9.994); Q51974 Hamburger SV - German sports club based in Hamburg, with its largest branch being its football department |
| Heidelberg, Germany | Q2966 Heidelberg - large city in Baden-Württemberg, Germany (49.409, 8.695) | Q1594002 Heidelberg - suburb of Melbourne, Victoria, Australia (-37.752, 145.070); Q1594009 Heidelberg - town in Gauteng province, South Africa (-26.501, 28.358) |
| Historisches Seminar der Universität Münster, Münster, Germany | Q2742 Münster - city in North Rhine-Westphalia, Germany (51.962, 7.626) | Q256895 Münster - municipality of Germany (48.633, 10.900); Q149419 Munster - commune in Haut-Rhin, France (48.041, 7.134) |
| Hochschule für Technik und Wirtschaft, Dresden | Q1731 Dresden - capital city of the Free State of Saxony in Germany (51.049, 13.738) | Q206353 Dresden - town in Tennessee, United States (36.284, -88.698); Q653002 Staatliche Kunstsammlungen Dresden - complex of 15 world famous Museums in Dresden, Germany including the Gemäldegalerie Alte Meister, Galerie Neue Meister, and Dresden Castle (51.053, 13.737) |
| Jade-Hoschschule, Oldenburg | Q2936 Oldenburg - independent city in Lower Saxony, Germany (53.144, 8.214) | Q496435 Oldenburg in Holstein - municipality of Schleswig-Holstein, Germany (54.292, 10.887); Q543350 Oldenburg Central Station - railway station in Oldenburg, Germany (53.144, 8.223) |
| JGU, Mainz Germany | Q1720 Mainz - capital of the federal state Rhineland-Palatinate, Germany (49.999, 8.274) | Q161982 Johannes Gutenberg University Mainz - public university in Mainz, Germany (49.993, 8.242); Q7072154 O.P. Jindal Global (Institution of Eminence Deemed to be University) - state private university in Sonipat, Haryana, India (28.927, 77.056) |
| Johannes Gutenberg Universität Mainz, Fachbereich 07, Klassische Archäologie | Q161982 Johannes Gutenberg University Mainz - public university in Mainz, Germany (49.993, 8.242) | Q101266358 Institute of Physics, Johannes Gutenberg-University Mainz - research institute; Q113861354 Kompetenzteam Forschungsdaten - research data management, Johannes Gutenberg University Mainz |
| Julius-Maximilians-Universität Würzburg | Q161976 University of Würzburg - university in Germany (49.788, 9.935) | Q101267538 Julius-Maximilians-Universität Würzburg Biozentrum - academic department; Q101268750 Julius-Maximilians-Universität Würzburg Medizinische Fakultät - medical school |
| KIT, Karlsruhe | Q1040 Karlsruhe - city in Baden-Württemberg, Germany (49.017, 8.400) | Q663558 German cruiser Karlsruhe - 1927 Königsberg-class cruiser (58.067, 8.067); Q309988 Karlsruhe Institute of Technology - technical university and research center in Karlsruhe, Germany (49.100, 8.432) |
| Kraków, Poland | Q31487 Kraków - capital city of Lesser Poland Voivodeship in southern Poland (50.061, 19.937) | Q536858 Krakow am See - town in Germany (53.650, 12.267); Q1164890 Kraków County - powiat of Poland (50.061, 19.938) |
| Leibniz-Zentrum für Archäologie (LEIZA), Mainz Germany | Q1648056 Leitza - municipality of Spain (43.079, -1.915) | Q115755098 Leibniz-Zentrum für Archäologie - Research institute and museum for archaeology as part of the Leibniz association (49.994, 8.281); Q878029 Römisch-Germanisches Zentralmuseum - archaeological research institute and museum in Mainz (50.006, 8.270) |
| Leibnizhaus, Hannover, Germany | Q1715 Hanover - capital city of the German federated state of Lower Saxony (52.374, 9.739) | Q164079 Kingdom of Hanover - German kingdom established in 1814 (52.367, 9.717); Q1813804 Leibnizhaus - reconstructed residential house in Hannover, Germany (52.371, 9.732) |
| Mainz, Germany | Q1720 Mainz - capital of the federal state Rhineland-Palatinate, Germany (49.999, 8.274) | Q161982 Johannes Gutenberg University Mainz - public university in Mainz, Germany (49.993, 8.242); Q8569 Mainz-Bingen district - district of Rhineland-Palatinate, Germany (49.920, 8.080) |
| Munich, Germany | Q1726 Munich - capital and most populous city of Bavaria, Germany (48.138, 11.575) | Q1053735 Munich Central Collecting Point - depot used by the Monuments, Fine Arts, and Archives program after the end of the Second World War to process, photograph and redistribute artwork and cultural artefacts that had been confiscated by the Nazis and hidden throughout Germany and Austria (48.145, 11.567); Q15789 FC Bayern Munich - association football club in Munich, Germany |
| Paris, France | Q90 Paris - capital and most populous city in France (48.857, 2.352) | Q830149 Paris - city in and county seat of Lamar County, Texas, United States (33.663, -95.548); Q18331346 Paris - family name |
| Polytechnic University of Valencia (Universitat Politècnica de València, UPV) | Q2003976 Technical University of Valencia - university in Spain (39.481, -0.341) | Q8818 Valencia - capital city of the Valencian Community, Spain (39.470, -0.376); Q42023134 Polytechnic University of Valencia open access policy |
| Potsdam, Germany | Q1711 Potsdam - capital city of the German state of Brandenburg (52.401, 13.059) | Q1022943 Potsdam - town in St. Lawrence County, New York, United States (44.670, -74.981); Q647973 Potsdam central station - central railway station in Potsdam, Germany (52.392, 13.067) |
| RGK, Frankfurt am Mainz | Q2529510 Gorno-Altaysk Airport - airport in Russia (51.967, 85.833) | Q7152833 R. G. Kar Medical College and Hospital - Asia's first Private medical school in Kolkata, West Bengal (Now Public) (22.604, 88.378); Q1425831 Deutsches Archäologisches Institut. Römisch-Germanische Kommission - institution |
| RWTH Aachen, C.A.R.L., Aachen, Germany | Q1017 Aachen - city in North Rhine-Westphalia, Germany (50.776, 6.084) | Q273263 RWTH Aachen University - university in Aachen, Germany (50.778, 6.078); Q560144 Klinikum Aachen - university hospital in Aachen, Germany (50.776, 6.044) |
| Sapienza University of Rome, Italy | Q6580 Rome - county seat of Floyd County, Georgia, United States (34.260, -85.185) | Q220 Rome - capital and largest city of Italy (41.893, 12.483); Q209344 Sapienza University of Rome - Italian university founded in Rome in 1303 (41.903, 12.516) |
| Siena, Italy | Q2751 Siena - city in Tuscany, Italy and capital of the province of Siena (43.318, 11.331) | Q20001017 Siena - female given name; Q2756 Siena FC - Italian football club based in Siena, Tuscany |
| Stuttgart, Germany | Q1022 Stuttgart - city on the Neckar river and capital of the federal state Baden-Württemberg, Germany (48.778, 9.180) | Q79844 Stuttgart - city in Arkansas, United States (34.497, -91.551); Q727750 Stuttgart-Mitte - human settlement in Germany (48.777, 9.178) |
| Technische Universität Hamburg (TUHH) | Q1060 Hamburg University of Technology - university in Germany (53.461, 9.970) | Q2496355 University Library of the Hamburg University of Technology - academic library (53.461, 9.969); Q55906115 TUHH Campus-Shop GmbH - company of the student body of the Technical University Hamburg (TUHH) |
| Toscana-Saal der Residenz Würzburg | Q2999 Würzburg - city in the region of Franconia, Northern Bavaria, Germany (49.794, 9.929) | Q10458 Würzburg - rural district in Lower Franconia, Bavaria, Germany (49.660, 10.000); Q161976 University of Würzburg - university in Germany (49.788, 9.935) |
| Tübingen, Germany | Q3806 Tübingen - town in central Baden-Württemberg, Germany (48.520, 9.056) | Q1536443 Tübingen - ship (44.698, 13.916); Q1661161 Index Theologicus - International Bibliography for Theology and Religious Studies and web portal of the Specialised Information Service Theology (48.525, 9.062) |
| Universidad de Barcelona, Spain | Q219615 University of Barcelona - public research university located in Barcelona, Catalonia (41.387, 2.164) | Q20102148 Universitat de l'Estudi General - (1558-1716); Q28444916 Universidad de Barcelona. Centro de Estudios Históricos Internacionales |
| Università di Torino, Italy | Q499911 University of Turin - university in Turin, Italy (45.069, 7.689) |  |
| Universität zu Köln, Köln, Deutschland | Q365 Cologne - most populous city in North Rhine-Westphalia, Germany (50.942, 6.958) | Q54096 University of Cologne - university in Germany (50.928, 6.929); Q105533759 Köln - family name |
| University College Cork (UCC), Cork, Ireland | Q36647 Cork - city in County Cork, Munster Province, Ireland (51.900, -8.473) | Q162475 County Cork - county in Ireland (52.000, -8.750); Q203312 Uccle - municipality in the Brussels-Capital Region, Belgium (50.804, 4.334) |
| University of Glasgow, Glasgow, United Kingdom (Scotland) | Q4093 Glasgow - city in Scotland, United Kingdom (55.861, -4.250) | Q55934339 Glasgow City - council area of Scotland, UK (55.850, -4.250); Q22 Scotland - country in north-west Europe, part of the United Kingdom (57.000, -5.000) |
| University of Stuttgart, Stuttgart | Q1022 Stuttgart - city on the Neckar river and capital of the federal state Baden-Württemberg, Germany (48.778, 9.180) | Q79844 Stuttgart - city in Arkansas, United States (34.497, -91.551); Q122453 University of Stuttgart - German public university (48.782, 9.175) |
| University of Vienna, Austria | Q165980 University of Vienna - public university in Vienna, Austria (48.213, 16.360) | Q55829324 University of Vienna, Institute of Botany Herbarium - herbarium (48.213, 16.360); Q8823198 Category:University of Vienna - Wikimedia category |
| University of West Attica, Athens, Greece | Q203263 Athens - consolidated city-county and county seat of Clarke County, Georgia, United States (33.955, -83.383) | Q79439 Athens - county seat of Limestone County, Alabama, United States (34.792, -86.967); Q1524 Athens - capital and largest city of Greece (37.984, 23.728) |
| Valencia, Spain | Q8818 Valencia - capital city of the Valencian Community, Spain (39.470, -0.376) | Q7026 Catalan - Western Romance language (41.500, 2.000); Q30440696 Valencia - family name |
| Vienna City Hall, Wappensaal, Vienna, Austria | Q686468 Vienna City Hall - town hall of Vienna, Austria (48.211, 16.357) | Q1741 Vienna - capital of and state in Austria (48.208, 16.372); Q1002926 Vienna - town in Fairfax County, Virginia, United States (38.900, -77.267) |
| Warsaw, Poland | Q270 Warsaw - capital and largest city of Poland (52.230, 21.011) | Q992560 Warsaw - city in Indiana, United States (41.241, -85.847); Q37500217 Warsaw - family name |
| Wikimedia Deutschland e.V., Berlin, Germany | Q64 Berlin - federated state, capital and largest city of Germany (52.517, 13.383) | Q821199 Berlin - town in Hartford County, Connecticut, United States (41.614, -72.772); Q8288 Wikimedia Germany - Wikimedia chapter in Germany (52.498, 13.381) |
| Wilhelmshaven, Germany | Q3857 Wilhelmshaven - city in Lower Saxony, Germany (53.529, 8.106) | Q32758817 Wilhelmshaven - Wikimedia permanent duplicate item (53.523, 8.107); Q32067994 Wilhelmshaven - municipality seat (53.570, 8.084) |
| Zagreb, Croatia | Q1435 Zagreb - capital city of Croatia (45.813, 15.977) | Q27038 Zagreb County - county in central Croatia (45.749, 15.571); Q675848 University of Zagreb - Croatian university (45.811, 15.970) |
