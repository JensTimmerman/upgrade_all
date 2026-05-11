# upgrade-all

> The `pip upgrade-all` command pip never shipped.

Upgrades every package installed in the current Python environment to its
latest release on PyPI — using pip's own internal machinery, so resolution,
wheel caching, and hash-checking all work exactly as they do with a normal
`pip install -U` call.

## Install

```sh
pip install upgrade-all
```

## Usage

```
upgrade-all [options]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--dry-run` | `-n` | Print what would be upgraded without doing anything |
| `--skip PKG` | `-s PKG` | Skip a package (repeatable) |
| `--user` | | Pass `--user` through to pip |
| `--index-url URL` | `-i URL` | Use a custom package index |
| `--verbose` | `-v` | Show pip's full output |
| `--version` | | Print version and exit |

### Examples

```sh
# Upgrade everything
upgrade-all

# See what would change without touching anything
upgrade-all --dry-run

# Upgrade everything except pip and setuptools
upgrade-all --skip pip --skip setuptools

# Use a private index
upgrade-all --index-url https://my.artifactory.example/simple/

# Pass extra flags straight through to pip (after --)
upgrade-all -- --no-deps
```

### As a module

```sh
python -m upgrade_all
```

### Programmatic API

```python
from upgrade_all.__main__ import upgrade_all

exit_code = upgrade_all(skip=["pip", "setuptools"], verbose=True)
```

## Why does this exist?

The pip maintainers [decided](https://github.com/pypa/pip/pull/10491) that
environment-wide upgrade management is out of pip's scope. Fair enough —
but the need is real. This package fills that gap with a tiny, focused tool
that does exactly one thing.

## Caveats

- Upgrades are attempted in alphabetical order. If package A depends on an
  old version of B and you upgrade both, the resolver may complain. Use
  `--skip` to exclude packages you want to pin.
- Editable installs (`pip install -e .`) are included. Use `--skip` to
  exclude them if needed.
- System-managed Python environments (Homebrew, distro packages) may
  reject upgrades without `--user`.

## License

GPL v3
