"""Metadata extraction."""

from lxml import etree

from .config import META_FIELDS, NS
from .render import first_element, inline
from .utils import text_content, yaml_string


def frontmatter(meta: dict) -> str:
    lines = ["---"]
    for field in META_FIELDS:
        value = meta.get(field)
        if value is None:
            value = ""
        if field == "authors" and isinstance(value, list):
            value = ", ".join(value)
        value = str(value).strip()
        if field == "year" and value.isdigit():
            lines.append(f"{field}: {value}")
        else:
            lines.append(f"{field}: {yaml_string(value)}")
    lines.append("---")
    return "\n".join(lines)


def extract_metadata_from_tei(tei_path):
    import re

    parser = etree.XMLParser(resolve_entities=False, no_network=True, recover=False)
    root = etree.parse(str(tei_path), parser).getroot()

    meta = {
        "title": "",
        "authors": [],
        "year": "",
        "journal": "",
        "volume": "",
        "issue": "",
        "pages": "",
        "doi": "",
        "doi_link": "",
    }

    title_node = first_element(
        root,
        "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title",
    )
    if title_node is not None:
        meta["title"] = inline(title_node)

    author_nodes = root.xpath(
        "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc//tei:biblStruct[1]/"
        "tei:analytic/tei:author",
        namespaces=NS,
    )
    for author in author_nodes:
        name = " ".join(
            author.xpath(
                ".//tei:forename//text() | .//tei:surname//text()", namespaces=NS
            )
        )
        name = re.sub(r"\s+", " ", name).strip()
        if name:
            meta["authors"].append(name)

    monogr = first_element(
        root,
        "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc//tei:biblStruct[1]/"
        "tei:monogr",
    )
    if monogr is not None:
        journal_node = first_element(monogr, "./tei:title[@level='j']")
        if journal_node is not None:
            meta["journal"] = inline(journal_node)
        date_node = first_element(monogr, "./tei:imprint/tei:date")
        if date_node is not None:
            when = date_node.get("when") or date_node.get("notBefore") or ""
            if when:
                meta["year"] = when[:4]
        vol_node = first_element(monogr, "./tei:imprint/tei:biblScope[@unit='volume']")
        if vol_node is not None:
            meta["volume"] = text_content(vol_node)
        issue_node = first_element(monogr, "./tei:imprint/tei:biblScope[@unit='issue']")
        if issue_node is not None:
            meta["issue"] = text_content(issue_node)
        pages_node = first_element(monogr, "./tei:imprint/tei:biblScope[@unit='page']")
        if pages_node is not None:
            meta["pages"] = text_content(pages_node)

    doi_node = root.xpath(
        "//tei:teiHeader//tei:idno[@type='DOI']",
        namespaces=NS,
    )
    if doi_node:
        doi = text_content(doi_node[0])
        meta["doi"] = doi
        if doi and not doi.startswith("http"):
            meta["doi_link"] = f"https://doi.org/{doi}"
        else:
            meta["doi_link"] = doi

    return meta
