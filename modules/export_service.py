import os
import re
import shutil
from html import escape
from urllib.parse import quote

from modules.component_service import get_components_by_page
from modules.page_service import get_pages_by_project
from modules.theme_service import ensure_theme
from modules.security import safe_link_url, safe_theme_values, safe_video_url


def safe_folder_name(name):

    safe_name = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        name
    ).strip(" .")

    return safe_name or "project"


def page_filename(page):

    if page["slug"] == "index":
        return "index.html"

    safe_slug = re.sub(
        r"[^a-z0-9-]+",
        "-",
        page["slug"].lower()
    ).strip("-")

    return f"{safe_slug or 'page'}.html"


def asset_filename(path):

    return os.path.basename(
        path or ""
    )


def asset_href(path):

    filename = asset_filename(path)

    if filename == "":
        return ""

    return "assets/" + quote(filename)


def collect_asset_paths(components):

    asset_paths = []

    for component in components:

        data = component["component_data"]

        if component["component_type"] == "image":

            image_path = asset_filename(
                data.get("image_path", "")
            )

            if image_path:
                asset_paths.append(image_path)

        elif component["component_type"] == "gallery":

            for image in data.get("images", []):

                if isinstance(image, dict):
                    image_path = asset_filename(
                        image.get("image_path", "")
                    )
                else:
                    image_path = asset_filename(image)

                if image_path:
                    asset_paths.append(image_path)

    return asset_paths


def copy_assets(project_folder, component_groups):

    asset_paths = []

    for components in component_groups:
        asset_paths.extend(
            collect_asset_paths(components)
        )

    asset_paths = list(
        dict.fromkeys(asset_paths)
    )

    if len(asset_paths) == 0:
        return

    assets_folder = os.path.join(
        project_folder,
        "assets"
    )

    os.makedirs(
        assets_folder,
        exist_ok=True
    )

    for image_path in asset_paths:

        source_path = os.path.join(
            "user_uploads",
            image_path
        )

        if not os.path.exists(source_path):
            raise ValueError(
                f"Missing uploaded asset: {image_path}"
            )

        shutil.copy2(
            source_path,
            os.path.join(
                assets_folder,
                image_path
            )
        )


def render_navigation(pages):

    links = []

    for page in pages:
        links.append(
            '<a href="{}">{}</a>'.format(
                page_filename(page),
                escape(page["title"])
            )
        )

    return """
    <header class="site-header">
        <nav aria-label="Site navigation">
            {}
        </nav>
    </header>
    """.format(
        "".join(links)
    )


def component_size_class(data):

    size = data.get(
        "size",
        "medium"
    )

    if size not in {
        "small",
        "medium",
        "large"
    }:
        size = "medium"

    return f"size-{size}"


def component_alignment_class(data):

    alignment = data.get(
        "alignment",
        "center"
    )

    if alignment not in {
        "left",
        "center",
        "right"
    }:
        alignment = "center"

    return f"align-{alignment}"


def video_embed_url(video_url):
    return safe_video_url(video_url)


