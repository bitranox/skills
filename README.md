# bx_skills

<!-- Badges -->
[![CI](https://github.com/bitranox/bx_skills/actions/workflows/default_cicd_public.yml/badge.svg)](https://github.com/bitranox/bx_skills/actions/workflows/default_cicd_public.yml)
[![CodeQL](https://github.com/bitranox/bx_skills/actions/workflows/codeql.yml/badge.svg)](https://github.com/bitranox/bx_skills/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open in Codespaces](https://img.shields.io/badge/Codespaces-Open-blue?logo=github&logoColor=white&style=flat-square)](https://codespaces.new/bitranox/bx_skills?quickstart=1)
[![PyPI](https://img.shields.io/pypi/v/bx_skills.svg)](https://pypi.org/project/bx_skills/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/bx_skills.svg)](https://pypi.org/project/bx_skills/)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-46A3FF?logo=ruff&labelColor=000)](https://docs.astral.sh/ruff/)
[![codecov](https://codecov.io/gh/bitranox/bx_skills/graph/badge.svg?token=UFBaUDIgRk)](https://codecov.io/gh/bitranox/bx_skills)
[![Maintainability](https://qlty.sh/badges/041ba2c1-37d6-40bb-85a0-ec5a8a0aca0c/maintainability.svg)](https://qlty.sh/gh/bitranox/projects/bx_skills)
[![Known Vulnerabilities](https://snyk.io/test/github/bitranox/bx_skills/badge.svg)](https://snyk.io/test/github/bitranox/bx_skills)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)



# Claude Skills

A collection of Claude Code skills for software engineering workflows.

Skills prefixed with `bx-` are custom-built or modified skills from one of the following sources :

- [Vercel Agent Skills Directory](https://skills.sh)
- [Obra Superpowers Skill Library](https://skills.sh/obra/superpowers)
- [React/Next.js Performance Optimization](https://skills.sh/vercel-labs/agent-skills)
- [Writing Clearly and Concisely](https://skills.sh/softaworks/agent-tools)
- [Agentation](https://skills.sh/benjitaylor/agentation)
- [Tailwind Design System](https://skills.sh/wshobson/agents/tailwind)
- [UI/UX Pro Max](https://skills.sh/nextlevelbuilder/ui)

## Installation

```bash
# install uv/uvx
python -m pip install --upgrade uv
# install bx-skills
uvx bx_skills@latest --help
```

## CLI Usage

```bash
uvx bx-skills@latest --help                                        # Show help
uvx bx-skills@latest list                                          # Browse catalog
uvx bx-skills@latest list -q                                       # Machine-readable list
uvx bx-skills@latest status --target all --scope both              # Audit installed skills
uvx bx-skills@latest install --all --target claude-code            # Install all skills
uvx bx-skills@latest install bx-textual --target claude-code --scope project  # Install specific skill
uvx bx-skills@latest uninstall bx-textual --target claude-code -y  # Remove a skill
uvx bx-skills@latest info                                          # Version & metadata
uvx bx-skills@latest tui                                           # Launch interactive TUI
```

## Auto-Update via Shell Alias

### Bash

Add the following to `~/.bashrc` to automatically sync skills before every `claude` session:

```bash
alias claude='uvx bx_skills@latest install --all -q && command claude'
```

Reload your shell or run `source ~/.bashrc` to activate.

## Skills

| Skill                              | Description                                                                                                                                                                    |
|------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **brainstorming**                  | Turns ideas into fully formed designs and specs through collaborative dialogue. Explores user intent, requirements, and design before implementation.                          |
| **bx-bash-clean-architecture**     | Framework-agnostic structured Bash architecture with layered ports-and-adapters pattern. Keeps domain pure and testable with inner layers never calling outer layers directly. |
| **bx-bash-reference**              | Complete reference for GNU Bash 5.3 covering all shell syntax, builtins, variables, expansions, redirections, and features.                                                    |
| **bx-enhance-code-quality**        | Scores a project 0-10, identifies issues by severity, and walks through fixes while respecting prior decisions documented in CLAUDE.md.                                        |
| **bx-python-clean-architecture**   | Framework-agnostic typed Python architecture with layered ports-and-adapters pattern. Keeps inner layers pure and independent of infrastructure.                               |
| **bx-python-libraries-to-use**     | Standardized library choices for Python projects ensuring consistency and enforcing preferred tools over alternatives.                                                         |
| **bx-uv**                          | Complete reference for uv (v0.10.2) covering project setup, dependency management, virtual environments, Python versions, tools, Docker, CI/CD, and migration from pip.        |
| **executing-plans**                | Loads a written implementation plan and executes tasks in batches with checkpoints for architect review between batches.                                                       |
| **force-using-skills**             | Establishes that skills must be invoked whenever applicable. If there is even a 1% chance a skill applies, it must be used.                                                    |
| **systematic-debugging**           | Requires finding root cause before attempting fixes. Prevents random patches that mask underlying issues.                                                                      |
| **test-driven-development**        | Write tests first, watch them fail, then write minimal code to pass. Ensures tests validate the right behavior.                                                                |
| **using-superpowers**              | Establishes how to find and use skills, requiring Skill tool invocation before any response when skills apply to the task.                                                     |
| **verification-before-completion** | Requires running verification commands and confirming output before making any success claims. Evidence before assertions.                                                     |
| **writing-plans**                  | Creates comprehensive implementation plans with bite-sized tasks, documenting which files to touch, testing strategies, and how to verify completion.                          |
| **writing-skills**                 | Applies TDD to process documentation by writing test cases, watching them fail, creating skill documentation, and verifying agents comply.                                     |
