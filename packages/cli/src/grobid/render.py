"""TEI rendering."""

import re

from lxml import etree

from .config import NS
from .utils import text_content


def inline(element):
    parts = [element.text or ""]
    for child in element:
        tag = etree.QName(child).localname
        content = inline(child)
        if tag == "hi":
            rend = (child.get("rend") or "").lower()
            if "italic" in rend:
                content = f"*{content}*"
            elif "bold" in rend:
                content = f"**{content}**"
        elif tag == "ref":
            target = child.get("target", "")
            if target.startswith(("https://", "http://")) and content:
                content = f"[{content}]({target})"
        elif tag == "lb":
            content = "  \n"
        parts.append(content)
        parts.append(child.tail or "")
    return re.sub(r"[ \t]+", " ", "".join(parts)).strip()


def render_list(element, depth: int = 0) -> str:
    lines = []
    for item in element.xpath("./tei:item", namespaces=NS):
        paragraphs = item.xpath("./tei:p", namespaces=NS)
        content = " ".join(inline(p) for p in paragraphs)
        if not content:
            content = inline(item)
        lines.append(f"{'  ' * depth}- {content}")
        for nested in item.xpath("./tei:list", namespaces=NS):
            lines.append(render_list(nested, depth + 1))
    return "\n".join(lines)


def render_table(element) -> str:
    rows = []
    for row in element.xpath(".//tei:row", namespaces=NS):
        cells = row.xpath("./tei:cell", namespaces=NS)
        rows.append([inline(cell).replace("|", r"\|") for cell in cells])
    if not rows:
        return text_content(element)
    width = max(map(len, rows))
    rows = [row + [""] * (width - len(row)) for row in rows]
    output = ["| " + " | ".join(rows[0]) + " |"]
    output.append("| " + " | ".join(["---"] * width) + " |")
    output.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return "\n".join(output)


def render(element, depth: int = 2) -> str:
    tag = etree.QName(element).localname
    if tag == "head":
        heading = inline(element)
        return f"{'#' * min(depth, 6)} {heading}"
    if tag == "p":
        return inline(element)
    if tag == "list":
        return render_list(element)
    if tag == "table":
        return render_table(element)
    if tag == "formula":
        return f"$$\n{text_content(element)}\n$$"
    if tag == "figure":
        label = " ".join(element.xpath("./tei:label//text()", namespaces=NS))
        caption = " ".join(
            element.xpath("./tei:figDesc//text() | ./tei:head//text()", namespaces=NS)
        )
        graphic = element.xpath(".//tei:graphic/@url", namespaces=NS)
        description = " ".join(x for x in [label, caption] if x)
        if graphic:
            return f"![{description}]({graphic[0]})"
        return f"> {description}" if description else ""
    if tag == "div":
        return render_children(element, depth + 1)
    return ""


def render_children(element, depth: int = 2) -> str:
    blocks = []
    for child in element:
        tag = etree.QName(child).localname
        if tag in {"head", "p", "div", "list", "table", "formula", "figure"}:
            result = render(child, depth)
            if result:
                blocks.append(result)
    return "\n\n".join(blocks)


def first_element(root, xpath: str):
    results = root.xpath(xpath, namespaces=NS)
    return results[0] if results else None


def convert_tei_to_md(input_path, meta=None) -> str:
    parser = etree.XMLParser(resolve_entities=False, no_network=True, recover=False)
    root = etree.parse(str(input_path), parser).getroot()

    title_node = first_element(
        root,
        "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title",
    )
    title = inline(title_node) if title_node is not None else input_path.stem

    author_nodes = root.xpath(
        "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc//tei:biblStruct[1]/"
        "tei:analytic/tei:author",
        namespaces=NS,
    )
    authors = []
    for author in author_nodes:
        name = " ".join(
            author.xpath(
                ".//tei:forename//text() | .//tei:surname//text()", namespaces=NS
            )
        )
        name = re.sub(r"\s+", " ", name).strip()
        if name:
            authors.append(name)

    abstract_node = first_element(root, "//tei:profileDesc/tei:abstract")
    body_node = first_element(root, "//tei:text/tei:body")

    from .metadata import extract_metadata_from_tei, frontmatter

    sections = []
    if meta is None:
        meta = extract_metadata_from_tei(input_path)
    sections.append(frontmatter(meta))
    sections.append(f"# {title}")
    if authors:
        sections.append("**Authors:** " + ", ".join(authors))
    if abstract_node is not None:
        abstract = render_children(abstract_node, 2)
        if abstract:
            sections.extend(["## Abstract", abstract])
    if body_node is not None:
        body = render_children(body_node, 2)
        if body:
            sections.extend(["## Article", body])

    references = []
    for ref in root.xpath(
        "//tei:listBibl/tei:biblStruct | //tei:listBibl/tei:bibl", namespaces=NS
    ):
        reference = text_content(ref)
        if reference:
            references.append(f"- {reference}")
    if references:
        sections.extend(["## References", "\n".join(references)])
    return "\n\n".join(sections).strip() + "\n"
