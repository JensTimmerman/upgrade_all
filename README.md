# pip-upgrade-all

> The `pip upgrade-all` command pip never shipped.

Upgrades every package installed in the current Python environment to its
latest release on PyPI — one package at a time, using pip's own internal
machinery.

The pip maintainers [decided](https://github.com/pypa/pip/pull/10491) that
environment-wide upgrade management is out of pip's scope. This tool fills
that gap.

## Install

```sh
pip install pip-upgrade-all
```

## Usage

```sh
pip-upgrade-all [options]
```

By default, packages are upgraded one by one without dependency resolution
(`--no-deps`). This avoids the resolver backtracking and version conflicts
that come with upgrading everything at once. Use `--with-deps` to opt into
full resolution if you need it.

System-managed packages (those installed by `dnf`, `rpm`, `apt`, etc.) are
automatically detected via their `INSTALLER` metadata and skipped when
using `--user`, so they won't get a duplicate copy in your user site-packages.

## Options

| Flag | Short | Description |
|------|-------|-------------|
| `--dry-run` | `-n` | Print what would be upgraded without doing anything |
| `--user` | | Only upgrade pip-installed packages, into `~/.local` |
| `--skip PKG` | `-s PKG` | Skip a package (repeatable) |
| `--with-deps` | | Enable full dependency resolution (slower, may conflict) |
| `--index-url URL` | `-i URL` | Use a custom package index |
| `--verbose` | `-v` | Show pip's full output |
| `--version` | | Print version and exit |

## Examples

```sh
# Upgrade everything (no-deps, fast)
pip-upgrade-all

# Only upgrade pip-installed packages, leave system packages alone
pip-upgrade-all --user

# See what would change without touching anything
pip-upgrade-all --dry-run

# Skip specific packages
pip-upgrade-all --skip websockets --skip urllib3

# Full dependency resolution (slower, may backtrack)
pip-upgrade-all --with-deps

# Use a private index
pip-upgrade-all --index-url https://my.artifactory.example/simple/
```

## Caveats

- **`--no-deps` is the default.** This means genuinely new dependencies
  introduced by an upgraded package won't be installed automatically. If
  something breaks after upgrading, install the missing dependency manually
  or re-run with `--with-deps`.

- **Dependency conflicts are ignored by default.** Upgrading everything to
  latest will sometimes leave packages with incompatible version combinations
  (e.g. `package-a` requires `websockets<16` but you now have `websockets 16`).
  These are usually harmless warnings unless you actually use that code path.
  Use `--skip` to pin packages you care about.

- **System packages are skipped with `--user`.** Without `--user`, a small
  hardcoded list of known system packages (`dnf`, `apt`, `pygobject`, etc.)
  is still skipped as a safety net.

## Programmatic API

```python
from pip_upgrade_all.__main__ import upgrade_all

exit_code = upgrade_all(user=True, verbose=True)
```

## License

GPL v3