def render_component(component):

    component_type = component["component_type"]
    data = component["component_data"]
    size_class = component_size_class(
        data
    )
    alignment_class = component_alignment_class(
        data
    )

    if component_type == "hero":
        return f"""
        <section class="hero {size_class} {alignment_class}">
            <h1>{escape(data.get('title', ''))}</h1>
            <p>{escape(data.get('subtitle', ''))}</p>
        </section>
        """

    if component_type == "text":
        content = escape(
            data.get("content", "")
        ).replace(
            "\n",
            "<br>"
        )

        return f"""
        <section class="text-section {size_class}">
            <p>{content}</p>
        </section>
        """

    if component_type == "image":
        image_url = asset_href(
            data.get("image_path", "")
        )

        if image_url == "":
            return ""

        return f"""
        <section class="image-section {size_class} {alignment_class}">
            <img src="{image_url}" alt="{escape(data.get('alt_text', ''))}">
        </section>
        """

    if component_type == "gallery":
        gallery_images = []

        for image in data.get("images", []):

            if isinstance(image, dict):
                image_path = image.get(
                    "image_path",
                    ""
                )
                alt_text = image.get(
                    "alt_text",
                    ""
                )
            else:
                image_path = image
                alt_text = ""

            image_url = asset_href(
                image_path
            )

            if image_url:
                gallery_images.append(
                    f'<img src="{image_url}" alt="{escape(alt_text)}">'
                )

        if len(gallery_images) == 0:
            return ""

        return """
        <section class="gallery-section {} {}">
            {}
        </section>
        """.format(
            size_class,
            alignment_class,
            "".join(gallery_images)
        )

    if component_type == "features":
        items = "".join(
            f"<li>{escape(item)}</li>"
            for item in data.get("items", "").splitlines()
            if item.strip()
        )

        return f"""
        <section class="feature-section {size_class}">
            <h2>{escape(data.get('heading', ''))}</h2>
            <ul>{items}</ul>
        </section>
        """

    if component_type == "cta":
        return f"""
        <section class="cta-section {size_class}">
            <h2>{escape(data.get('headline', ''))}</h2>
            <a class="site-button" href="{escape(safe_link_url(data.get('button_url')), quote=True)}">{escape(data.get('button_text', ''))}</a>
        </section>
        """

    if component_type == "testimonial":
        return f"""
        <section class="testimonial-section {size_class}">
            <blockquote>{escape(data.get('quote', ''))}</blockquote>
            <p>{escape(data.get('author', ''))}</p>
        </section>
        """

    if component_type == "pricing":
        items = "".join(
            f"<li>{escape(item)}</li>"
            for item in data.get("features", "").splitlines()
            if item.strip()
        )

        return f"""
        <section class="pricing-section {size_class}">
            <h2>{escape(data.get('plan', ''))}</h2>
            <p class="price">{escape(data.get('price', ''))}</p>
            <ul>{items}</ul>
        </section>
        """

    if component_type == "contact":
        return f"""
        <section class="contact-section {size_class}" id="contact">
            <h2>{escape(data.get('heading', ''))}</h2>
            <p>{escape(data.get('email', ''))}</p>
            <p>{escape(data.get('phone', ''))}</p>
            <p>{escape(data.get('address', ''))}</p>
        </section>
        """

    if component_type == "business_card":
        return f"""
        <section class="business-card-section {size_class}">
            <h2>{escape(data.get('name', ''))}</h2>
            <p>{escape(data.get('role', ''))} &middot; {escape(data.get('company', ''))}</p>
            <p>{escape(data.get('email', ''))}</p>
            <a href="{escape(safe_link_url(data.get('website')), quote=True)}">{escape(data.get('website', ''))}</a>
        </section>
        """

    if component_type == "product_demo":
        video_url = video_embed_url(data.get("video_url", ""))
        video_markup = ""

        if video_url:
            video_markup = f"""
            <div class="demo-video">
                <iframe src="{escape(video_url, quote=True)}" title="{escape(data.get('title', 'Product demo'))}" allowfullscreen></iframe>
            </div>
            """

        return f"""
        <section class="product-demo-section {size_class}">
            <div>
                <h2>{escape(data.get('title', ''))}</h2>
                <p>{escape(data.get('description', ''))}</p>
            </div>
            {video_markup}
            <a class="site-button" href="{escape(safe_link_url(data.get('button_url')), quote=True)}">{escape(data.get('button_text', ''))}</a>
        </section>
        """

    if component_type == "blog_post":
        return f"""
        <article class="blog-post-section {size_class}">
            <p class="post-meta">{escape(data.get('meta', ''))}</p>
            <h2>{escape(data.get('title', ''))}</h2>
            <p>{escape(data.get('excerpt', ''))}</p>
        </article>
        """

    if component_type == "portfolio":
        details = escape(
            data.get("details", "")
        ).replace(
            "\n",
            "<br>"
        )

        return f"""
        <section class="portfolio-section {size_class}">
            <h2>{escape(data.get('title', ''))}</h2>
            <p>{escape(data.get('summary', ''))}</p>
            <p>{details}</p>
        </section>
        """

    if component_type == "footer":
        return f"""
        <footer class="{size_class}">
            {escape(data.get('copyright', ''))}
        </footer>
        """

    return ""


