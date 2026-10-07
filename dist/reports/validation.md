# Validation report (S8)

| Check | Graph | Violations | Warnings | Infos |
|---|---|---|---|---|
| DCAT-AP 3.0.1 | `dist/squirrelpapers.ttl` | 0 | 0 | 0 |
| Journal rules | `dist/squirrelpapers.ttl` | 0 | 0 | 0 |
| CIDOC CRM rules | `dist/squirrelpapers-crm.ttl` | 0 | 0 | 0 |

Self-test: a deliberately broken entry (`shapes/selftest.ttl`) was reported by every rule it lists before the real graphs were checked.

DCAT-AP 3.0.1 refers to property shapes it never defines; these references were dropped when loading (the files themselves are unchanged):

- `https://semiceu.github.io/DCAT-AP/releases/3.0.1#dcat:DatasetShape` → `4918ff7a6c1c4b0eea6403dca4b992b87ee1f4ab`
- `https://semiceu.github.io/DCAT-AP/releases/3.0.1#dcat:DatasetShape` → `95c69c99a1e3ade043911b51b942f206dea0e68d`
- `https://semiceu.github.io/DCAT-AP/releases/3.0.1#dcat:DistributionShape` → `653804840386e33525b3d39d205c174780be414b`
- `https://semiceu.github.io/DCAT-AP/releases/3.0.1#dcat:DistributionShape` → `a07d6e7a0a1790b89a1ce7ff602cbbd9ea835282`
- `https://semiceu.github.io/DCAT-AP/releases/3.0.1#dcat:RelationshipShape` → `b7aa98e1befa5130659568aa62e7f38575dc17c1`
