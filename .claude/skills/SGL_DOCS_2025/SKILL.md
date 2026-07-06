```markdown
# SGL_DOCS_2025 Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill outlines the key development patterns and conventions used in the SGL_DOCS_2025 repository. The codebase is written in TypeScript and focuses on documentation-related features, following clear and consistent coding and commit conventions. This guide will help contributors maintain code quality and consistency.

## Coding Conventions

### File Naming
- Use **camelCase** for file names.
  - Example: `userProfile.ts`, `dataFetcher.ts`

### Import Style
- Use **relative imports** for modules within the repository.
  - Example:
    ```typescript
    import { fetchData } from './dataFetcher';
    ```

### Export Style
- Use **named exports** rather than default exports.
  - Example:
    ```typescript
    // dataFetcher.ts
    export function fetchData() { /* ... */ }
    ```

### Commit Messages
- Follow **conventional commit** style.
- Use the `docs` prefix for documentation-related changes.
- Keep commit messages concise (average ~73 characters).
  - Example:
    ```
    docs: update API usage section in README
    ```

## Workflows

### Documentation Update
**Trigger:** When updating or adding documentation files  
**Command:** `/update-docs`

1. Make changes to documentation files.
2. Stage your changes:
    ```
    git add <doc-file>
    ```
3. Commit using the conventional commit style:
    ```
    git commit -m "docs: <concise description of change>"
    ```
4. Push your changes:
    ```
    git push
    ```

### Code Contribution
**Trigger:** When adding or modifying TypeScript source files  
**Command:** `/contribute-code`

1. Create or update `.ts` files using camelCase naming.
2. Use relative imports and named exports.
3. Write or update corresponding test files (see Testing Patterns).
4. Stage, commit, and push your changes using the commit conventions.

## Testing Patterns

- Test files follow the pattern: `*.test.*` (e.g., `userProfile.test.ts`).
- The testing framework is not specified; follow existing patterns in the repository.
- Place test files alongside the files they test or in a dedicated test directory.
- Example test file name: `dataFetcher.test.ts`

## Commands
| Command         | Purpose                                         |
|-----------------|-------------------------------------------------|
| /update-docs    | Workflow for updating documentation             |
| /contribute-code| Workflow for contributing TypeScript code       |
```
