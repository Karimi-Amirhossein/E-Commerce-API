# Contribution Guidelines

Welcome to the E-Commerce API project! To ensure smooth collaboration, please follow these rules.  
Our goal is clean code, clear communication, and a stable `main` branch. 🚀

---

## 1. Git Workflow

**Main rules:**
- 🚫 Never push directly to `main`.
- 🌿 Create a new branch for each feature or fix:
  `feature/authentication`, `fix/order-total`, etc.
- ✅ Always open a **Pull Request (PR)** to merge into `develop`.
- 👀 Every PR must be **reviewed and approved** by another team member.
- ✍️ Follow **Conventional Commits** for commit messages:
  - `feat:` → new feature
  - `fix:` → bug fix
  - `refactor:` → code refactor
  - `docs:` → documentation change
- **🧹 Stay Updated with Rebase:** Before creating a PR, sync your branch with `develop` to keep the history clean:
  ```bash
  git pull --rebase origin develop
  ```


**Example Workflow:**
  # 1. Create a new branch for your task
  git checkout -b feature/add-user-model

  # 2. Do your work and commit it
  # ... code changes ...
  git commit -m "feat: add CustomUser model"

  # 3. Before pushing, sync your branch with the latest develop
  git pull --rebase origin develop

  # 4. Now push your clean, updated branch
  git push origin feature/add-user-model


## 2. Development Setup

- 🐍 Python 3.12.x  
- 🐘 PostgreSQL 17.x  
- 📦 Install dependencies:  
  ```bash
  pip install -r requirements.txt
  ```
- ⚙️ Use `.env` for secrets (never commit it).
  - Add `.env.example` as a template.

---

## 3. Code Style

- Use **PEP 8** standards.  
- Use **Ruff** to lint & format code:  
  ```bash
  ruff check . --fix
  ruff format .
  ```
- Class names → `PascalCase`  
- Variables & functions → `snake_case`  
- Files → `snake_case.py`  
- Models must include `__str__()` and timestamps (`created_at`, `updated_at`).

---

## 4. Database Rules

- Singular model names (e.g., `Product`, `Order`).  
- Always define `related_name` for foreign keys.  
- Run migrations before pushing code:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

---

## 5. Code Reviews & PRs

When creating a **Pull Request**:
- Title format: `[Feature] Add user model`
- Description should include:
  - What changed
  - Why it changed
  - Any tests run

**On GitHub**, PRs will trigger automatic checks:
1. Linting (Ruff)
2. Tests (`python manage.py test`)
3. Review approval

Only approved PRs can merge into `develop`.

---

## 6. API Responses

Follow a consistent JSON format:
```json
{
  "success": true,
  "message": "Product created successfully",
  "data": {}
}
```
For errors:
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

---

## 7. Collaboration Tools

- Task management → **Trello / GitHub Projects**
- Communication → **Telegram / Discord**
- Weekly sync meeting → review progress + merge develop → main

---

## 8. Deployment Rules

- `.env` files never committed  
- Use **Docker** for consistent builds  
- Test everything in **staging** before pushing to production  

---

## 9. GitHub PR Template (optional)

To automatically show PR instructions in GitHub:

Create a file at: `.github/pull_request_template.md` with:

```md
## Description
Explain what your PR does.

## Type of change
- [ ] New feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation update

## Checklist
- [ ] Code is linted with Ruff
- [ ] Tests passed locally
- [ ] Reviewed by a teammate
```

This makes every PR consistent and professional 💪

---

**End of Guidelines — Thank you for contributing! 🙌**
