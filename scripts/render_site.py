#!/usr/bin/env python3
"""Render the static homepage from data/profile.yml."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.yml"
INDEX_PATH = ROOT / "index.html"


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value[0:1] == value[-1:] and value.startswith(("'", '"')):
        return value[1:-1]
    if value.isdigit():
        return int(value)
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() in {"null", "none"}:
        return None
    return value


def split_key_value(text: str) -> tuple[str, str]:
    if ":" not in text:
        raise ValueError(f"Expected key/value pair: {text}")
    key, value = text.split(":", 1)
    return key.strip(), value.strip()


def line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_block(lines: list[str], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index

    stripped = lines[index].strip()
    if line_indent(lines[index]) == indent and stripped.startswith("- "):
        items = []
        while index < len(lines):
            line = lines[index]
            current_indent = line_indent(line)
            stripped = line.strip()
            if current_indent < indent or not stripped.startswith("- "):
                break
            if current_indent != indent:
                raise ValueError(f"Unexpected indentation: {line}")

            item_text = stripped[2:].strip()
            index += 1

            if not item_text:
                item, index = parse_block(lines, index, indent + 2)
                items.append(item)
            elif ":" in item_text:
                key, value = split_key_value(item_text)
                item = {key: parse_scalar(value) if value else None}

                while index < len(lines) and line_indent(lines[index]) > indent:
                    child_indent = line_indent(lines[index])
                    if child_indent != indent + 2:
                        raise ValueError(f"Unexpected indentation: {lines[index]}")
                    child_key, child_value = split_key_value(lines[index].strip())
                    index += 1
                    if child_value:
                        item[child_key] = parse_scalar(child_value)
                    else:
                        child, index = parse_block(lines, index, child_indent + 2)
                        item[child_key] = child

                items.append(item)
            else:
                items.append(parse_scalar(item_text))

        return items, index

    mapping = {}
    while index < len(lines):
        line = lines[index]
        current_indent = line_indent(line)
        if current_indent < indent:
            break
        if current_indent != indent:
            raise ValueError(f"Unexpected indentation: {line}")

        key, value = split_key_value(line.strip())
        index += 1
        if value:
            mapping[key] = parse_scalar(value)
        else:
            child, index = parse_block(lines, index, indent + 2)
            mapping[key] = child

    return mapping, index


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
        lines = [line.rstrip() for line in raw_lines if line.strip() and not line.lstrip().startswith("#")]
        parsed, index = parse_block(lines, 0, 0)
        if index != len(lines):
            raise ValueError("Could not parse full YAML file")
        if not isinstance(parsed, dict):
            raise ValueError("Profile YAML must be a mapping")
        return parsed

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Profile YAML must be a mapping")
    return data


def html_list(items: list[str]) -> str:
    return "\n".join(f"          <li>{escape(str(item))}</li>" for item in items)


def render(profile: dict[str, Any]) -> str:
    name = str(profile.get("name", ""))
    username = str(profile.get("public_username", ""))
    site_url = str(profile.get("site_url", ""))
    position = profile.get("current_position", {})
    advisor = profile.get("advisor", {})
    education = profile.get("education", [])
    interests = profile.get("skills_and_interests", [])

    title = str(position.get("title", ""))
    department = str(position.get("department", ""))
    institution = str(position.get("institution", ""))
    position_line = ", ".join(part for part in [title, department, institution] if part)

    education_items = []
    for item in education:
        degree = str(item.get("degree", ""))
        field = str(item.get("field", ""))
        edu_department = str(item.get("department", ""))
        edu_institution = str(item.get("institution", ""))
        year = str(item.get("year", ""))
        credential = " in ".join(part for part in [degree, field] if part)
        details = ", ".join(part for part in [edu_department, edu_institution, year] if part)
        education_items.append(f"{credential}, {details}" if details else credential)

    advisor_name = str(advisor.get("name", ""))
    advisor_website = str(advisor.get("website", ""))

    return f"""<!doctype html>
<!-- Generated from data/profile.yml by scripts/render_site.py. -->
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(name or username)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f8f7f3;
      --text: #1f2a2e;
      --muted: #5d686d;
      --accent: #0d6b70;
      --rule: #d8d2c6;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}

    main {{
      width: min(760px, calc(100% - 32px));
      margin: 0 auto;
      padding: 64px 0;
    }}

    header {{
      padding-bottom: 32px;
      border-bottom: 1px solid var(--rule);
    }}

    .eyebrow {{
      margin: 0 0 8px;
      color: var(--accent);
      font-size: 0.9rem;
      font-weight: 700;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      font-size: 2.6rem;
      line-height: 1.1;
    }}

    h2 {{
      margin: 0 0 12px;
      font-size: 1.1rem;
    }}

    p {{
      margin: 12px 0 0;
    }}

    a {{
      color: var(--accent);
    }}

    section {{
      padding: 28px 0;
      border-bottom: 1px solid var(--rule);
    }}

    ul {{
      margin: 0;
      padding-left: 20px;
    }}

    .muted {{
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="eyebrow">Personal website</p>
      <h1>{escape(name)}</h1>
      <p>{escape(position_line)}</p>
      <p><a href="{escape(site_url)}">{escape(username)}</a></p>
    </header>

    <section>
      <h2>Education</h2>
      <ul>
{html_list(education_items)}
      </ul>
    </section>

    <section>
      <h2>Advisor</h2>
      <p><a href="{escape(advisor_website)}">{escape(advisor_name)}</a></p>
    </section>

    <section>
      <h2>Skills and Interests</h2>
      <ul>
{html_list(interests)}
      </ul>
    </section>

    <section>
      <h2>About This Site</h2>
      <p class="muted">This site is generated from a small public profile file and will grow over time.</p>
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    profile = load_yaml(PROFILE_PATH)
    INDEX_PATH.write_text(render(profile), encoding="utf-8")
    print(f"Rendered {INDEX_PATH.relative_to(ROOT)} from {PROFILE_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
