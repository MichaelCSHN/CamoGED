# camo-eval architecture

## Design rule

Names communicate evidence. Validated standards keep their accepted names. Experimental substitutes use descriptive names or `_lite`. Planned standard names raise rather than returning a misleading number.

## Layers

1. **Validated core** — deterministic metrics with authoritative comparison tests.
2. **Experimental extensions** — domain helpers and explicitly named diagnostics.
3. **Protocol layer** — observer, channel, task, dataset/prediction provenance, threshold policy, environment, seed, uncertainty, and implementation version.
4. **External experiments** — schemas and analyzers for human or sensor studies; the package does not pretend to execute field experiments.

## Package layout

```text
camo_eval/
  metrics/       validated and experimental algorithms
  protocols/     context, provenance and manifests
  runner.py      basename-matched batch evaluation
  export.py      Markdown and LaTeX output
  cli.py         explicit command-line surface
```

## Release gate

A public package release requires tests on supported Python versions, lint and format checks, wheel/sdist build, installation smoke test, validation-register update, and a tagged release manifest.
