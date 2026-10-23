//! TEI rendering.

use roxmltree::Node;

use crate::metadata::{extract_metadata_from_tei, frontmatter};
use crate::utils::text_content;

/// Get namespace map for roxmltree - roxmltree uses prefixes differently,
/// easier to match by local name or just search by tag name patterns
fn find_element_by_tag<'a>(node: Node<'a, 'a>, tag: &str) -> Option<Node<'a, 'a>> {
    node.children()
        .find(|child| child.is_element() && child.tag_name().name() == tag)
}

pub fn first_element<'a>(node: Node<'a, 'a>, xpath: &str) -> Option<Node<'a, 'a>> {
    // Simplified xpath handling for common patterns used
    if xpath.contains("/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title") {
        // Look in teiHeader/fileDesc/titleStmt/title
        if let Some(tei) = node
            .children()
            .find(|n| n.is_element() && n.tag_name().name() == "TEI")
        {
            if let Some(header) = find_element_by_tag(tei, "teiHeader") {
                if let Some(file_desc) = find_element_by_tag(header, "fileDesc") {
                    if let Some(title_stmt) = find_element_by_tag(file_desc, "titleStmt") {
                        if let Some(title) = find_element_by_tag(title_stmt, "title") {
                            return Some(title);
                        }
                    }
                }
            }
        }
        return None;
    }
    if xpath == "//tei:profileDesc/tei:abstract" {
        let tei = node
            .children()
            .find(|n| n.is_element() && n.tag_name().name() == "TEI")?;
        let header = find_element_by_tag(tei, "teiHeader")?;
        let profile = find_element_by_tag(header, "profileDesc")?;
        return find_element_by_tag(profile, "abstract");
    }
    if xpath == "//tei:text/tei:body" {
        let tei = node
            .children()
            .find(|n| n.is_element() && n.tag_name().name() == "TEI")?;
        let text = find_element_by_tag(tei, "text")?;
        return find_element_by_tag(text, "body");
    }
    None
}

pub fn find_all<'a>(node: Node<'a, 'a>, xpath: &str) -> Vec<Node<'a, 'a>> {
    let mut results = Vec::new();
    // For now, handle common cases
    if xpath.contains("tei:author") {
        // search recursively
        fn search_authors<'a>(n: Node<'a, 'a>, results: &mut Vec<Node<'a, 'a>>) {
            if n.is_element() && n.tag_name().name() == "author" {
                results.push(n);
                return;
            }
            for child in n.children() {
                search_authors(child, results);
            }
        }
        search_authors(node, &mut results);
    }
    if xpath.contains("tei:listBibl") {
        fn search_listbibl<'a>(n: Node<'a, 'a>, results: &mut Vec<Node<'a, 'a>>) {
            if n.is_element() && (n.tag_name().name() == "listBibl") {
                for child in n.children() {
                    if child.is_element()
                        && (child.tag_name().name() == "biblStruct"
                            || child.tag_name().name() == "bibl")
                    {
                        results.push(child);
                    }
                }
                return;
            }
            for child in n.children() {
                search_listbibl(child, results);
            }
        }
        search_listbibl(node, &mut results);
    }
    results
}

pub fn inline(element: Node) -> String {
    let mut parts: Vec<String> = Vec::new();
    if let Some(text) = element.text() {
        parts.push(text.to_string());
    }
    for child in element.children() {
        if child.is_element() {
            let tag = child.tag_name().name();
            let content = inline(child);
            if tag == "hi" {
                let rend = child.attribute("rend").unwrap_or("").to_lowercase();
                if rend.contains("italic") {
                    parts.push(format!("*{}*", content));
                } else if rend.contains("bold") {
                    parts.push(format!("**{}**", content));
                } else {
                    parts.push(content);
                }
            } else if tag == "ref" {
                let target = child.attribute("target").unwrap_or("");
                if target.starts_with("https://") || target.starts_with("http://") {
                    if !content.is_empty() {
                        parts.push(format!("[{}]({})", content, target));
                    } else {
                        parts.push(content);
                    }
                } else {
                    parts.push(content);
                }
            } else if tag == "lb" {
                parts.push("  \n".to_string());
            } else {
                parts.push(content);
            }
            if let Some(tail) = child.tail() {
                parts.push(tail.to_string());
            }
        } else if child.is_text() {
            parts.push(child.text().unwrap_or("").to_string());
        }
    }
    let joined = parts.join("");
    collapse_spaces(&joined).trim().to_string()
}

