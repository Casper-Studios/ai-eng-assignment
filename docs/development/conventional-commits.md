# Conventional Commits Guide

**Last updated: August 4, 2024**

This project **enforces** the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for commit messages. This leads to more readable messages that are easy to follow when looking through the project history.

## Commit Message Format

Each commit message consists of a **header**, a **body** and a **footer**. The header has a special format that includes a **type**, a **scope** and a **subject**:

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

The **header** is mandatory and the **scope** of the header is optional.

### Type

Must be one of the following:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation

### Scope

The scope should be the name of the feature affected (as perceived by the person reading the changelog generated from commit messages). To view/edit the current scopes in the repo, it can be found inside `commitlint.config.js`.

### Subject

The subject contains a succinct description of the change:

- use the imperative, present tense: "change" not "changed" nor "changes"
- don't capitalize the first letter
- no dot (.) at the end

### Body

Just as in the **subject**, use the imperative, present tense. The body should include the motivation for the change and contrast this with previous behavior.

### Footer

The footer should contain any information about **Breaking Changes** and is also the place to reference GitHub issues that this commit **Closes**.

**Breaking Changes** should start with the word `BREAKING CHANGE:` with a space or two newlines. The rest of the commit message is then used for this.

## Examples

```
feat(auth): add login functionality

Implement user authentication using JWT tokens.
```

```
fix(data-cleaner): resolve null pointer exception

BREAKING CHANGE: `clean()` now returns an object instead of an array.
```

```
docs(readme): update installation instructions

Reflect recent changes in the build process.
```

Remember, following these conventions makes it easier for others (and yourself) to understand the project's history and manage releases.