def generate_html(project, page, pages, components):

    rendered_components = "".join(
        render_component(component)
        for component in components
    )

    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} | {project_name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    {navigation}
    <main>
        {components}
    </main>
</body>
</html>
""".format(
        page_title=escape(page["title"]),
        project_name=escape(project["name"]),
        navigation=render_navigation(pages),
        components=rendered_components
    )


def generate_css(theme):

    theme = safe_theme_values(
        theme.get("font_family"),
        theme.get("primary_color"),
        theme.get("secondary_color"),
        theme.get("background_color"),
        theme.get("text_color")
    )

    return f"""
:root {{
    --site-bg: {theme.get('background_color', '#ffffff')};
    --site-text: {theme.get('text_color', '#111111')};
    --site-primary: {theme.get('primary_color', '#2563eb')};
    --site-secondary: {theme.get('secondary_color', '#1e40af')};
    --site-card: color-mix(in srgb, var(--site-bg) 88%, var(--site-primary));
    --site-border: color-mix(in srgb, var(--site-text) 16%, transparent);
}}

* {{
    box-sizing: border-box;
}}

body {{
    background:
        radial-gradient(circle at top left, color-mix(in srgb, var(--site-primary) 13%, transparent), transparent 34rem),
        var(--site-bg);
    color: var(--site-text);
    font-family: {theme.get('font_family', 'Arial')}, Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
}}

.site-header {{
    background: color-mix(in srgb, var(--site-bg) 86%, transparent);
    border-bottom: 1px solid var(--site-border);
    padding: 18px 32px;
    position: sticky;
    top: 0;
    backdrop-filter: blur(12px);
}}

.site-header nav {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}}

.site-header a {{
    color: var(--site-primary);
    font-weight: 700;
    text-decoration: none;
    transition: color 160ms ease, transform 160ms ease;
}}

.site-header a:hover {{
    color: var(--site-secondary);
    transform: translateY(-1px);
}}

main {{
    padding: 54px 40px;
}}

.hero {{
    text-align: center;
    margin: 0 auto;
    padding: 72px 20px;
}}

.hero h1 {{
    color: var(--site-primary);
    font-size: clamp(2.2rem, 5vw, 4rem);
    margin: 0;
}}

.hero p {{
    color: var(--site-secondary);
    font-size: 1.2rem;
}}

.text-section {{
    line-height: 1.7;
    max-width: 760px;
    margin: 0 auto 32px;
}}

.size-small {{
    max-width: 680px;
}}

.size-medium {{
    max-width: 960px;
}}

.size-large {{
    max-width: 1180px;
}}

.hero.size-small {{
    padding: 42px 20px;
}}

.hero.size-large {{
    padding: 104px 20px;
}}

.hero.align-left {{
    margin-left: 0;
    margin-right: auto;
    text-align: left;
}}

.hero.align-center {{
    margin-left: auto;
    margin-right: auto;
    text-align: center;
}}

.hero.align-right {{
    margin-left: auto;
    margin-right: 0;
    text-align: right;
}}

.image-section,
.gallery-section {{
    margin: 32px auto;
}}

.image-section.align-left,
.gallery-section.align-left {{
    margin-left: 0;
    margin-right: auto;
}}

.image-section.align-center,
.gallery-section.align-center {{
    margin-left: auto;
    margin-right: auto;
}}

.image-section.align-right,
.gallery-section.align-right {{
    margin-left: auto;
    margin-right: 0;
}}

.image-section img,
.gallery-section img {{
    display: block;
    max-width: 100%;
    height: auto;
    margin: 0 auto 16px;
    border-radius: 14px;
    box-shadow: 0 18px 45px color-mix(in srgb, var(--site-text) 16%, transparent);
}}

.gallery-section {{
    display: grid;
    gap: 16px;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}}

.image-section.align-left img {{
    margin-left: 0;
    margin-right: auto;
}}

.image-section.align-center img {{
    margin-left: auto;
    margin-right: auto;
}}

.image-section.align-right img {{
    margin-left: auto;
    margin-right: 0;
}}

