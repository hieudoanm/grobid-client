import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

export const POST = async (req: NextRequest) => {
  let body: { files: { name: string; markdown: string }[] };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  const files = body.files ?? [];
  if (!files.length) {
    return NextResponse.json({ error: 'No files to package' }, { status: 400 });
  }

  const { ZipArchive } = await import('archiver');
  const archive = new ZipArchive({ zlib: { level: 9 } });
  const chunks: Buffer[] = [];

  for (const file of files) {
    archive.append(file.markdown ?? '', { name: file.name });
  }
  archive.finalize();

  for await (const chunk of archive as any) {
    chunks.push(Buffer.from(chunk));
  }

  const buffer = Buffer.concat(chunks);
  return new NextResponse(buffer, {
    status: 200,
    headers: {
      'Content-Type': 'application/zip',
      'Content-Disposition': 'attachment; filename="grobid-converted.zip"',
      'Content-Length': String(buffer.length),
    },
  });
};
