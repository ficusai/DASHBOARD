# Ficus Multi-Repo Master Workspace — /home/ficus-pro/Documents

This directory is the primary multi-repository workspace for `ficusai` projects. Each subfolder represents an independent Git repository connected to public GitHub remotes under the `ficusai` organization.

> **PRIMARY CONFIGURATION SOURCE**: All workspace specifications, project paths, tech stacks, entry points, and rules are defined in machine-readable JSON at:
> **`/home/ficus-pro/Documents/agents.json`**

---

## Project Catalog

| Project | Path | Branch | Remote | Description |
|---------|------|--------|--------|-------------|
| CLUSTER | `/home/ficus-pro/Documents/CLUSTER` | `CLUSTER-0.1v-linux-native` | `https://github.com/ficusai/CLUSTER.git` | Python cluster management tool |
| GENERATOR | `/home/ficus-pro/Documents/GENERATOR` | `GENERATOR-0.1v-linux-native` | `https://github.com/ficusai/GENERATOR.git` | Prompt generator application |
| RSS | `/home/ficus-pro/Documents/RSS` | `RSS-0.1v-linux-native` | `https://github.com/ficusai/RSS.git` | RSS feed scraper and reader |
| SCRIPT | `/home/ficus-pro/Documents/SCRIPT` | `SCRIPT-0.1v-linux-native` | `https://github.com/ficusai/SCRIPT.git` | OpenCode script extractor |
| TRIP | `/home/ficus-pro/Documents/TRIP` | `TRIP-0.1v-linux-native` | `https://github.com/ficusai/TRIP.git` | TypeScript travel planner |
| PROGRESS | `/home/ficus-pro/Documents/PROGRESS` | `PROGRESS-0.1v-linux-native` | `https://github.com/ficusai/PROGRESS.git` | Session progress tracker |
| **DASHBOARD** | `/home/ficus-pro/Documents/DASHBOARD` | `DASHBOARD-0.1v-linux-native` | `https://github.com/ficusai/DASHBOARD.git` | Minimal GTK4 dashboard application |

---

## 1. Autonomous Execution Protocol & Mandatory TODO Checklist

When an AI agent is requested to work on any custom project in this workspace, it MUST operate with **100% full autonomy** according to the following mandatory execution pipeline:

1. **Context Ingestion**: Read `/home/ficus-pro/Documents/agents.json`, project `README.md`, and source code architecture before editing any files.
2. **TODO List Tracking**: Maintain an active task list (`todowrite`) covering research, branch creation, implementation, testing, local commits, and remote publishing.
3. **Autonomous Feature Branching**: Create a dedicated local feature branch (`git checkout -b feature/<feature-name>`) automatically without waiting for explicit prompt instructions.
4. **Idiomatic Implementation**: Modify code adhering strictly to existing project conventions, formatting, type hints, and architecture patterns.
5. **Self-Verification Loop**: Run automated tests, linters, syntax checks, or build commands (`pytest`, `python3 run_tests.py`, `npx tsc --noEmit`, `npm run build`) before completing any step.
6. **Automatic Local Commits**: Stage and commit all edits locally to Git with clear, concise commit messages (`git add . && git commit -m "feat: ..."`).
7. **Remote Branch Publishing**: Push local feature commits to remote GitHub (`git push -u origin feature/<feature-name>`).
8. **Release Merge**: Merge verified feature branches into `<PROJECT>-0.1v-linux-native` and push the updated release branch to remote GitHub.
9. **Documentation Sync**: Update project `README.md` and `agents.json` if entry points, dependencies, or configuration schemas were modified.
10. **Mandatory Branch File Documentation**: Every feature branch MUST record ALL branch-related file changes in the project's public `README.md` **before** the branch is pushed to remote GitHub. Add/refresh a `## Branch-Related File Changes` subsection under the `## Git & Release Branching` section listing every file added or modified by the feature branch, with a one-line description of each change. Update the branch map table, and **remove any branch entries that are NOT actually implemented/pushed** (do not document planned or draft branches). Never skip this step — it is what keeps the public repo README in sync so future feature sessions work without user prompting.

---

## 2. System Environment State & Confidentiality
* **System Environment**:
  * Trading Engine Root: `/home/ficus-pro/Documents/TRADING`
  * Local .NET SDK Root: `/home/ficus-pro/Documents/TRADING/.dotnet`
  * PythonNet DLL: `/home/ficus-pro/Documents/TRADING/miniconda3/envs/qc_lean/lib/libpython3.11.so`
  * OmniRoute Integration: `http://localhost:20128/v1` (Daemon data dir: `/home/ficus-pro/.omniroute`)
  * Obsidian Knowledge Vaults: `/home/ficus-pro/Desktop/BARDAKAS/BRAIN_V2/` and `/home/ficus-pro/Desktop/BARDAKAS/OBSIDIAN-VAULTS/KNOWLEDGEV3/`
* **Confidentiality & Local Isolation**:
  * `/home/ficus-pro/Documents/agents.json` and `/home/ficus-pro/Documents/AGENTS.md` preserve local system state and are explicitly ignored in `/home/ficus-pro/Documents/.gitignore`. They must NEVER be committed to any public Git repository.

---

## 3. Dynamic New Project Auto-Onboarding Protocol
Whenever a NEW project directory is added under `/home/ficus-pro/Documents/<NEW_PROJECT>`, AI agents MUST automatically execute the following 8-step onboarding procedure:

1. **Git Initialization**: Run `git init` inside `/home/ficus-pro/Documents/<NEW_PROJECT>` if it is not already a Git repository.
2. **Branch Standardization**: Set primary branch to `<NEW_PROJECT>-0.1v-linux-native` (`git checkout -b <NEW_PROJECT>-0.1v-linux-native`).
3. **GitHub Remote Setup**: Set remote origin to `https://github.com/ficusai/<NEW_PROJECT>.git`.
4. **JSON Config Indexing**: Append a new project object to `/home/ficus-pro/Documents/agents.json` conforming 100% to the uniform schema (`id`, `name`, `path`, `branch`, `remote`, `description`, `tech_stack`, `entry_points`, `commands`, `ports`, `directories`).
5. **Master Index Update**: Update `/home/ficus-pro/Documents/AGENTS.md` to include the new project in the project catalog.
6. **Standardized Documentation**: Generate a complete 9-section `README.md` in `/home/ficus-pro/Documents/<NEW_PROJECT>/README.md`.
7. **Agent Redirect**: Create `/home/ficus-pro/Documents/<NEW_PROJECT>/AGENTS.md` pointing to master `/home/ficus-pro/Documents/AGENTS.md`.
8. **Git Commit & Publish**: Commit local metadata and push the release branch to remote GitHub (`git push -u origin <NEW_PROJECT>-0.1v-linux-native`).

---

## 4. Code Organization Standards

When writing any new function or code to any codebase in this workspace:
* **One file per function**: Every new function MUST be placed in its own dedicated file.
* **Dedicated folders**: Each function's file must reside in a purpose-built directory specific to that function's responsibility.
* **No grouping in shared files**: Functions must not be grouped into shared or utility files; each function gets its own standalone file within its dedicated folder.

---

## 5. Uniform Project Catalog

All project definitions in `agents.json` share a 100% uniform schema:
* `id`, `name`, `path`, `branch`, `remote`, `description`, `tech_stack`
* `entry_points` (`main`, `cli`, `gui`, `launcher`)
* `commands` (`dev`, `build`, `test`, `compile`, `clean`)
* `ports` (`primary`, `secondary`)
* `directories` (`source`, `tests`, `assets`, `docs`)