.gallery-section.align-left {{
    justify-items: start;
}}

.gallery-section.align-center {{
    justify-items: center;
}}

.gallery-section.align-right {{
    justify-items: end;
}}

.feature-section,
.pricing-section,
.contact-section,
.business-card-section,
.blog-post-section,
.portfolio-section,
.testimonial-section,
.cta-section,
.product-demo-section {{
    max-width: 960px;
    margin: 34px auto;
    padding: 30px;
    background: var(--site-card);
    border: 1px solid var(--site-border);
    border-radius: 16px;
    box-shadow: 0 16px 40px color-mix(in srgb, var(--site-text) 10%, transparent);
}}

.feature-section ul,
.pricing-section ul {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 14px;
    list-style: none;
    padding: 0;
}}

.feature-section li,
.pricing-section li {{
    padding: 14px;
    border-radius: 12px;
    background: color-mix(in srgb, var(--site-bg) 72%, white);
}}

.site-button {{
    display: inline-flex;
    align-items: center;
    min-height: 44px;
    padding: 0 18px;
    border-radius: 999px;
    background: var(--site-primary);
    color: #ffffff;
    font-weight: 700;
    text-decoration: none;
    transition: transform 160ms ease, filter 160ms ease;
}}

.site-button:hover {{
    filter: brightness(1.08);
    transform: translateY(-2px);
}}

.testimonial-section blockquote {{
    margin: 0;
    font-size: clamp(1.4rem, 3vw, 2.2rem);
    line-height: 1.3;
}}

.price {{
    color: var(--site-primary);
    font-size: 2rem;
    font-weight: 800;
}}

.product-demo-section {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
}}

.feature-section.size-small,
.pricing-section.size-small,
.contact-section.size-small,
.business-card-section.size-small,
.blog-post-section.size-small,
.portfolio-section.size-small,
.testimonial-section.size-small,
.cta-section.size-small,
.product-demo-section.size-small {{
    max-width: 680px;
}}

.feature-section.size-large,
.pricing-section.size-large,
.contact-section.size-large,
.business-card-section.size-large,
.blog-post-section.size-large,
.portfolio-section.size-large,
.testimonial-section.size-large,
.cta-section.size-large,
.product-demo-section.size-large {{
    max-width: 1180px;
}}

.demo-video {{
    flex: 1 1 320px;
}}

.demo-video iframe {{
    width: 100%;
    aspect-ratio: 16 / 9;
    border: 0;
    border-radius: 14px;
}}

.post-meta {{
    color: var(--site-secondary);
    font-weight: 700;
}}

footer {{
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid var(--site-border);
}}

@media (max-width: 640px) {{
    main {{
        padding: 24px 18px;
    }}

    .site-header {{
        padding: 14px 18px;
    }}

    .product-demo-section {{
        display: grid;
    }}
}}
"""


def export_project(project):

    if project is None:
        raise ValueError(
            "Cannot export a project that does not exist."
        )

    project_folder = os.path.join(
        "exports",
        safe_folder_name(project["name"])
    )

    os.makedirs(
        project_folder,
        exist_ok=True
    )

    theme = ensure_theme(
        project["id"]
    )

    pages = get_pages_by_project(
        project["id"]
    )

    if len(pages) == 0:
        raise ValueError(
            f"No pages found for project '{project['name']}'."
        )

    component_groups = []
    page_component_pairs = []

    for page in pages:
        components = get_components_by_page(
            page["id"]
        )
        component_groups.append(
            components
        )
        page_component_pairs.append(
            (
                page,
                components
            )
        )

    copy_assets(
        project_folder,
        component_groups
    )

    for page, components in page_component_pairs:
        html_content = generate_html(
            project,
            page,
            pages,
            components
        )

        with open(
            os.path.join(
                project_folder,
                page_filename(page)
            ),
            "w",
            encoding="utf-8"
        ) as file:
            file.write(
                html_content
            )

    css_content = generate_css(
        theme
    )

    with open(
        os.path.join(
            project_folder,
            "style.css"
        ),
        "w",
        encoding="utf-8"
    ) as file:
        file.write(
            css_content
        )

    return project_folder
