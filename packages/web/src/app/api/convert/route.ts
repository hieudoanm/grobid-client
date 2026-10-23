import { NextRequest, NextResponse } from 'next/server';
import { callGrobid } from '@/lib/grobid';
import { teiToMd } from '@/lib/tei-to-md';

export const runtime = 'nodejs';

export const POST = async (req: NextRequest) => {
  const form = await req.formData();
  const files = form.getAll('files') as File[];
  if (!files.length) {
    return NextResponse.json({ error: 'No files uploaded' }, { status: 400 });
  }

  const results = [];
  for (const file of files) {
    try {
      const buf = Buffer.from(await file.arrayBuffer());
      const tei = await callGrobid(buf, file.name);
      const markdown = teiToMd(tei);
      results.push({
        name: file.name.replace(/\.pdf$/i, '') + '.md',
        markdown,
      });
    } catch (err) {
      results.push({
        name: file.name.replace(/\.pdf$/i, '') + '.md',
        markdown: '',
        error: err instanceof Error ? err.message : String(err),
      });
    }
  }

  return NextResponse.json({ results });
};
