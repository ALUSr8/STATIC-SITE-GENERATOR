# Accessibility and End-User Test Report

Date: 2026-06-11

## Accessibility Checks

Passed:

- Pages use semantic `header`, `nav`, `main`, `section`, and form elements.
- A skip link is available for keyboard users.
- Form inputs have visible labels.
- Buttons and links have visible focus outlines.
- Image upload inputs restrict expected image file types.
- Component images support alt text.
- Layout responds to smaller screens without overlapping controls.
- Text wraps inside cards, buttons, and panels.

Remaining improvement:

- Add automated accessibility tooling such as axe-core in a browser test suite.
- Add per-image alt text editing for existing gallery images.

## End-User Understanding Checks

Passed:

- Home screen explains the create-compose-export workflow.
- Project list has a visible `New Project` action.
- Project detail has visible page management, theme editing, and export actions.
- Page editor separates the component toolbox from the page canvas.
- Each component preview has an `Edit` action.
- Status messages confirm successful create/save actions.

## Manual Smoke Tests

Completed:

- Homepage loads.
- Project list loads.
- New project form creates a project.
- New page form creates a page with a unique slug.
- Page editor displays component toolbox and component previews.
- Image previews load from `/uploads/...`.
- Export route writes static HTML, CSS, and assets.

## Automated Tests

Command:

```powershell
python -m unittest discover -s tests
```

Coverage areas:

- Database/project creation
- Page creation and unique slugs
- Component storage
- Theme updates and fallback creation
- Multi-page export with copied assets
- Core route loading and form behavior
