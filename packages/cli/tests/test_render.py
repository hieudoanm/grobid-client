"""Tests for grobid.render."""

from lxml import etree

from grobid.render import (
    convert_tei_to_md,
    first_element,
    inline,
    render,
    render_children,
    render_list,
    render_table,
)


def test_inline_basic():
    xml = """<p xmlns="http://www.tei-c.org/ns/1.0">Hello world</p>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = inline(root)
    assert result == "Hello world"


def test_inline_italic():
    xml = """<p xmlns="http://www.tei-c.org/ns/1.0">Hello <hi rend="italic">world</hi></p>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = inline(root)
    assert "*world*" in result


def test_inline_bold():
    xml = """<p xmlns="http://www.tei-c.org/ns/1.0">Hello <hi rend="bold">world</hi></p>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = inline(root)
    assert "**world**" in result


def test_inline_ref_with_url():
    xml = """<p xmlns="http://www.tei-c.org/ns/1.0">See <ref target="https://example.com">here</ref></p>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = inline(root)
    assert "[here](https://example.com)" in result


def test_inline_ref_without_url():
    xml = """<p xmlns="http://www.tei-c.org/ns/1.0">See <ref target="#section">here</ref></p>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = inline(root)
    assert "here" in result
    assert "http" not in result


def test_inline_lb():
    xml = """<p xmlns="http://www.tei-c.org/ns/1.0">Line 1<lb/>Line 2</p>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = inline(root)
    # lb produces " \n" (space + newline) after regex normalization
    assert "\n" in result
    assert "Line 1" in result
    assert "Line 2" in result


def test_inline_tail():
    xml = """<p xmlns="http://www.tei-c.org/ns/1.0">Before <hi rend="italic">middle</hi> after</p>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = inline(root)
    assert "Before" in result
    assert "*middle*" in result
    assert "after" in result


def test_render_list():
    xml = """<list xmlns="http://www.tei-c.org/ns/1.0"><item><p>A</p></item><item><p>B</p></item></list>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render_list(root)
    assert "- A" in result
    assert "- B" in result


def test_render_list_nested():
    xml = """<list xmlns="http://www.tei-c.org/ns/1.0"><item><p>A</p><list><item><p>A1</p></item></list></item></list>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render_list(root)
    assert "- A" in result
    assert "  - A1" in result


def test_render_list_empty_item():
    xml = """<list xmlns="http://www.tei-c.org/ns/1.0"><item/></list>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render_list(root)
    assert "- " in result


def test_render_table():
    xml = """<table xmlns="http://www.tei-c.org/ns/1.0"><row><cell>H1</cell><cell>H2</cell></row><row><cell>a</cell><cell>b</cell></row></table>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render_table(root)
    assert "| H1 | H2 |" in result
    assert "| --- | --- |" in result
    assert "| a | b |" in result


def test_render_table_empty():
    xml = """<table xmlns="http://www.tei-c.org/ns/1.0"></table>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render_table(root)
    assert result == ""


def test_render_table_uneven_rows():
    xml = """<table xmlns="http://www.tei-c.org/ns/1.0"><row><cell>H1</cell><cell>H2</cell></row><row><cell>a</cell></row></table>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render_table(root)
    assert "| H1 | H2 |" in result
    assert "| a |  |" in result


def test_render_head():
    xml = """<head xmlns="http://www.tei-c.org/ns/1.0">Introduction</head>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render(root, 2)
    assert "## Introduction" in result


def test_render_p():
    xml = """<p xmlns="http://www.tei-c.org/ns/1.0">Paragraph text</p>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render(root, 2)
    assert result == "Paragraph text"


def test_render_formula():
    xml = """<formula xmlns="http://www.tei-c.org/ns/1.0">E = mc^2</formula>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render(root, 2)
    assert "$$\nE = mc^2\n$$" == result


def test_render_figure_with_graphic():
    xml = """<figure xmlns="http://www.tei-c.org/ns/1.0"><label>Fig 1</label><figDesc>A figure</figDesc><graphic url="fig1.png"/></figure>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render(root, 2)
    assert "![Fig 1 A figure](fig1.png)" == result


def test_render_figure_without_graphic():
    xml = """<figure xmlns="http://www.tei-c.org/ns/1.0"><label>Fig 1</label><figDesc>A figure</figDesc></figure>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render(root, 2)
    assert "> Fig 1 A figure" == result


