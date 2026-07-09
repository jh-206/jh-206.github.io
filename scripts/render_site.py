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


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def link(label: str, url: str, class_name: str = "") -> str:
    class_attr = f' class="{escape(class_name)}"' if class_name else ""
    return f'<a{class_attr} href="{escape(url)}">{escape(label)}</a>'


def compact_list(items: list[Any]) -> str:
    return "\n".join(f"        <li>{escape(str(item))}</li>" for item in items)


def render_tags(items: list[Any]) -> str:
    return "\n".join(f"        <li>{escape(str(item))}</li>" for item in items)


def find_profile_link(profile: dict[str, Any], label: str) -> dict[str, Any]:
    for item in as_list(profile.get("links")):
        item = as_mapping(item)
        if str(item.get("label", "")).lower() == label.lower():
            return item
    return {}


def render_link_row(profile: dict[str, Any]) -> str:
    links = []
    cv = as_mapping(profile.get("cv"))
    if cv.get("pdf_path"):
        links.append(link("CV", str(cv["pdf_path"])))
    for item in as_list(profile.get("links")):
        item = as_mapping(item)
        label = str(item.get("label", ""))
        url = str(item.get("url", ""))
        if label and url:
            links.append(link(label, url))
    if not links:
        return ""
    return "\n      ".join(links)


def render_education(items: list[Any]) -> str:
    rows = []
    for item in items:
        item = as_mapping(item)
        degree = str(item.get("degree", ""))
        field = str(item.get("field", ""))
        department = str(item.get("department", ""))
        institution = str(item.get("institution", ""))
        year = str(item.get("year", ""))
        credential = ", ".join(part for part in [degree, field] if part)
        details = ", ".join(part for part in [department, institution] if part)
        year_html = f'<span class="date">{escape(year)}</span>' if year else ""
        rows.append(
            f"""        <li>
          <span><strong>{escape(credential)}</strong>{", " if details else ""}{escape(details)}</span>
          {year_html}
        </li>"""
        )
    return "\n".join(rows)


def render_advisor(advisor: dict[str, Any]) -> str:
    name = str(advisor.get("name", ""))
    website = str(advisor.get("website", ""))
    if not name:
        return ""
    advisor_html = link(name, website) if website else escape(name)
    return f"""
    <section class="section-row">
      <h2>Advisor</h2>
      <div>
        <p>{advisor_html}</p>
      </div>
    </section>
"""


def render_featured_card(
    title: str,
    meta: str,
    description: str,
    url: str,
    action_label: str,
    secondary_links: list[str] | None = None,
    detail: str = "",
) -> str:
    secondary_links = secondary_links or []
    detail_html = f'\n          <p class="card-detail">{escape(detail)}</p>' if detail else ""
    secondary_html = (
        f'\n          <p class="secondary-links">{" ".join(secondary_links)}</p>'
        if secondary_links
        else ""
    )
    action_html = f"\n          <p>{link(action_label, url, 'card-action')}</p>" if url else ""
    return f"""        <article class="feature-card">
          <p class="card-meta">{escape(meta)}</p>
          <h3>{escape(title)}</h3>{detail_html}
          <p>{escape(description)}</p>{action_html}{secondary_html}
        </article>"""


