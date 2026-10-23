import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { callGrobid } from '../grobid';

describe('callGrobid', () => {
  const originalFetch = globalThis.fetch;
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    globalThis.fetch = originalFetch;
  });

  it('POSTs the PDF to GROBID and returns the TEI text', async () => {
    fetchMock.mockResolvedValue(
      new Response('<TEI>tei content</TEI>', { status: 200 })
    );

    const buf = Buffer.from('%PDF-1.4 fake pdf');
    const result = await callGrobid(buf, 'research-paper.pdf');

    expect(result).toBe('<TEI>tei content</TEI>');
    expect(fetchMock).toHaveBeenCalledTimes(1);

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('http://localhost:8070/api/processFulltextDocument');
    expect(init?.method).toBe('POST');

    const form = init?.body as FormData;
    expect(form.get('consolidateHeader')).toBe('1');

    const input = form.get('input') as File;
    expect(input).toBeInstanceOf(File);
    expect(input.name).toBe('research-paper.pdf');
    expect(input.type).toBe('application/pdf');
  });

  it('throws when GROBID returns a non-ok status', async () => {
    fetchMock.mockResolvedValue(new Response('server error', { status: 500 }));

    await expect(callGrobid(Buffer.from('%PDF'), 'a.pdf')).rejects.toThrow(
      'GROBID returned 500'
    );
  });

  it('throws when fetch rejects', async () => {
    fetchMock.mockRejectedValue(new Error('network down'));

    await expect(callGrobid(Buffer.from('%PDF'), 'a.pdf')).rejects.toThrow(
      'network down'
    );
  });
});
