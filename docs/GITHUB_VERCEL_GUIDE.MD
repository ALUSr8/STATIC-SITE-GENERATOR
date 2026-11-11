# GitHub and Vercel Guide

## Before Pushing to GitHub

Check:

- `python -m unittest discover -s tests`
- No private data in `database/sitegen.db`
- No required generated files inside `exports/`
- No personal uploads that should not be public

Recommended files to include:

- Source code
- Templates
- Static CSS
- Tests
- Documentation
- `requirements.txt`
- `vercel.json`
- `api/index.py`

## Vercel Hosting

This repository includes basic Vercel files:

- `vercel.json`
- `api/index.py`

Vercel can run the Flask app through the Python serverless runtime.

Important limitation:

- SQLite database writes and local uploads are not durable on Vercel serverless deployments.

For a production hosted editor, replace local persistence with:

- Hosted SQL database, such as PostgreSQL
- Object storage for uploads, such as S3-compatible storage
- Environment variable configuration for secrets and database URLs

For hosting exported static sites, upload the generated `exports/<project-name>/` folder to any static host.
