```mermaid
graph TD
CellType-->Assay
ExposureScenario-->Assay
ExposureDuration-->ExposureScenario
ExposureDose-->ExposureScenario
Chemical-->ChemicalProperties
ChemicalProperties---Assay
Assay-->Data
Data-->DataFormat
```
