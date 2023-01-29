```mermaid
graph TD
  Sysrev.com-->Sysrev.licences
  Sysrev.licences--HasLicence-->Utrecht.University
  Sysrev.licences--HasLicence-->Hogeschool.Utrecht
  Sysrev.licences--HasLicence-->RIVM
  Sysrev.com-->VHP4Safety.Sysrev.Org
  M.Teunis--HasRootAccess-->VHP4Safety.Sysrev.Org
  SecondAdmin--HasRootAccess-->VHP4Safety.Sysrev.Org
  Hogeschool.Utrecht--IsOwner-->VHP4Safety.Sysrev.Org
  VHP4Safety.Sysrev.Org--IsOwner-->VHP4Safety.Shared.Projects
  Hogeschool.Utrecht--Has-->VHP4Safety.Shared.Projects
```
