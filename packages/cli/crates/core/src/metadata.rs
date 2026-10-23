//! Metadata extraction from TEI XML.

use crate::config::META_FIELDS;
use crate::render::{find_all, first_element, inline};
use crate::utils::{text_content, yaml_string};

/// Build YAML frontmatter string from a metadata map.
pub fn frontmatter(meta: &Metadata) -> String {
    let mut lines: Vec<String> = vec!["---".to_string()];
    for field in META_FIELDS {
        let value = match field.to_string().as_str() {
            "authors" => {
                if meta.authors.is_empty() {
                    String::new()
                } else {
                    meta.authors.join(", ")
                }
            }
            "year" => meta.year.clone().unwrap_or_default(),
            _ => match field.to_string().as_str() {
                "title" => meta.title.clone().unwrap_or_default(),
                "journal" => meta.journal.clone().unwrap_or_default(),
                "volume" => meta.volume.clone().unwrap_or_default(),
                "issue" => meta.issue.clone().unwrap_or_default(),
                "pages" => meta.pages.clone().unwrap_or_default(),
                "doi" => meta.doi.clone().unwrap_or_default(),
                "doi_link" => meta.doi_link.clone().unwrap_or_default(),
                _ => String::new(),
            },
        };
        if field == &"year" && !value.is_empty() && value.chars().all(|c| c.is_ascii_digit()) {
            lines.push(format!("year: {value}"));
        } else {
            lines.push(format!("{}: {}", field, yaml_string(&value)));
        }
    }
    lines.push("---".to_string());
    lines.join(
        "
",
    )
}

/// Metadata extracted from a TEI document.
#[derive(Debug, Clone, Default)]
pub struct Metadata {
    pub title: Option<String>,
    pub authors: Vec<String>,
    pub year: Option<String>,
    pub journal: Option<String>,
    pub volume: Option<String>,
    pub issue: Option<String>,
    pub pages: Option<String>,
    pub doi: Option<String>,
    pub doi_link: Option<String>,
}

/// Extract metadata from a TEI XML file.
pub fn extract_metadata_from_tei(tei_path: &std::path::Path) -> anyhow::Result<Metadata> {
    let content = std::fs::read_to_string(tei_path)?;
    let doc = roxmltree::Document::parse(&content)?;
    let root = doc.root();

    let mut meta = Metadata::default();

    // Try to find title
    let title_node = first_element(
        root,
        "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title",
    );
    if let Some(node) = title_node {
        let t = inline(node);
        if !t.is_empty() {
            let mut tc = t.clone();
            if tc.len() > 10 {
                let mid = tc.len() / 2;
                let (a, b) = tc.split_at(mid);
                if a.trim() == b.trim() && !a.trim().is_empty() {
                    tc = a.trim().to_string();
                }
            }
            meta.title = Some(tc);
        }
    }
    if meta.title.as_ref().is_none_or(|t| t.is_empty()) {
        if let Some(tei) = if root.is_element() && root.tag_name().name() == "TEI" {
            Some(root)
        } else {
            root.children()
                .find(|n| n.is_element() && n.tag_name().name() == "TEI")
        } {
            if let Some(header) = crate::render::find_element_by_tag_pub(tei, "teiHeader") {
                if let Some(file_desc) = crate::render::find_element_by_tag_pub(header, "fileDesc")
                {
                    if let Some(title_stmt) =
                        crate::render::find_element_by_tag_pub(file_desc, "titleStmt")
                    {
                        for child in title_stmt.children() {
                            if child.is_element() && child.tag_name().name() == "title" {
                                let t = inline(child);
                                if !t.is_empty() {
                                    meta.title = Some(t.clone());
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Find authors
    let mut author_nodes = find_all(root, "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc//tei:biblStruct[1]/tei:analytic/tei:author");
    if author_nodes.is_empty() {
        fn search_authors<'a>(
            n: roxmltree::Node<'a, 'a>,
            results: &mut Vec<roxmltree::Node<'a, 'a>>,
        ) {
            if n.is_element() && n.tag_name().name() == "author" {
                results.push(n);
                return;
            }
            for child in n.children() {
                search_authors(child, results);
            }
        }
        search_authors(root, &mut author_nodes);
    }
    for author in author_nodes {
        let mut name_parts: Vec<String> = Vec::new();
        for n in author.descendants() {
            if n.is_element()
                && (n.tag_name().name() == "forename" || n.tag_name().name() == "surname")
            {
                if let Some(t) = n.text() {
                    name_parts.push(t.to_string());
                }
            }
        }
        let name = name_parts.join(" ");
        let name = crate::utils::collapse_whitespace(&name).trim().to_string();
        if !name.is_empty() {
            meta.authors.push(name);
        }
    }

    let monogr = first_element(
        root,
        "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc//tei:biblStruct[1]/tei:monogr",
    );
    if let Some(m) = monogr {
        if let Some(journal_node) = first_element(m, "./tei:title[@level='j']") {
            meta.journal = Some(inline(journal_node));
        }
        if let Some(date_node) = first_element(m, "./tei:imprint/tei:date") {
            let when = date_node
                .attribute("when")
                .or_else(|| date_node.attribute("notBefore"))
                .unwrap_or("");
            if !when.is_empty() {
                meta.year = Some(when[..when.len().min(4)].to_string());
            }
        }
        if let Some(vol_node) = first_element(m, "./tei:imprint/tei:biblScope[@unit='volume']") {
            meta.volume = Some(text_content(&vol_node));
        }
        if let Some(issue_node) = first_element(m, "./tei:imprint/tei:biblScope[@unit='issue']") {
            meta.issue = Some(text_content(&issue_node));
        }
        if let Some(pages_node) = first_element(m, "./tei:imprint/tei:biblScope[@unit='page']") {
            meta.pages = Some(text_content(&pages_node));
        }
    }

    let doi_nodes = find_all(root, "//tei:teiHeader//tei:idno[@type='DOI']");
    if let Some(doi_node) = doi_nodes.first() {
        let doi = text_content(doi_node);
        if !doi.is_empty() {
            let doi_link = if doi.starts_with("http") {
                doi.clone()
            } else {
                format!("https://doi.org/{doi}")
            };
            meta.doi = Some(doi);
            meta.doi_link = Some(doi_link);
        }
    }

    Ok(meta)
}
