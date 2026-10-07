# RDF report (S7)

- `dist/squirrelpapers.ttl`: 12658 triples
- `dist/squirrelpapers-crm.ttl`: 6185 triples
- `dist/vocab/types.ttl`: 234 triples
- `dist/ontology/sqp.ttl`: 48 triples
- resources with their own `index.ttl` / `index.jsonld`: 259

## Classes (DCAT graph)

| Class | Instances |
|---|---|
| `foaf:Document` | 259 |
| `bibo:Document` | 210 |
| `rdf:Seq` | 210 |
| `dcat:Dataset` | 210 |
| `dcat:Distribution` | 210 |
| `spdx:Checksum` | 162 |
| `foaf:Person` | 106 |
| `schema:Person` | 106 |
| `fabio:Presentation` | 92 |
| `event:Event` | 70 |
| `schema:Event` | 70 |
| `dct:Location` | 51 |
| `geo:Feature` | 51 |
| `geo:Geometry` | 51 |
| `schema:Place` | 51 |
| `dcat:DatasetSeries` | 48 |
| `fabio:JournalIssue` | 40 |
| `fabio:Dataset` | 27 |
| `fabio:ConferencePoster` | 22 |
| `fabio:ComputerProgram` | 21 |
| `fabio:Expression` | 11 |
| `fabio:WorkingPaper` | 10 |
| `fabio:JournalVolume` | 8 |
| `fabio:ProceedingsPaper` | 7 |
| `fabio:JournalArticle` | 6 |
| `dct:LicenseDocument` | 4 |
| `fabio:ConferencePaper` | 4 |
| `fabio:Preprint` | 3 |
| `dct:LinguisticSystem` | 2 |
| `fabio:Abstract` | 2 |
| `fabio:BookChapter` | 2 |
| `fabio:ReportDocument` | 2 |
| `dct:MediaType` | 1 |
| `dct:MediaTypeOrExtent` | 1 |
| `bibo:Periodical` | 1 |
| `fabio:Book` | 1 |
| `fabio:Journal` | 1 |
| `spdx:ChecksumAlgorithm` | 1 |
| `dcat:Catalog` | 1 |
| `foaf:Organization` | 1 |
| `schema:Periodical` | 1 |

## Classes (CRM graph)

| Class | Instances |
|---|---|
| `crm:E52_Time-Span` | 279 |
| `crm:E42_Identifier` | 278 |
| `crm:E73_Information_Object` | 259 |
| `lrmoo:F28_Expression_Creation` | 210 |
| `lrmoo:F2_Expression` | 210 |
| `crm:E35_Title` | 210 |
| `crm:E65_Creation` | 210 |
| `crmdig:D1_Digital_Object` | 162 |
| `crm:E21_Person` | 106 |
| `crm:E41_Appellation` | 70 |
| `crm:E7_Activity` | 70 |
| `crm:E53_Place` | 51 |
| `lrmoo:F18_Serial_Work` | 1 |

## Properties (both graphs)

| Property | Triples |
|---|---|
| `rdf:type` | 4253 |
| `crm:P190_has_symbolic_content` | 558 |
| `crm:P2_has_type` | 538 |
| `dct:title` | 517 |
| `dct:creator` | 512 |
| `crm:P14_carried_out_by` | 512 |
| `dcat:keyword` | 407 |
| `dct:license` | 395 |
| `crm:P1_is_identified_by` | 348 |
| `owl:sameAs` | 344 |
| `crm:P4_has_time-span` | 279 |
| `crm:P82a_begin_of_the_begin` | 279 |
| `crm:P82b_end_of_the_end` | 279 |
| `dct:description` | 260 |
| `dct:type` | 260 |
| `dcat:theme` | 260 |
| `dcat:landingPage` | 259 |
| `prism:volume` | 258 |
| `dct:isPartOf` | 258 |
| `crm:P106i_forms_part_of` | 258 |
| `prism:number` | 250 |
| `dct:hasPart` | 250 |
| `dcat:inSeries` | 250 |
| `rdfs:label` | 227 |
| `dct:publisher` | 211 |
| `lrmoo:R17_created` | 210 |
| `dct:issued` | 210 |
| `bibo:authorList` | 210 |
| `bibo:locator` | 210 |
| `crm:P102_has_title` | 210 |
| `crm:P94_has_created` | 210 |
| `rdf:_1` | 210 |
| `dcat:accessURL` | 210 |
| `dcat:distribution` | 210 |
| `sqp:citationLabel` | 210 |
| `sqp:entryNumber` | 210 |
| `dct:identifier` | 202 |
| `bibo:doi` | 201 |
| `prov:wasDerivedFrom` | 201 |
| `bibo:abstract` | 194 |
| `dct:language` | 169 |
| `dct:format` | 162 |
| `spdx:algorithm` | 162 |
| `spdx:checksum` | 162 |
| `spdx:checksumValue` | 162 |
| `crm:P165_incorporates` | 162 |
| `dcat:byteSize` | 162 |
| `dcat:downloadURL` | 162 |
| `dcat:mediaType` | 162 |
| `rdf:_2` | 153 |
| `bibo:presentedAt` | 115 |
| `crm:P16_used_specific_object` | 115 |
| `foaf:name` | 107 |
| `foaf:familyName` | 106 |
| `foaf:givenName` | 106 |
| `rdf:_3` | 78 |
| `schema:identifier` | 76 |
| `schema:name` | 70 |
| `sqp:languageGuessed` | 70 |
| `schema:endDate` | 69 |
| `schema:startDate` | 69 |
| `event:place` | 60 |
| `crm:P7_took_place_at` | 60 |
| `schema:location` | 60 |
| `crm:P168_place_is_defined_by` | 51 |
| `geo:asWKT` | 51 |
| `geo:hasDefaultGeometry` | 51 |
| `geo:hasGeometry` | 51 |
| `dcat:centroid` | 51 |
| `schema:addressCountry` | 51 |
| `schema:description` | 51 |
| `schema:latitude` | 51 |
| `schema:longitude` | 51 |
| `sqp:sigil` | 40 |
| `sqp:specialIssue` | 40 |
| `dcat:version` | 38 |
| `rdf:_4` | 37 |
| `rdfs:seeAlso` | 21 |
| `schema:codeRepository` | 19 |
| `bibo:editor` | 15 |
| `rdf:_5` | 14 |
| `schema:eventAttendanceMode` | 10 |
| `dcat:dataset` | 8 |
| `rdf:_6` | 7 |
| `rdf:_7` | 6 |
| `dct:contributor` | 5 |
| `rdf:_8` | 3 |
| `rdf:_10` | 2 |
| `rdf:_9` | 2 |
| `prism:issn` | 1 |
| `dct:modified` | 1 |
| `dct:relation` | 1 |
| `bibo:issn` | 1 |
| `rdf:_11` | 1 |
| `dcat:themeTaxonomy` | 1 |
| `foaf:homepage` | 1 |
| `schema:editor` | 1 |
