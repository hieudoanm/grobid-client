import { XMLParser } from 'fast-xml-parser';

const asArray = (v: any): any[] => {
  if (v == null) return [];
  return Array.isArray(v) ? v : [v];
};

const childTags = (obj: any): { tag: string; node: any }[] => {
  const out: { tag: string; node: any }[] = [];
  if (!obj || typeof obj !== 'object') return out;
  for (const [k, v] of Object.entries(obj)) {
    if (k === '#text' || k.startsWith('@_')) continue;
    for (const node of asArray(v)) out.push({ tag: k, node });
  }
  return out;
};

const findTag = (
  kids: { tag: string; node: any }[],
  tag: string
): { tag: string; node: any } | undefined => kids.find((k) => k.tag === tag);

const inlineText = (node: any): string => {
  const parts: string[] = [];
  if (typeof node === 'string') return node;
  if (!node || typeof node !== 'object') return '';
  const t = node['#text'];
  if (typeof t === 'string') parts.push(t);
  const inlineTags = new Set([
    'ref',
    'ptr',
    'emph',
    'title',
    'foreign',
    'name',
    'keyword',
  ]);
  for (const { tag, node: child } of childTags(node)) {
    if (inlineTags.has(tag)) parts.push(inlineText(child));
  }
  return parts.join('');
};

const renderChildren = (node: any): string =>
  childTags(node)
    .map(({ tag, node: n }) => renderNode(tag, n))
    .join('\n');

const renderTable = (node: any): string => {
  const rows = childTags(node).filter(({ tag }) => tag === 'row');
  if (rows.length === 0) return '';
  const md: string[] = [];
  const cells = (tag: string, n: any) =>
    childTags(n)
      .filter(({ tag: t }) => t === tag)
      .map(({ node: c }) => inlineText(c));
  const header = cells('cell', rows[0].node);
  md.push('| ' + header.join(' | ') + ' |');
  md.push('| ' + header.map(() => '---').join(' | ') + ' |');
  for (const { node: row } of rows.slice(1))
    md.push('| ' + cells('cell', row).join(' | ') + ' |');
  return md.join('\n') + '\n';
};

const renderNode = (tag: string, node: any): string => {
  const kids = childTags(node);
  switch (tag) {
    case 'TEI':
      return kids.map(({ tag: t, node: n }) => renderNode(t, n)).join('\n\n');
    case 'teiHeader': {
      let md = '';
      const title = findTag(kids, 'title');
      if (title) md += '# ' + inlineText(title.node) + '\n\n';
      const abstract = findTag(kids, 'abstract');
      if (abstract)
        md += '## Abstract\n\n' + renderChildren(abstract.node) + '\n\n';
      return md;
    }
    case 'title':
      return inlineText(node);
    case 'abstract':
    case 'body':
    case 'div':
      return renderChildren(node);
    case 'head':
      return '## ' + inlineText(node) + '\n';
    case 'p':
      return inlineText(node) + '\n';
    case 'list':
      return (
        kids
          .map(({ tag: t, node: n }) =>
            t === 'item' ? '- ' + inlineText(n) : renderNode(t, n)
          )
          .join('\n') + '\n'
      );
    case 'item':
      return inlineText(node);
    case 'table':
      return renderTable(node);
    case 'figure':
      return renderChildren(node);
    case 'figDesc':
      return '*' + inlineText(node) + '*\n';
    case 'ref':
    case 'ptr':
      return inlineText(node);
    case 'bibl':
      return '- ' + inlineText(node) + '\n';
    default:
      return renderChildren(node);
  }
};

export const teiToMd = (xml: string): string => {
  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: '@_',
    textNodeName: '#text',
    parseTagValue: false,
    parseAttributeValue: false,
    trimValues: true,
    ignoreDeclaration: true,
  });
  const obj = parser.parse(xml) as any;
  const tei = obj.TEI || obj;
  return renderNode('TEI', tei).trim();
};