fn collapse_spaces(s: &str) -> String {
    let mut result = String::with_capacity(s.len());
    let mut prev_space = false;
    for ch in s.chars() {
        if ch.is_whitespace() && ch != '\n' {
            if !prev_space {
                result.push(' ');
                prev_space = true;
            }
        } else {
            result.push(ch);
            prev_space = ch == ' ';
        }
    }
    result
}

fn render_list(element: Node, depth: usize) -> String {
    let mut lines: Vec<String> = Vec::new();
    for item in element.children() {
        if item.is_element() && item.tag_name().name() == "item" {
            // look for p or direct content
            let mut content = String::new();
            let mut has_p = false;
            for p in item.children() {
                if p.is_element() && p.tag_name().name() == "p" {
                    content.push_str(&inline(p));
                    content.push(' ');
                    has_p = true;
                }
            }
            if !has_p {
                content = inline(item);
            }
            let content = content.trim().to_string();
            lines.push(format!("{}- {}", "  ".repeat(depth), content));
            for nested in item.children() {
                if nested.is_element() && nested.tag_name().name() == "list" {
                    lines.push(render_list(nested, depth + 1));
                }
            }
        }
    }
    lines.join("\n")
}

fn render_table(element: Node) -> String {
    let mut rows: Vec<Vec<String>> = Vec::new();
    for row in element.descendants() {
        if row.is_element() && row.tag_name().name() == "row" {
            let mut cells: Vec<String> = Vec::new();
            for cell in row.children() {
                if cell.is_element() && cell.tag_name().name() == "cell" {
                    cells.push(inline(cell).replace("|", "\\|"));
                }
            }
            if !cells.is_empty() {
                rows.push(cells);
            }
        }
    }
    if rows.is_empty() {
        return text_content(&element);
    }
    let width = rows.iter().map(|r| r.len()).max().unwrap_or(0);
    let rows_padded: Vec<Vec<String>> = rows
        .into_iter()
        .map(|mut r| {
            while r.len() < width {
                r.push(String::new());
            }
            r
        })
        .collect();
    let mut output: Vec<String> = Vec::new();
    if !rows_padded.is_empty() {
        output.push(format!("| {} |", rows_padded[0].join(" | ")));
        output.push(format!("| {} |", vec!["---"; width].join(" | ")));
        for row in rows_padded[1..].iter() {
            output.push(format!("| {} |", row.join(" | ")));
        }
    }
    output.join("\n")
}

fn render_node(element: Node, depth: usize) -> String {
    let tag = element.tag_name().name();
    if tag == "head" {
        let heading = inline(element);
        let level = if depth < 6 { depth } else { 6 };
        return format!("{} {}", "#".repeat(level), heading);
    }
    if tag == "p" {
        return inline(element);
    }
    if tag == "list" {
        return render_list(element, 0);
    }
    if tag == "table" {
        return render_table(element);
    }
    if tag == "formula" {
        return format!("$$\n{}\n$$", text_content(&element));
    }
    if tag == "figure" {
        let mut label_parts: Vec<String> = Vec::new();
        for l in element.children() {
            if l.is_element() && l.tag_name().name() == "label" {
                label_parts.push(text_content(&l));
            }
        }
        let mut caption_parts: Vec<String> = Vec::new();
        for c in element.children() {
            if c.is_element() && (c.tag_name().name() == "figDesc" || c.tag_name().name() == "head")
            {
                caption_parts.push(text_content(&c));
            }
        }
        let mut graphic_url = String::new();
        for g in element.descendants() {
            if g.is_element() && g.tag_name().name() == "graphic" {
                if let Some(url) = g.attribute("url") {
                    graphic_url = url.to_string();
                    break;
                }
            }
        }
        let description: String = [label_parts.join(" "), caption_parts.join(" ")]
            .into_iter()
            .filter(|x| !x.is_empty())
            .collect::<Vec<_>>()
            .join(" ");
        if !graphic_url.is_empty() {
            return format!("![{}]({})", description, graphic_url);
        }
        if !description.is_empty() {
            return format!("> {}", description);
        }
        return String::new();
    }
    if tag == "div" {
        return render_children(element, depth + 1);
    }
    String::new()
}

