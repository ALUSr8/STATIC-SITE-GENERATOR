# Developer Guide

## Requirements

- Python 3.12 or compatible Python 3 version
- Dependencies from `requirements.txt`

## Local Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Tests

```powershell
python -m unittest discover -s tests
```

The tests use temporary databases and temporary upload/export folders. They should not mutate the real `database/sitegen.db` file.

## Important Generated Folders

Ignored by Git:

- `exports/`
- `database/*.db`
- `user_uploads/*`
- `__pycache__/`
- `.venv/`

## Adding Features

Recommended order:

1. Add or update service functions in `modules/`.
2. Add route/form handling in `routes/`.
3. Update templates in `templates/`.
4. Update export behavior when the feature affects generated static sites.
5. Add tests.
6. Update documentation.
