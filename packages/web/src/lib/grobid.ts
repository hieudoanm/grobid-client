const GROBID_URL = process.env.GROBID_URL || 'http://localhost:8070';

export const callGrobid = async (
  buf: Buffer,
  filename: string
): Promise<string> => {
  const form = new FormData();
  form.append(
    'input',
    new Blob([buf as unknown as BlobPart], { type: 'application/pdf' }),
    filename
  );
  form.append('consolidateHeader', '1');

  const res = await fetch(`${GROBID_URL}/api/processFulltextDocument`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) throw new Error(`GROBID returned ${res.status}`);
  return res.text();
};