def render_featured_cards(profile: dict[str, Any]) -> str:
    cards = []
    cv = as_mapping(profile.get("cv"))
    if cv.get("pdf_path"):
        cards.append(
            render_featured_card(
                "Curriculum Vitae",
                "PDF",
                "Current academic CV.",
                str(cv["pdf_path"]),
                "Download CV",
            )
        )

    for item in as_list(profile.get("featured_links")):
        item = as_mapping(item)
        title = str(item.get("title", ""))
        item_type = str(item.get("type", "")).title()
        year = str(item.get("year", ""))
        dates = str(item.get("dates", ""))
        venue = str(item.get("venue", ""))
        url = str(item.get("url", ""))
        description = str(item.get("description", ""))
        secondary_links = []

        meta = " / ".join(part for part in [item_type, year] if part)
        detail = " / ".join(part for part in [dates, venue] if part)
        action_label = "Open link"
        if item_type.lower() == "talk":
            action_label = "Watch video"
        elif item_type.lower() == "recognition":
            action_label = "Read report"

        for secondary in as_list(item.get("secondary_links")):
            secondary = as_mapping(secondary)
            label = str(secondary.get("label", ""))
            secondary_url = str(secondary.get("url", ""))
            if label and secondary_url:
                secondary_links.append(link(label, secondary_url))

        cards.append(
            render_featured_card(
                title,
                meta,
                description,
                url,
                action_label,
                secondary_links,
                detail,
            )
        )

    scholar = find_profile_link(profile, "Google Scholar")
    if scholar:
        cards.append(
            render_featured_card(
                "Google Scholar",
                "Profile",
                "Publication and citation profile.",
                str(scholar.get("url", "")),
                "View profile",
            )
        )

    if not cards:
        return ""

    return f"""
    <section class="featured-section">
      <div class="section-heading">
        <h2>Featured</h2>
        <p>Selected profile links, recognition, and invited talks.</p>
      </div>
      <div class="feature-grid">
{chr(10).join(cards)}
      </div>
    </section>
"""


def render_other_activities(items: list[Any]) -> str:
    if not items:
        return ""
    rows = []
    for item in items:
        item = as_mapping(item)
        role = str(item.get("role", ""))
        organization = str(item.get("organization", ""))
        description = str(item.get("description", ""))
        url = str(item.get("url", ""))
        title = ", ".join(part for part in [role, organization] if part)
        title_html = link(title, url) if url else escape(title)
        rows.append(f"        <li><strong>{title_html}</strong>. {escape(description)}</li>")
    return f"""
    <section class="section-row">
      <h2>Other</h2>
      <div>
        <ul>
{chr(10).join(rows)}
        </ul>
      </div>
    </section>
"""


