# Branching Strategy

This document formalizes the Git branching model and workflow for AutoFactoryScope.

## Branch Types

### `main`

- **Purpose**: Production-ready code
- **Protection**: Protected branch, no direct commits
- **Merges**: Only from `develop` or `hotfix/*` branches
- **Releases**: Tagged releases only (e.g., `v0.1.0`, `v1.0.0`)

### `develop`

- **Purpose**: Integration branch for day-to-day development
- **Protection**: Protected branch, no direct commits
- **Merges**: From `feature/*` branches via Pull Requests
- **Status**: Should always be in a deployable state

### `feature/*`

- **Purpose**: New features, enhancements, or tasks
- **Source**: Branched from `develop`
- **Naming**: `feature/<short-description>`
- **Examples**:
  - `feature/backend-tiling-optimisation`
  - `feature/backend-nms-tuning`
  - `feature/frontend-wpf-upload-ui`
  - `feature/devops-ci-pipeline`
- **Merge**: Back into `develop` via Pull Request

### `hotfix/*`

- **Purpose**: Urgent fixes for production issues
- **Source**: Branched from `main`
- **Naming**: `hotfix/<short-description>`
- **Examples**:
  - `hotfix/backend-onnx-path-bug`
  - `hotfix/frontend-null-reference-exception`
- **Merge**: Into `main`, then back into `develop`

### `release/*` (Optional)

- **Purpose**: Release hardening and version bumping
- **Source**: Branched from `develop`
- **Naming**: `release/<version>` (e.g., `release/v0.1.0`)
- **Merge**: Into `main` (tagged) and back into `develop`

## Workflow Rules

### General Rules

1. **No direct commits** to `main` or `develop`
2. **All work** happens on feature or hotfix branches
3. **Pull Requests required** for all merges
4. **Squash merges preferred** for feature branches
5. **CI checks must pass** before merge
6. **At least one review** required for PRs

### Creating a Feature Branch

```bash
# Ensure you're on develop and up to date
git checkout develop
git pull origin develop

# Create and switch to new feature branch
git checkout -b feature/your-feature-name

# Make your changes, commit
git add .
git commit -m "feat: description of changes"

# Push to remote
git push -u origin feature/your-feature-name
```

### Creating a Hotfix Branch

```bash
# Start from main
git checkout main
git pull origin main

# Create hotfix branch
git checkout -b hotfix/critical-bug-fix

# Make fix, commit
git add .
git commit -m "fix: description of fix"

# Push to remote
git push -u origin hotfix/critical-bug-fix
```

## Pull Request Process

### Opening a PR

1. Push your feature/hotfix branch to remote
2. Open Pull Request on GitHub:
   - **Target**: `develop` (for features) or `main` (for hotfixes)
   - **Title**: Clear, descriptive (e.g., "feat: optimize image tiling algorithm")
   - **Description**: Use PR template (`.github/PULL_REQUEST_TEMPLATE.md`)
   - **Link**: Reference related issue if applicable

### PR Requirements

- [ ] CI checks pass (backend tests, frontend build)
- [ ] Code follows project style guidelines
- [ ] Documentation updated if needed
- [ ] No merge conflicts
- [ ] At least one approval from maintainer

### PR Review

- Reviewers check code quality, tests, and documentation
- Request changes if needed
- Approve when ready
- Squash merge into target branch

## Example Workflow: Implementing a Feature

### Scenario: Optimize tiling algorithm

1. **Create issue**: "Optimize image tiling to reduce overlap"
2. **Create branch**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/backend-tiling-optimisation
   ```
3. **Develop**:
   - Make changes to `src/backend/autofactoryscope_api/tiling.py`
   - Add tests
   - Update documentation if needed
   - Commit: `git commit -m "feat: reduce tile overlap from 0.2 to 0.1"`
4. **Push and PR**:
   ```bash
   git push -u origin feature/backend-tiling-optimisation
   ```
   - Open PR targeting `develop`
   - Fill out PR template
   - Link to issue
5. **Review and merge**:
   - CI runs automatically
   - Reviewer approves
   - Squash merge into `develop`
6. **Cleanup**:
   - Delete feature branch (local and remote)
   - Close issue

## Commit Message Guidelines

Use conventional commit format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
- `feat: add batch processing endpoint`
- `fix: correct NMS IoU threshold calculation`
- `docs: update architecture diagram`

## Branch Protection

Recommended GitHub branch protection settings:

### `main` branch
- Require pull request reviews (1 approval)
- Require status checks to pass (CI)
- Require branches to be up to date
- Restrict deletions and force pushes

### `develop` branch
- Require pull request reviews (1 approval)
- Require status checks to pass (CI)
- Allow force pushes (for emergency fixes, use with caution)

## Troubleshooting

### Merge conflicts

1. Update your branch from target:
   ```bash
   git checkout feature/your-branch
   git pull origin develop
   ```
2. Resolve conflicts locally
3. Commit and push

### Accidentally committed to develop

1. Create feature branch from current state:
   ```bash
   git checkout -b feature/rescue-commits
   git push -u origin feature/rescue-commits
   ```
2. Reset develop to remote:
   ```bash
   git checkout develop
   git reset --hard origin/develop
   ```
3. Continue work on feature branch

## Questions?

- See `CONTRIBUTING.md` for general contribution guidelines
- Open an issue for workflow questions
- Discuss with maintainers before large changes