def test_render_div():
    xml = """<div xmlns="http://www.tei-c.org/ns/1.0"><head>Section</head><p>Content</p></div>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render(root, 2)
    assert "### Section" in result
    assert "Content" in result


def test_render_unknown_tag():
    xml = """<unknown xmlns="http://www.tei-c.org/ns/1.0">text</unknown>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render(root, 2)
    assert result == ""


def test_render_children():
    xml = (
        """<div xmlns="http://www.tei-c.org/ns/1.0"><p>Para 1</p><p>Para 2</p></div>"""
    )
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = render_children(root, 2)
    assert "Para 1" in result
    assert "Para 2" in result
    assert "\n\n" in result


def test_first_element_found():
    xml = """<root xmlns:tei="http://www.tei-c.org/ns/1.0"><tei:p>test</tei:p></root>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    elem = first_element(root, ".//tei:p")
    assert elem is not None
    assert etree.QName(elem).localname == "p"


def test_first_element_not_found():
    xml = """<root xmlns:tei="http://www.tei-c.org/ns/1.0"><tei:p>test</tei:p></root>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    elem = first_element(root, ".//tei:div")
    assert elem is None


def test_convert_tei_to_md_full(tmp_path):
    tei_content = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title level="a">Test Article</title></titleStmt>
      <sourceDesc>
        <biblStruct>
          <analytic>
            <author><persName><forename>John</forename><surname>Doe</surname></persName></author>
          </analytic>
          <monogr>
            <title level="j">Journal</title>
            <imprint><date when="2023"/></imprint>
          </monogr>
        </biblStruct>
      </sourceDesc>
    </fileDesc>
    <profileDesc>
      <abstract><p>Abstract text.</p></abstract>
    </profileDesc>
  </teiHeader>
  <text>
    <body>
      <div><head>Introduction</head><p>Hello world.</p></div>
    </body>
  </text>
</TEI>
"""
    tei_file = tmp_path / "test.tei.xml"
    tei_file.write_text(tei_content)
    result = convert_tei_to_md(tei_file)
    assert result.startswith("---\n")
    assert "# Test Article" in result
    assert "**Authors:** John Doe" in result
    assert "## Abstract" in result
    assert "Abstract text." in result
    assert "## Article" in result
    assert "### Introduction" in result
    assert "Hello world." in result


def test_convert_tei_to_md_with_references(tmp_path):
    tei_content = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title level="a">Test</title></titleStmt>
      <sourceDesc><biblStruct><analytic/><monogr><title level="j">J</title><imprint/></monogr></biblStruct></sourceDesc>
    </fileDesc>
  </teiHeader>
  <text>
    <body/>
    <back>
      <listBibl>
        <biblStruct>Reference 1</biblStruct>
        <bibl>Reference 2</bibl>
      </listBibl>
    </back>
  </text>
</TEI>
"""
    tei_file = tmp_path / "refs.tei.xml"
    tei_file.write_text(tei_content)
    result = convert_tei_to_md(tei_file)
    assert "## References" in result
    assert "Reference 1" in result
    assert "Reference 2" in result


def test_convert_tei_to_md_no_abstract_no_body(tmp_path):
    tei_content = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title level="a">Test</title></titleStmt>
      <sourceDesc><biblStruct><analytic/><monogr><title level="j">J</title><imprint/></monogr></biblStruct></sourceDesc>
    </fileDesc>
  </teiHeader>
  <text><body/></text>
</TEI>
"""
    tei_file = tmp_path / "empty.tei.xml"
    tei_file.write_text(tei_content)
    result = convert_tei_to_md(tei_file)
    assert "# Test" in result
    assert "## Abstract" not in result
    assert "## Article" not in result


def test_convert_tei_to_md_with_meta_override(tmp_path):
    tei_content = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title level="a">Original</title></titleStmt>
      <sourceDesc><biblStruct><analytic/><monogr><title level="j">J</title><imprint/></monogr></biblStruct></sourceDesc>
    </fileDesc>
  </teiHeader>
  <text><body/></text>
</TEI>
"""
    tei_file = tmp_path / "override.tei.xml"
    tei_file.write_text(tei_content)
    meta = {"title": "Overridden", "authors": ["Override Author"]}
    result = convert_tei_to_md(tei_file, meta)
    assert 'title: "Overridden"' in result
    assert 'authors: "Override Author"' in result
