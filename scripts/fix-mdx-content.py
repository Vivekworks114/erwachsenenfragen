#!/usr/bin/env python3
"""Fix MDX content files for valid parsing."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIRS = [ROOT / "src" / "content" / "blog", ROOT / "src" / "content" / "pages"]


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return f"---{parts[1]}---", parts[2].lstrip("\n")


def extract_inner_div(body: str) -> str:
    body = body.strip()
    match = re.match(r'<div class="wp-content">\s*(.*)\s*</div>\s*$', body, re.S)
    return match.group(1).strip() if match else body


def sanitize_body(body: str) -> str:
    body = extract_inner_div(body)
    body = re.sub(r"\[dwqa-submit-question-form\]", "", body)
    body = re.sub(r"\[zb_[^\]]+\]", "", body)
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.I | re.S)
    body = re.sub(r"<style\b[^>]*>.*?</style>", "", body, flags=re.I | re.S)
    body = re.sub(r"<p>\s*</p>", "", body)
    body = re.sub(r"<a([^>]*)>\s*<p>(.*?)</p>\s*</a>", r"<a\1>\2</a>", body, flags=re.S)
    body = re.sub(r"<img([^>]*)/>", r"<img\1></img>", body)
    body = re.sub(r"\s+", " ", body)
    body = re.sub(r">\s+<", "><", body)

    # Split into block-level tags and wrap only bare text nodes.
    tokens = re.split(r"(</?(?:h[1-6]|p|div|section|form|ul|ol|li|label|input|textarea|button|a|img|table|tr|td|th|blockquote|hr|br)[^>]*>)", body, flags=re.I)
    output: list[str] = []
    for token in tokens:
        if not token:
            continue
        if re.match(r"</?(?:h[1-6]|p|div|section|form|ul|ol|li|label|input|textarea|button|a|img|table|tr|td|th|blockquote|hr|br)", token, re.I):
            output.append(token)
        else:
            text = token.strip()
            if text:
                output.append(f"<p>{text}</p>")

    inner = "".join(output)
    return f'<div class="wp-content">{inner}</div>\n'


def main() -> None:
    for directory in CONTENT_DIRS:
        for path in directory.glob("*.mdx"):
            frontmatter, body = split_frontmatter(path.read_text(encoding="utf-8"))
            sanitized = sanitize_body(body)
            path.write_text(f"{frontmatter}\n\n{sanitized}", encoding="utf-8")
            print(f"Fixed {path.name}")


if __name__ == "__main__":
    main()
