#!/usr/bin/env python3
"""Install/uninstall the local Zen URL context stylesheet mod."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MOD_NAME = "zen-url-context"
START = f"/* BEGIN {MOD_NAME} managed block */"
END = f"/* END {MOD_NAME} managed block */"
PREF_START = f"// BEGIN {MOD_NAME} managed block"
PREF_END = f"// END {MOD_NAME} managed block"
PREFERENCE = 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'

def managed_block(start: str, body: str, end: str) -> str:
    return f"{start}\n{body.rstrip()}\n{end}"

def replace_block(path: Path, start: str, end: str, replacement: str | None, *, prepend: bool = False) -> None:
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    pattern = re.compile(
        rf"(?m)^{re.escape(start)}\n.*?^{re.escape(end)}(?:\n)?",
        re.DOTALL,
    )
    matches = list(pattern.finditer(content))
    if len(matches) > 1:
        raise RuntimeError(f"Multiple managed blocks found in {path}; refusing to edit it")

    if matches:
        match = matches[0]
        content = content[: match.start()] + content[match.end() :]
    elif start in content or end in content:
        raise RuntimeError(f"Incomplete managed block found in {path}; refusing to edit it")

    if replacement:
        if prepend:
            content = replacement + "\n" + content
        else:
            separator = "\n" if content and not content.endswith("\n") else ""
            content = f"{content}{separator}{replacement}\n"

    if content:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    elif path.exists():
        path.unlink()

def install(profile: Path) -> None:
    source_css = Path(__file__).with_name("zen-url-context.css")
    if not source_css.is_file():
        raise RuntimeError(f"Missing stylesheet: {source_css}")

    chrome = profile / "chrome"
    chrome.mkdir(parents=True, exist_ok=True)
    installed_css = chrome / "zen-url-context.css"
    css_content = source_css.read_text(encoding="utf-8")
    if installed_css.exists():
        current = installed_css.read_text(encoding="utf-8")
        if "Zen Mod: URL Context Quick Actions" not in current:
            raise RuntimeError(f"Refusing to overwrite unrelated file: {installed_css}")
    installed_css.write_text(css_content, encoding="utf-8")

    import_body = '@import url("zen-url-context.css");'
    user_chrome_block = managed_block(START, import_body, END)
    replace_block(profile / "chrome" / "userChrome.css", START, END, user_chrome_block, prepend=True)

    preference_block = managed_block(PREF_START, PREFERENCE, PREF_END)
    replace_block(profile / "user.js", PREF_START, PREF_END, preference_block)

    print(f"Installed {MOD_NAME} in {profile}")
    print("Restart Zen to apply the mod and enable profile chrome styles.")

def uninstall(profile: Path) -> None:
    css_file = profile / "chrome" / "zen-url-context.css"
    if css_file.exists():
        content = css_file.read_text(encoding="utf-8")
        if "Zen Mod: URL Context Quick Actions" not in content:
            raise RuntimeError(f"Refusing to remove unrelated file: {css_file}")

    replace_block(profile / "chrome" / "userChrome.css", START, END, None)
    replace_block(profile / "user.js", PREF_START, PREF_END, None)

    if css_file.exists():
        css_file.unlink()

    print(f"Uninstalled {MOD_NAME} from {profile}")
    print("Restart Zen if it is currently running.")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "uninstall"))
    parser.add_argument("--profile", required=True, type=Path)
    args = parser.parse_args()
    profile = args.profile.expanduser().resolve()

    try:
        if not str(args.profile).strip() or not profile.is_dir():
            raise RuntimeError(
                "Profile must be an existing directory. Find its path via about:support in Zen."
            )
        if args.action == "install":
            install(profile)
        else:
            uninstall(profile)
    except (OSError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
