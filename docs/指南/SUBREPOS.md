% 独立子仓库说明

以下两个目录为独立 Git 仓库，不纳入本项目的版本管理：

- `Researchloop-v1/`
- `v0-researchloop/`

主仓库的 `.gitignore` 已忽略它们，避免误提交。

## 使用建议
- 在各自目录内单独进行 Git 操作（`git status/commit/push/pull`）。
- 克隆本主仓库后，这两个目录不会随之出现，需要时请自行克隆/初始化：
  - 例如：`git clone <repo-url> Researchloop-v1`
  - 例如：`git clone <repo-url> v0-researchloop`
- 若希望将其纳入主仓库，建议改用 Git Submodule 管理：
  - `git submodule add <repo-url> Researchloop-v1`
  - `git submodule add <repo-url> v0-researchloop`
  - 并删除 `.gitignore` 中对应忽略规则。

## 维护注意
- 请不要在主仓库中直接提交上述目录下的文件。
- 如需共享这两个子仓库的变更，请在各自仓库中提交并推送到其远程。

