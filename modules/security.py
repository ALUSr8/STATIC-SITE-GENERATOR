import re
from urllib.parse import urlparse


ALLOWED_FONT_FAMILIES = {
    "Arial",
    "Helvetica",
    "Verdana",
    "Tahoma",
    "Trebuchet MS",
    "Georgia",
    "Times New Roman",
    "Courier New",
    "Segoe UI",
    "Roboto",
    "Open Sans",
    "Lato",
}

DEFAULT_COLORS = {
    "primary_color": "#2563eb",
    "secondary_color": "#1e40af",
    "background_color": "#ffffff",
    "text_color": "#111111",
}

COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def safe_link_url(value, default="#"):
    """Allow relative links and common web/contact schemes only."""
    value = (value or "").strip()

    if value == "":
        return default

    parsed = urlparse(value)

    if parsed.scheme.lower() in {"http", "https", "mailto", "tel"}:
        return value

    if parsed.scheme == "" and not value.startswith("//"):
        return value

    return default


def safe_video_url(value):
    """Return a YouTube embed URL, or an empty value when unsupported."""
    value = (value or "").strip()
    parsed = urlparse(value)
    host = parsed.netloc.lower()

    if host in {"www.youtube.com", "youtube.com"}:
        video_id = parsed.query.split("v=", 1)[-1].split("&", 1)[0]
    elif host == "youtu.be":
        video_id = parsed.path.strip("/")
    else:
        return ""

    if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", video_id or ""):
        return f"https://www.youtube.com/embed/{video_id}"

    return ""


def safe_theme_values(font_family, primary_color, secondary_color,
                      background_color, text_color):
    colors = {
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "background_color": background_color,
        "text_color": text_color,
    }

    normalized = {
        key: value.lower() if isinstance(value, str) and COLOR_PATTERN.fullmatch(value)
        else DEFAULT_COLORS[key]
        for key, value in colors.items()
    }
    normalized["font_family"] = (
        font_family if font_family in ALLOWED_FONT_FAMILIES else "Arial"
    )

    return normalized
