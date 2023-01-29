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
  Utrecht.University--Has-->VHP4Safety.Shared.Projects
  RIVM--Has-->VHP4Safety.Shared.Projects
  Other.VHP4Safety.Partners--Has-->VHP4Safety.Shared.Projects
  Hogeschool.Utrecht<--IsMember--M.Teunis
  Hogeschool.Utrecht<--IsMember--Second.admin  
```