fn render_children(element: Node, depth: usize) -> String {
    let mut blocks: Vec<String> = Vec::new();
    for child in element.children() {
        if child.is_element() {
            let tag = child.tag_name().name();
            if matches!(
                tag,
                "head" | "p" | "div" | "list" | "table" | "formula" | "figure"
            ) {
                let result = render_node(child, depth);
                if !result.is_empty() {
                    blocks.push(result);
                }
            }
        }
    }
    blocks.join("\n\n")
}

pub fn convert_tei_to_md(
    input_path: &std::path::Path,
    meta: Option<&crate::metadata::Metadata>,
) -> anyhow::Result<String> {
    let content = std::fs::read_to_string(input_path)?;
    let doc = roxmltree::Document::parse(&content)?;
    let root = doc.root();

    // Find TEI element
    let tei = root
        .children()
        .find(|n| n.is_element() && n.tag_name().name() == "TEI")
        .unwrap_or(root);

    // Title
    let title = if let Some(title_node) = first_element(
        tei,
        "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title",
    ) {
        inline(title_node)
    } else {
        input_path
            .file_stem()
            .unwrap_or_default()
            .to_string_lossy()
            .to_string()
    };

    // Authors
    let mut authors: Vec<String> = Vec::new();
    let author_nodes = find_all(tei, "author");
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
        let name = collapse_spaces(&name).trim().to_string();
        if !name.is_empty() {
            authors.push(name);
        }
    }

    let abstract_node = first_element(tei, "//tei:profileDesc/tei:abstract");
    let body_node = first_element(tei, "//tei:text/tei:body");

    let mut sections: Vec<String> = Vec::new();
    let meta_resolved = match meta {
        Some(m) => m.clone(),
        None => extract_metadata_from_tei(input_path)?,
    };
    sections.push(frontmatter(&meta_resolved));
    sections.push(format!("# {}", title));
    if !authors.is_empty() {
        sections.push(format!("**Authors:** {}", authors.join(", ")));
    }
    if let Some(abs) = abstract_node {
        let abstract_md = render_children(abs, 2);
        if !abstract_md.is_empty() {
            sections.push("## Abstract".to_string());
            sections.push(abstract_md);
        }
    }
    if let Some(body) = body_node {
        let body_md = render_children(body, 2);
        if !body_md.is_empty() {
            sections.push("## Article".to_string());
            sections.push(body_md);
        }
    }

    // References
    let mut references: Vec<String> = Vec::new();
    for ref_node in find_all(tei, "listBibl") {
        // get biblStruct or bibl children
        for child in ref_node.children() {
            if child.is_element()
                && (child.tag_name().name() == "biblStruct" || child.tag_name().name() == "bibl")
            {
                let ref_text = text_content(&child);
                if !ref_text.is_empty() {
                    references.push(format!("- {}", ref_text));
                }
            }
        }
    }
    if !references.is_empty() {
        sections.push("## References".to_string());
        sections.push(references.join("\n"));
    }

    let result = sections.join("\n\n").trim().to_string();
    Ok(format!("{}\n", result))
}
