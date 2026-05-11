"""pip-upgrade-all: upgrade every installed package to the latest PyPI release.

Uses pip's own internal machinery (the same path pip install -U uses) so
resolution, wheel caching, hash-checking and VCS support all work exactly
as they would with a normal pip install invocation.
"""

from __future__ import annotations

import argparse
import signal
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
    "pygobject",
    "pycairo",
    "dbus-python",
}


def _installed_packages(skip: set[str], pip_only: bool = False) -> list[str]:
    """Return the project names of every distribution in the current env.

    If pip_only is True, only packages installed by pip are included,
    skipping anything installed by the OS package manager (dnf, rpm, etc).
    """
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
        if pip_only:
            installer = (dist.read_text("INSTALLER") or "").strip().lower()
            if installer not in ("pip", ""):
                continue
        seen.add(normalised)
        names.append(project_name)

    return sorted(names, key=str.lower)


def upgrade_all(
    *,
    dry_run: bool = False,
    skip: list[str] | None = None,
    user: bool = False,
    with_deps: bool = False,
    index_url: str | None = None,
    verbose: bool = False,
) -> int:
    """Upgrade all installed packages one by one.

    Returns 0 if all succeeded, 1 if any failed.
    """
    skip_set = SYSTEM_PACKAGES | {s.lower().replace("-", "_") for s in (skip or [])}
    packages = _installed_packages(skip_set, pip_only=user)

    if not packages:
        print("No packages found to upgrade.", file=sys.stderr)
        return 0

    base_cmd = ["install", "--upgrade"]
    if user:
        base_cmd.append("--user")
    if not with_deps:
        base_cmd.append("--no-deps")
    if index_url:
        base_cmd.extend(["--index-url", index_url])
    if not verbose:
        base_cmd.append("-q")

    if dry_run:
        print("Would run:")
        for p in packages:
            print(f"  pip {' '.join(base_cmd)} {p}")
        return 0

    failed: list[str] = []
    total = len(packages)

    # Restore default SIGINT so Ctrl+C works even if pip swallows it
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        for i, package in enumerate(packages, 1):
            print(f"[{i}/{total}] {package}… ", end="", flush=True)
            exit_code = pip_main(base_cmd + [package])
            if exit_code == 0:
                print("✓")
            else:
                print("✗ failed")
                failed.append(package)
    except KeyboardInterrupt:
        print("\n\nAborted.")
        if failed:
            print(f"\n{len(failed)} package(s) failed before abort:")
            for p in failed:
                print(f"  • {p}")
        return 1

    if failed:
        print(f"\n{len(failed)} package(s) failed to upgrade:")
        for p in failed:
            print(f"  • {p}")
        return 1

    print(f"\n✨ All {total} package(s) upgraded successfully.")
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="pip-upgrade-all",
        description=(
            "Upgrade every installed package to the latest release on PyPI.\n\n"
            "Installs packages one by one with --no-deps by default.\n"
            "Use --with-deps to enable full dependency resolution."
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
        help=(
            "Only upgrade packages installed by pip (not the OS package manager), "
            "and install into the user site-packages directory."
        ),
    )
    parser.add_argument(
        "--with-deps",
        action="store_true",
        help="Enable full dependency resolution (slower, may cause conflicts).",
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

    args = parser.parse_args(argv)

    exit_code = upgrade_all(
        dry_run=args.dry_run,
        skip=args.skip,
        user=args.user,
        with_deps=args.with_deps,
        index_url=args.index_url,
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
