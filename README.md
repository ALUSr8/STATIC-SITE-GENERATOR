# TemplateForge

TemplateForge is a Flask-based static site generator for building small multi-page websites through a visual component editor. Create pages, customize themes, upload assets, and export a portable HTML/CSS website ready for deployment.

## Highlights

- Account-based projects and page management
- Visual component editor with move up/down controls
- Hero, text, image, gallery, feature, CTA, testimonial, pricing, contact, portfolio, and footer components
- Theme customization for fonts and colors
- Validated image uploads
- Static HTML/CSS export with copied assets
- Generated multi-page navigation

## Tech Stack

- Python
- Flask
- SQLite
- Jinja2
- HTML & CSS
- Pillow
- Python `unittest`

## Quick Start

### Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

### Create and Activate a Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

Open your browser and navigate to:

```
http://127.0.0.1:5000
```

Create an account and start building a project.

## Running Tests

```bash
python -m unittest discover -s tests
```

## Project Structure

```text
app.py                 Flask application setup
routes/                Request handlers
modules/               Authentication, database, editor, and export logic
templates/             Jinja UI templates
static/                Application styles and assets
database/              SQLite database storage
tests/                 Automated test suite
exports/               Generated static websites
user_uploads/          User-uploaded assets
```

## Security Features

- Parameterized SQLite queries to reduce SQL injection risk
- User content escaping during static-site generation
- CSRF protection for form actions
- Image upload validation for JPG, PNG, GIF, and WebP files
- Password hashing for user accounts

### Deployment Recommendations

For production deployments:

- Configure a secure `SECRET_KEY`
- Enable `SESSION_COOKIE_SECURE=1` when using HTTPS
- Consider adding rate limiting and additional security headers

## Current Limitations

This project was developed as a learning exercise in Flask, SQLite, and static-site generation. The core site-building and export workflow is complete, though several advanced features remain out of scope.

### Security & Deployment

- Exported websites are intentionally generated as public static sites.
- Storage currently relies on SQLite and the local file system.
- Advanced production features such as rate limiting, Content Security Policy (CSP), comprehensive audit logging, and deployment automation are not implemented.
- Multi-user asset ownership controls are planned for future versions.

### Editor Features

- Project names and descriptions cannot currently be edited after creation.
- Pages cannot be reordered or assigned custom navigation labels.
- Components support reordering but do not support drag-and-drop, duplication, undo/redo, or revision history.
- Rich-text and Markdown editing are not implemented.

### Asset & Export Management

- Asset library management features are limited.
- Exports are written to local folders only.
- ZIP exports, deployment integrations, export history, and automatic cleanup are not yet available.

## Future Improvements

Planned enhancements include:

- Drag-and-drop page and component editing
- Rich-text and Markdown support
- Asset library and optimization workflows
- Enhanced account management
- SEO tools and custom metadata
- PostgreSQL support
- CI/CD pipelines
- Deployment automation
- Export history and ZIP downloads

## License

This project is licensed under the MIT License.
