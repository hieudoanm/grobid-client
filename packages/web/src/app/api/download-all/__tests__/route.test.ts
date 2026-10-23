import { describe, it, expect } from 'vitest';
import { POST } from '../route';

describe('POST /api/download-all', () => {
  it('returns 400 when invalid JSON', async () => {
    const req = new Request('http://localhost/api/download-all', {
      method: 'POST',
      body: 'invalid json',
    }) as any;

    const res = await POST(req);
    const data = await res.json();
    expect(res.status).toBe(400);
    expect(data.error).toBe('Invalid JSON body');
  });

  it('returns 400 when no files to package', async () => {
    const req = new Request('http://localhost/api/download-all', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ files: [] }),
    }) as any;

    const res = await POST(req);
    const data = await res.json();
    expect(res.status).toBe(400);
    expect(data.error).toBe('No files to package');
  });

  it('returns zip file with correct headers', async () => {
    const req = new Request('http://localhost/api/download-all', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        files: [
          { name: 'test.md', markdown: '# Hello' },
          { name: 'test2.md', markdown: '# World' },
        ],
      }),
    }) as any;

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(res.headers.get('Content-Type')).toBe('application/zip');
    expect(res.headers.get('Content-Disposition')).toBe(
      'attachment; filename="grobid-converted.zip"'
    );
  });
});
