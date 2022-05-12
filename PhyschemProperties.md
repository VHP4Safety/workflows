```mermaid
graph TD
  Chemical-->Assay
  Assay-->Readout
  Readout-->DataRepository
  DataRepository-->Wikibase
  DataRepository-->Parameters
  Parameters-->Models
  Models-->PBPK
  Models-->qAOP
  Models-->QSAR
  Models-->MIEPrediction
  Models-->MetabolismPrediction
  Models-->ExposurePrediction
  Models-->QIVIVE
```
