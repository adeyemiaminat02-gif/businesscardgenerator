"""
Business card templates.

Each template defines:
  - label: shown on the picker button
  - fields: list of (field_key, prompt_text) asked in order.
            If a field is optional, mention in the prompt that the user
            can send "-" to skip it.
  - render: function(dict) -> str that builds the final text card
"""


def render_classic(d: dict) -> str:
    lines = []
    lines.append("┏" + "━" * 24 + "┓")
    lines.append(f"  {d['name']}")
    lines.append(f"  {d['title']} @ {d['company']}")
    lines.append("┗" + "━" * 24 + "┛")
    lines.append(f"📞 {d['phone']}")
    lines.append(f"✉️ {d['email']}")
    if d.get("website") and d["website"] != "-":
        lines.append(f"🌐 {d['website']}")
    return "\n".join(lines)


def render_minimal(d: dict) -> str:
    lines = [
        d["name"].upper(),
        d["title"],
        "",
        f"{d['phone']} · {d['email']}",
    ]
    return "\n".join(lines)


def render_modern(d: dict) -> str:
    lines = []
    lines.append(f"✨ {d['name']} ✨")
    lines.append(f"🏢 {d['company']}")
    lines.append("─" * 20)
    lines.append(f"📱 {d['phone']}")
    lines.append(f"📧 {d['email']}")
    if d.get("website") and d["website"] != "-":
        lines.append(f"🌐 {d['website']}")
    if d.get("address") and d["address"] != "-":
        lines.append(f"📍 {d['address']}")
    return "\n".join(lines)


TEMPLATES = {
    "classic": {
        "label": "🎩 Classic",
        "fields": [
            ("name", "What's your full name?"),
            ("title", "What's your job title?"),
            ("company", "What's your company name?"),
            ("phone", "What's your phone number?"),
            ("email", "What's your email address?"),
            ("website", "What's your website? (send - to skip)"),
        ],
        "render": render_classic,
    },
    "minimal": {
        "label": "◽ Minimal",
        "fields": [
            ("name", "What's your full name?"),
            ("title", "What's your job title?"),
            ("phone", "What's your phone number?"),
            ("email", "What's your email address?"),
        ],
        "render": render_minimal,
    },
    "modern": {
        "label": "✨ Modern",
        "fields": [
            ("name", "What's your full name?"),
            ("company", "What's your company name?"),
            ("phone", "What's your phone number?"),
            ("email", "What's your email address?"),
            ("website", "What's your website? (send - to skip)"),
            ("address", "What's your office address? (send - to skip)"),
        ],
        "render": render_modern,
    },
}