def render(profile: dict[str, Any]) -> str:
    name = str(profile.get("name", ""))
    username = str(profile.get("public_username", ""))
    position = as_mapping(profile.get("current_position"))
    advisor = as_mapping(profile.get("advisor"))
    education = as_list(profile.get("education"))
    interests = as_list(profile.get("skills_and_interests"))
    other_activities = as_list(profile.get("other_activities"))
    research_summary = str(profile.get("research_summary", ""))

    title = str(position.get("title", ""))
    department = str(position.get("department", ""))
    institution = str(position.get("institution", ""))
    affiliation = ", ".join(part for part in [department, institution] if part)
    position_line = ", ".join(part for part in [title, affiliation] if part)

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
      --bg: #ffffff;
      --band: #f5f9f8;
      --card: #ffffff;
      --text: #223036;
      --muted: #667276;
      --accent: #146c78;
      --warm: #8a5a12;
      --rule: #dbe2e2;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 17px;
      line-height: 1.6;
    }}

    .wrap {{
      width: min(980px, calc(100% - 32px));
      margin: 0 auto;
    }}

    .site-header {{
      background: var(--band);
      border-top: 6px solid var(--accent);
      border-bottom: 1px solid var(--rule);
    }}

    .hero {{
      display: grid;
      gap: 22px;
      padding: 44px 0 34px;
    }}

    main {{
      padding: 28px 0 72px;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(2rem, 4vw, 3rem);
      line-height: 1.15;
      font-weight: 700;
      letter-spacing: 0;
    }}

    h2 {{
      margin: 0 0 10px;
      font-size: 1.1rem;
      font-weight: 650;
      letter-spacing: 0;
    }}

    h3 {{
      margin: 6px 0 0;
      font-size: 1.05rem;
      line-height: 1.35;
    }}

    p {{
      margin: 10px 0 0;
    }}

    a {{
      color: var(--accent);
      text-decoration: none;
    }}

    a:hover {{
      text-decoration: underline;
    }}

    section {{
      padding: 26px 0;
      border-bottom: 1px solid var(--rule);
    }}

    ul {{
      margin: 0;
      padding-left: 22px;
    }}

    li + li {{
      margin-top: 8px;
    }}

    .kicker {{
      color: var(--warm);
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      margin: 0 0 8px;
      text-transform: uppercase;
    }}

    .affiliation {{
      color: var(--muted);
      font-size: 1.02rem;
    }}

    .links {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px 14px;
      margin-top: 18px;
      font-weight: 600;
    }}

    .links a::after {{
      color: var(--muted);
      content: " /";
      font-weight: 400;
      margin-left: 14px;
    }}

    .links a:last-child::after {{
      content: "";
      margin-left: 0;
    }}

    .summary {{
      max-width: 720px;
      font-size: 1.08rem;
    }}

    .focus-band {{
      align-items: baseline;
      border-bottom: 1px solid var(--rule);
      display: grid;
      gap: 16px;
      grid-template-columns: 180px minmax(0, 1fr);
      padding: 22px 0;
    }}

    .tag-list {{
      display: grid;
      gap: 10px;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      list-style: none;
      padding-left: 0;
    }}

    .tag-list li {{
      align-items: center;
      background: #eef6f4;
      border: 1px solid #c9ddda;
      border-radius: 8px;
      color: #24484c;
      display: flex;
      font-size: 0.94rem;
      justify-content: center;
      line-height: 1.3;
      min-height: 42px;
      padding: 8px 10px;
      text-align: center;
    }}

    .featured-section {{
      padding: 30px 0;
    }}

    .section-heading {{
      align-items: baseline;
      display: flex;
      gap: 16px;
      justify-content: space-between;
      margin-bottom: 16px;
    }}

    .section-heading p {{
      color: var(--muted);
      margin: 0;
    }}

    .feature-grid {{
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}

    .feature-card {{
      background: var(--card);
      border: 1px solid var(--rule);
      border-radius: 8px;
      padding: 18px;
    }}

    .feature-card p {{
      margin-top: 8px;
    }}

    .card-meta {{
      color: var(--warm);
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      margin: 0;
      text-transform: uppercase;
    }}

    .card-detail {{
      color: var(--muted);
      font-size: 0.94rem;
    }}

    .card-action {{
      font-weight: 700;
    }}

    .secondary-links {{
      font-weight: 600;
    }}

    .section-row {{
      display: grid;
      gap: 24px;
      grid-template-columns: 180px minmax(0, 1fr);
    }}

    .education-list {{
      display: grid;
      gap: 10px;
      list-style: none;
      padding-left: 0;
    }}

    .education-list li {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: baseline;
    }}

    .date,
    .muted {{
      color: var(--muted);
    }}

    .site-footer {{
      color: var(--muted);
      font-size: 0.9rem;
      padding: 22px 0 40px;
    }}

    .site-footer p {{
      margin: 0;
    }}

    @media (max-width: 760px) {{
      main {{
        padding-top: 18px;
      }}

      h1 {{
        font-size: 1.9rem;
      }}

      .focus-band,
      .section-row {{
        grid-template-columns: 1fr;
      }}

      .feature-grid {{
        grid-template-columns: 1fr;
      }}

      .tag-list {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}

      .section-heading {{
        align-items: flex-start;
        flex-direction: column;
        gap: 4px;
      }}

      .education-list li {{
        grid-template-columns: 1fr;
        gap: 2px;
      }}
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="wrap hero">
      <div>
        <p class="kicker">Academic website</p>
      <h1>{escape(name)}</h1>
      <p class="affiliation">{escape(position_line)}</p>
        <p class="summary">{escape(research_summary)}</p>
      <nav class="links" aria-label="Profile links">
      {render_link_row(profile)}
      </nav>
      </div>
    </div>
  </header>

  <main class="wrap">
    <section class="focus-band" aria-label="Research focus">
      <h2>Research Focus</h2>
      <ul class="tag-list">
{render_tags(interests)}
      </ul>
    </section>
{render_featured_cards(profile)}

    <section class="section-row">
      <h2>Education</h2>
      <div>
        <ul class="education-list">
{render_education(education)}
        </ul>
      </div>
    </section>
{render_advisor(advisor)}
{render_other_activities(other_activities)}
  </main>

  <footer class="wrap site-footer">
    <p>Site generated from structured profile data with assistance from Codex.</p>
  </footer>
</body>
</html>
"""


def main() -> None:
    profile = load_yaml(PROFILE_PATH)
    INDEX_PATH.write_text(render(profile), encoding="utf-8")
    print(f"Rendered {INDEX_PATH.relative_to(ROOT)} from {PROFILE_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
