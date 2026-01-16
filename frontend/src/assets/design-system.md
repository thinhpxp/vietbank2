# Admin Design System

This project uses a centralized Design System for the Admin Interface to ensure consistency, easy maintenance, and Dark Mode support.

## 1. Core Principles
- **Tokens**: All colors, spacing, and sizing are defined in `tokens.scss`.
- **Global CSS**: Common components (Buttons, Panels, Tables, Forms) are defined in `admin.css`.
- **No Scoped CSS**: Admin components should avoid `<style scoped>` for layout and common elements. Use global classes instead.

## 2. Design Tokens (`tokens.scss`)
Imported globally in `main.js`. Use CSS variables in your styles if you need custom overrides.

```css
/* Examples */
color: var(--color-primary);
background: var(--color-bg);
padding: var(--spacing-md);
border-radius: var(--radius-sm);
```

### Dark Mode
Dark mode is activated by adding the class `dark-mode` to the `<html>` element.
`tokens.scss` automatically overrides variables when this class is present.

```js
// Toggle Dark Mode
document.documentElement.classList.toggle('dark-mode');
```

## 3. Global Components

### Panels & Containers
- `admin-page`: Root container for a page.
- `admin-panel`: A white/boxed section for forms or content.
- `dashboard-container`: Centered container width.

### Forms
Use these classes for consistent form styling.
- `admin-form-grid`: Grid layout for forms.
- `admin-form-section`: Grouping fields with a header.
- `admin-field`: Wrapper for label + input.
- `admin-form-control`: Standard input/select style.
- `admin-checkbox-label`: Flex container for checkboxes.
- `admin-form-selector`: Box for selecting multiple items (checkbox list).

### Buttons
- `btn-action`: Base class.
- `btn-primary`, `btn-save`, `btn-create`: Primary actions (Blue).
- `btn-edit`, `btn-delete`, `btn-copy`: Contextual actions.

### Tables
- `data-table`: Standard striped table.
- `admin-sortable`: Class for sortable headers.

### Badges & Chips
- `badge`, `badge-admin`, `badge-user`: Status indicators.
- `admin-group-chip`: Selection chips.

## 4. Migration Guide
To migrate an existing component:
1. Remove local `<style scoped>` if it duplicates global styles.
2. Replace local classes with `admin-*` classes in `<template>`.
   - `.form-control` -> `.admin-form-control`
   - `.card` / `.box` -> `.admin-panel`
3. Ensure no hardcoded hex colors are used.

## 5. Directory Structure
- `frontend/src/assets/tokens.scss`: Variable definitions.
- `frontend/src/assets/admin.css`: Global class definitions.
