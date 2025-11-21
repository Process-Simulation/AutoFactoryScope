# Contributing to AutoFactoryScope

Thank you for your interest in contributing to AutoFactoryScope! This guide will help you get started.

## Prerequisites

Before contributing, ensure you have:

- **Python 3.11** (for backend development)
- **Node.js 18+** and **npm** (or **yarn**/ **pnpm**) (for frontend development)
- **Git** (for version control)
- **Visual Studio Code** or modern IDE (for TypeScript/React development)
- Basic familiarity with:
  - Python and FastAPI
  - TypeScript and React (for frontend work)
  - Git and GitHub workflows

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/AutoFactoryScope.git
cd AutoFactoryScope
```

### 2. Set Up Backend

```bash
cd src/backend/autofactoryscope_api

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Frontend

```bash
cd src/frontend/autofactoryscope-web

# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

### 4. Run Locally

**Backend:**
```bash
# From src/backend/autofactoryscope_api
uvicorn autofactoryscope_api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
# From src/frontend/autofactoryscope-web
npm run dev
# or
yarn dev
# or
pnpm dev
```

Or use the development scripts in `scripts/`:
- `scripts/dev_backend.ps1` (Windows) or `scripts/dev_backend.sh` (Linux/macOS)
- `scripts/dev_frontend.ps1` (Windows) or `scripts/dev_frontend.sh` (Linux/macOS)

## Development Workflow

### 1. Choose or Create an Issue

- Check existing issues to see if your idea is already discussed
- Review `docs/PROJECT_STATUS.md` to understand current priorities
- If starting new work, create an issue first to discuss

### 2. Create a Feature Branch

Follow the branching strategy in `docs/BRANCHING_STRATEGY.md`:

```bash
# Ensure you're on develop and up to date
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
```

**Branch naming:**
- `feature/backend-tiling-optimisation`
- `feature/frontend-wpf-upload-ui`
- `feature/devops-ci-pipeline`

### 3. Make Your Changes

- Write clear, maintainable code
- Follow existing code style
- Add comments for complex logic
- Keep functions small and focused
- Use guard clauses and avoid deep nesting

### 4. Run Tests

**Backend:**
```bash
cd src/backend/autofactoryscope_api
pytest
```

**Frontend:**
```bash
cd src/frontend/autofactoryscope-web
npm run build  # Ensure it builds
npm test  # If tests exist
# or
yarn build
yarn test
```

Or use the validation script:
```bash
scripts/check_all.ps1
```

### 5. Update Documentation

- Update `docs/PROJECT_STATUS.md` if you complete tasks
- Add/update code comments and docstrings
- Update README if setup instructions change
- Update architecture docs if system design changes

### 6. Commit Your Changes

Use conventional commit messages:

```bash
git add .
git commit -m "feat: add batch processing endpoint"
```

**Commit types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance

### 7. Push and Open Pull Request

```bash
git push -u origin feature/your-feature-name
```

Then:
1. Open Pull Request on GitHub
2. Target branch: `develop` (for features) or `main` (for hotfixes)
3. Fill out PR template (`.github/PULL_REQUEST_TEMPLATE.md`)
4. Link to related issue
5. Wait for CI checks to pass
6. Request review from maintainers

### 8. Address Review Feedback

- Make requested changes
- Push updates to your branch (PR updates automatically)
- Respond to comments
- Re-request review when ready

### 9. Merge and Cleanup

Once approved and merged:
- Delete your feature branch (local and remote)
- Update local `develop` branch: `git checkout develop && git pull`

## Code Style Guidelines

### Python (Backend)

- Use type hints
- Follow PEP 8 style guide
- Keep functions small and single-purpose
- Use guard clauses instead of deep nesting
- Avoid `else` when early return is clearer

### TypeScript/React (Frontend)

- Follow TypeScript best practices
- Use functional components with hooks
- Separate UI logic from service calls
- Keep components focused and testable
- Use TypeScript types for API responses

## Testing Guidelines

- Write tests for new features
- Ensure existing tests still pass
- Aim for reasonable coverage (not 100%, but meaningful)
- Test edge cases and error conditions

## Documentation Guidelines

- Write clear, concise documentation
- Assume competent engineers as audience
- Update relevant docs when making changes
- Keep examples up to date

## What to Contribute

We welcome contributions in:

- **Bug fixes**: Fix issues reported in GitHub Issues
- **Features**: Implement features from roadmap or approved issues
- **Documentation**: Improve docs, add examples, fix typos
- **Tests**: Add test coverage, improve test quality
- **Performance**: Optimize algorithms, reduce latency
- **CI/CD**: Improve workflows, add checks

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Use `.github/ISSUE_TEMPLATE/bug_report.md`
- **Features**: Use `.github/ISSUE_TEMPLATE/feature_request.md`
- **Workflow**: See `docs/BRANCHING_STRATEGY.md`

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project maintainers' guidance

## Recognition

Contributors will be recognized in:
- GitHub Contributors page
- Release notes (for significant contributions)
- Project documentation (if applicable)

Thank you for contributing to AutoFactoryScope!

