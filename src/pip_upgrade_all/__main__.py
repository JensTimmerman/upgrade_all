"""pip-upgrade-all: upgrade every installed package to the latest PyPI release.

Uses pip's own internal machinery (the same path pip install -U uses) so
resolution, wheel caching, hash-checking and VCS support all work exactly
as they would with a normal pip install invocation.
"""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import distributions

from pip._internal.cli.main import main as pip_main

# Packages managed by the OS package manager that must never be upgraded via pip.
SYSTEM_PACKAGES = {
    "dnf",
    "dnf-plugins-core",
    "rpm",
    "rpm-python",
    "gpg",
    "gpgme",
    "apt",
    "apt-pkg",
    "distro-info",
    "ubuntu-advantage-tools",
    "unattended-upgrades",
}


def _installed_packages(skip: set[str]) -> list[str]:
    """Return the project names of every distribution in the current env."""
    seen: set[str] = set()
    names: list[str] = []

    for dist in distributions():
        project_name = dist.metadata["Name"]
        if not project_name:
            continue
        normalised = project_name.lower().replace("-", "_")
        if normalised in seen:
            continue
        if normalised in skip:
            continue
        seen.add(normalised)
        names.append(project_name)

    return sorted(names, key=str.lower)


def upgrade_all(
    *,
    dry_run: bool = False,
    skip: list[str] | None = None,
    user: bool = False,
    index_url: str | None = None,
    extra_args: list[str] | None = None,
    verbose: bool = False,
) -> int:
    """Upgrade all installed packages.

    Returns pip's exit code (0 = success).
    """
    skip_set = SYSTEM_PACKAGES | {s.lower().replace("-", "_") for s in (skip or [])}
    packages = _installed_packages(skip_set)

    if not packages:
        print("No packages found to upgrade.", file=sys.stderr)
        return 0

    cmd = ["install", "--upgrade"]

    if user:
        cmd.append("--user")
    if index_url:
        cmd.extend(["--index-url", index_url])
    if not verbose:
        cmd.append("-q")

    cmd.extend(extra_args or [])
    cmd.extend(packages)

    if dry_run:
        print("Would run:")
        print("  pip", " ".join(cmd))
        print(f"\n{len(packages)} package(s) would be upgraded:")
        for p in packages:
            print(f"  {p}")
        return 0

    if verbose:
        print(f"Upgrading {len(packages)} package(s)…")

    return pip_main(cmd)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="pip-upgrade-all",
        description=(
            "Upgrade every installed package to the latest release on PyPI.\n\n"
            "Equivalent to: pip install -U <all installed packages>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Print what would be upgraded without actually doing it.",
    )
    parser.add_argument(
        "--skip", "-s",
        metavar="PKG",
        action="append",
        default=[],
        help="Skip this package (can be repeated). E.g. --skip pip --skip setuptools",
    )
    parser.add_argument(
        "--user",
        action="store_true",
        help="Install into the user site-packages directory (passes --user to pip).",
    )
    parser.add_argument(
        "--index-url", "-i",
        metavar="URL",
        help="Base URL of the Python Package Index (passed through to pip).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show pip's full output instead of suppressing it.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_version()}",
    )

    # Anything after '--' is forwarded verbatim to pip install
    args, extra = parser.parse_known_args(argv)

    exit_code = upgrade_all(
        dry_run=args.dry_run,
        skip=args.skip,
        user=args.user,
        index_url=args.index_url,
        extra_args=extra or None,
        verbose=args.verbose,
    )
    sys.exit(exit_code)


def _version() -> str:
    try:
        from importlib.metadata import version
        return version("pip-upgrade-all")
    except Exception:
        return "unknown"


if __name__ == "__main__":
    main()
