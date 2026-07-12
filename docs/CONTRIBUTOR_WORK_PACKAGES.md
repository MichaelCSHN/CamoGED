# Contributor work packages

Work packages are assigned to people or reviewed pull requests, not to AI model names.

| Package | Scope | Required evidence |
|---|---|---|
| BOOK | chapters, bibliography, figures, publication apparatus | resolved citations, Quarto build, factual review notes, asset rights |
| DATA | papers, datasets, verified results registry | schema validation, primary source, verification state, license state |
| EVAL | metric code, protocol schema, CLI, package | tests, authoritative comparison where applicable, API and version notes |
| WEB | generated pages and teaching demo | VitePress build, accessibility smoke, no unlicensed assets |
| RELEASE | versions, artifacts, DOI/archive metadata | tagged commit, complete CI, release manifest, signed human review |
| SECURITY | vulnerability and dual-use response | private intake, triage record, coordinated disclosure decision |

## Interface changes

A change to metric names, data fields, report schemas, generated-page contracts, or public CLI options must update all consumers in one PR and include migration notes.

## Definition of done

A work package is complete only when its required CI is green and the PR records what was validated, what remains experimental, and who performed the human review.
