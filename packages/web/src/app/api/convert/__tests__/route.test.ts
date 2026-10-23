import { describe, it, expect, vi, beforeEach } from 'vitest';
import { POST } from '../route';

vi.mock('@/lib/grobid', () => ({
  callGrobid: vi.fn(),
}));

vi.mock('@/lib/tei-to-md', () => ({
  teiToMd: vi.fn(),
}));

import { callGrobid } from '@/lib/grobid';
import { teiToMd } from '@/lib/tei-to-md';

describe('POST /api/convert', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns 400 when no files uploaded', async () => {
    const formData = new FormData();
    const req = new Request('http://localhost/api/convert', {
      method: 'POST',
      body: formData,
    }) as any;
    req.formData = async () => formData;

    const res = await POST(req);
    const data = await res.json();
    expect(res.status).toBe(400);
    expect(data.error).toBe('No files uploaded');
  });

  it('converts files successfully', async () => {
    const formData = new FormData();
    const file = new File(['pdf'], 'test.pdf', { type: 'application/pdf' });
    formData.append('files', file);

    const req = new Request('http://localhost/api/convert', {
      method: 'POST',
      body: formData,
    }) as any;
    req.formData = async () => formData;

    (callGrobid as any).mockResolvedValue('<TEI></TEI>');
    (teiToMd as any).mockReturnValue('# Title\n\nContent');

    const res = await POST(req);
    const data = await res.json();
    expect(res.status).toBe(200);
    expect(data.results).toHaveLength(1);
    expect(data.results[0].name).toBe('test.md');
    expect(data.results[0].markdown).toBe('# Title\n\nContent');
  });

  it('handles conversion errors', async () => {
    const formData = new FormData();
    const file = new File(['pdf'], 'test.pdf', { type: 'application/pdf' });
    formData.append('files', file);

    const req = new Request('http://localhost/api/convert', {
      method: 'POST',
      body: formData,
    }) as any;
    req.formData = async () => formData;

    (callGrobid as any).mockRejectedValue(new Error('GROBID failed'));

    const res = await POST(req);
    const data = await res.json();
    expect(res.status).toBe(200);
    expect(data.results[0].error).toBe('GROBID failed');
    expect(data.results[0].markdown).toBe('');
  });
});
