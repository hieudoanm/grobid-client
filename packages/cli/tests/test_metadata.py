"""Tests for grobid.metadata."""

from grobid.metadata import extract_metadata_from_tei, frontmatter


def test_frontmatter():
    meta = {
        "title": "Test Title",
        "authors": "John Doe",
        "year": "2023",
        "journal": "Nature",
        "volume": "10",
        "issue": "2",
        "pages": "100-200",
        "doi": "10.1234/test",
        "doi_link": "https://doi.org/10.1234/test",
    }
    fm = frontmatter(meta)
    assert fm.startswith("---")
    assert fm.endswith("---")
    assert 'title: "Test Title"' in fm
    assert 'authors: "John Doe"' in fm
    assert "year: 2023" in fm
    assert 'journal: "Nature"' in fm
    assert 'volume: "10"' in fm
    assert 'issue: "2"' in fm
    assert 'pages: "100-200"' in fm
    assert 'doi: "10.1234/test"' in fm
    assert 'doi_link: "https://doi.org/10.1234/test"' in fm


def test_frontmatter_authors_list():
    meta = {"title": "Test", "authors": ["John Doe", "Jane Smith"]}
    fm = frontmatter(meta)
    assert 'authors: "John Doe, Jane Smith"' in fm


def test_frontmatter_empty_values():
    meta = {}
    fm = frontmatter(meta)
    # frontmatter outputs all META_FIELDS with empty values
    assert fm.startswith("---\n")
    assert fm.endswith("\n---")
    assert 'title: ""' in fm
    assert 'authors: ""' in fm
    assert 'year: ""' in fm
    assert 'journal: ""' in fm
    assert 'volume: ""' in fm
    assert 'issue: ""' in fm
    assert 'pages: ""' in fm
    assert 'doi: ""' in fm
    assert 'doi_link: ""' in fm


def test_frontmatter_none_values():
    meta = {"title": None, "authors": None}
    fm = frontmatter(meta)
    assert 'title: ""' in fm
    assert 'authors: ""' in fm


def test_extract_metadata_from_tei_full(tmp_path):
    tei_content = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title level="a">Sample Title</title>
      </titleStmt>
      <sourceDesc>
        <biblStruct>
          <analytic>
            <author>
              <persName>
                <forename>Alice</forename>
                <surname>Smith</surname>
              </persName>
            </author>
            <author>
              <persName>
                <forename>Bob</forename>
                <surname>Jones</surname>
              </persName>
            </author>
          </analytic>
          <monogr>
            <title level="j">Nature</title>
            <imprint>
              <date when="2022"/>
              <biblScope unit="volume">10</biblScope>
              <biblScope unit="issue">2</biblScope>
              <biblScope unit="page">100-200</biblScope>
            </imprint>
          </monogr>
        </biblStruct>
      </sourceDesc>
    </fileDesc>
    <profileDesc>
      <abstract>
        <p>This is the abstract.</p>
      </abstract>
    </profileDesc>
  </teiHeader>
  <text>
    <body>
    </body>
  </text>
</TEI>
"""
    tei_file = tmp_path / "sample.tei.xml"
    tei_file.write_text(tei_content)
    meta = extract_metadata_from_tei(tei_file)
    assert meta["title"] == "Sample Title"
    assert "Alice Smith" in meta["authors"]
    assert "Bob Jones" in meta["authors"]
    assert meta["year"] == "2022"
    assert meta["journal"] == "Nature"
    assert meta["volume"] == "10"
    assert meta["issue"] == "2"
    assert meta["pages"] == "100-200"


def test_extract_metadata_from_tei_with_doi(tmp_path):
    tei_content = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title level="a">Test</title>
      </titleStmt>
      <sourceDesc>
        <biblStruct>
          <analytic/>
          <monogr>
            <title level="j">Journal</title>
            <imprint/>
          </monogr>
        </biblStruct>
      </sourceDesc>
    </fileDesc>
    <teiHeader>
      <idno type="DOI">10.1234/test.doi</idno>
    </teiHeader>
  </teiHeader>
  <text><body/></text>
</TEI>
"""
    tei_file = tmp_path / "doi.tei.xml"
    tei_file.write_text(tei_content)
    meta = extract_metadata_from_tei(tei_file)
    assert meta["doi"] == "10.1234/test.doi"
    assert meta["doi_link"] == "https://doi.org/10.1234/test.doi"


def test_extract_metadata_from_tei_with_doi_link(tmp_path):
    tei_content = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title level="a">Test</title></titleStmt>
      <sourceDesc><biblStruct><analytic/><monogr><title level="j">J</title><imprint/></monogr></biblStruct></sourceDesc>
    </fileDesc>
    <teiHeader><idno type="DOI">https://doi.org/10.1234/test</idno></teiHeader>
  </teiHeader>
  <text><body/></text>
</TEI>
"""
    tei_file = tmp_path / "doi_link.tei.xml"
    tei_file.write_text(tei_content)
    meta = extract_metadata_from_tei(tei_file)
    assert meta["doi"] == "https://doi.org/10.1234/test"
    assert meta["doi_link"] == "https://doi.org/10.1234/test"


def test_extract_metadata_from_tei_minimal(tmp_path):
    tei_content = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title level="a">Minimal</title></titleStmt>
      <sourceDesc><biblStruct><analytic/><monogr><title level="j">J</title><imprint/></monogr></biblStruct></sourceDesc>
    </fileDesc>
  </teiHeader>
  <text><body/></text>
</TEI>
"""
    tei_file = tmp_path / "minimal.tei.xml"
    tei_file.write_text(tei_content)
    meta = extract_metadata_from_tei(tei_file)
    assert meta["title"] == "Minimal"
    assert meta["authors"] == []
    assert meta["year"] == ""
    assert meta["journal"] == "J"


def test_extract_metadata_from_tei_not_before(tmp_path):
    tei_content = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title level="a">Test</title></titleStmt>
      <sourceDesc>
        <biblStruct>
          <analytic/>
          <monogr>
            <title level="j">Journal</title>
            <imprint><date notBefore="2020"/></imprint>
          </monogr>
        </biblStruct>
      </sourceDesc>
    </fileDesc>
  </teiHeader>
  <text><body/></text>
</TEI>
"""
    tei_file = tmp_path / "notbefore.tei.xml"
    tei_file.write_text(tei_content)
    meta = extract_metadata_from_tei(tei_file)
    assert meta["year"] == "2020"
