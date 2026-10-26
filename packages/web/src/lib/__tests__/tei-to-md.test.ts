import { describe, it, expect } from 'vitest';
import { teiToMd } from '../tei-to-md';

const wrap = (inner: string): string =>
  `<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">${inner}</TEI>`;

describe('teiToMd', () => {
  it('converts a minimal TEI document with title and abstract', () => {
    const xml = wrap(
      `<teiHeader>
        <title>The Paper Title</title>
        <abstract><p>This is the abstract text.</p></abstract>
      </teiHeader>
      <body>
        <div><head>Introduction</head><p>Body paragraph one.</p></div>
      </body>`
    );

    const md = teiToMd(xml);
    expect(md).toContain('# The Paper Title');
    expect(md).toContain('## Abstract');
    expect(md).toContain('This is the abstract text.');
    expect(md).toContain('## Introduction');
    expect(md).toContain('Body paragraph one.');
  });

  it('renders top-level headings and paragraphs', () => {
    const xml = wrap(
      `<body>
        <div>
          <head>Methods</head>
          <p>First method paragraph.</p>
          <p>Second method paragraph.</p>
        </div>
      </body>`
    );

    const md = teiToMd(xml);
    expect(md).toContain('## Methods');
    expect(md).toContain('First method paragraph.');
    expect(md).toContain('Second method paragraph.');
  });

  it('renders lists', () => {
    const xml = wrap(
      `<body>
        <list>
          <item>Item one</item>
          <item>Item two</item>
        </list>
      </body>`
    );

    const md = teiToMd(xml);
    expect(md).toContain('- Item one');
    expect(md).toContain('- Item two');
  });

  it('renders tables', () => {
    const xml = wrap(
      `<body>
        <table>
          <row>
            <cell>Header A</cell>
            <cell>Header B</cell>
          </row>
          <row>
            <cell>Value 1</cell>
            <cell>Value 2</cell>
          </row>
        </table>
      </body>`
    );

    const md = teiToMd(xml);
    expect(md).toContain('| Header A | Header B |');
    expect(md).toContain('| --- | --- |');
    expect(md).toContain('| Value 1 | Value 2 |');
  });

  it('renders figures with captions', () => {
    const xml = wrap(
      `<body>
        <figure>
          <figDesc>A chart showing results.</figDesc>
        </figure>
      </body>`
    );

    const md = teiToMd(xml);
    expect(md).toContain('*A chart showing results.*');
  });

  it('renders references', () => {
    const xml = wrap(
      `<body>
        <listBibl>
          <bibl>Author, A. (2024). Title. Journal.</bibl>
        </listBibl>
      </body>`
    );

    const md = teiToMd(xml);
    expect(md).toContain('- Author, A. (2024). Title. Journal.');
  });

  it('handles TEI without a TEI wrapper element', () => {
    const xml = `<body><p>Standalone paragraph.</p></body>`;
    const md = teiToMd(xml);
    expect(md).toContain('Standalone paragraph.');
  });

  it('returns empty string for empty TEI', () => {
    const xml = wrap('');
    expect(teiToMd(xml)).toBe('');
  });
});
