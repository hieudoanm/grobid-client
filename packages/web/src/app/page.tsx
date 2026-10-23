'use client';

import { useCallback, useState } from 'react';

type Result = { name: string; markdown: string; error?: string };

const Home = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [results, setResults] = useState<Result[]>([]);
  const [converting, setConverting] = useState(false);
  const [error, setError] = useState('');

  const onFiles = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(Array.from((e.target as HTMLInputElement).files ?? []));
    setError('');
    setResults([]);
  }, []);

  const removeFile = useCallback(
    (name: string) => setFiles((f) => f.filter((x) => x.name !== name)),
    []
  );

  const convert = useCallback(async () => {
    if (!files.length) return;
    setConverting(true);
    setError('');
    const form = new FormData();
    for (const f of files) form.append('files', f);
    try {
      const res = await fetch('/api/convert', { method: 'POST', body: form });
      if (!res.ok) throw new Error(`Conversion failed (${res.status})`);
      const data = await res.json();
      setResults(
        (data.results ?? []).map((r: any) => ({
          name: r.name,
          markdown: r.markdown ?? '',
          error: r.error,
        }))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setConverting(false);
    }
  }, [files]);

  const download = (name: string, content: string) => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadAll = async () => {
    if (!results.length) return;
    try {
      const res = await fetch('/api/download-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ files: results }),
      });
      if (!res.ok) throw new Error(`Download failed (${res.status})`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'grobid-converted.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <div
      style={{
        fontFamily: 'system-ui, -apple-system, Segoe UI, sans-serif',
        maxWidth: 960,
        margin: '0 auto',
        padding: 32,
      }}>
      <h1>Grobid Web</h1>
      <p>
        Upload one or more research PDFs. They are converted to Markdown via
        your self-hosted GROBID server (docker-compose, port 8070).
      </p>

      <div
        style={{
          border: '1px solid #ccc',
          padding: 18,
          marginTop: 18,
          borderRadius: 8,
          background: '#fafafa',
        }}>
        <label
          htmlFor="file-input"
          style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>
          Select PDF files
        </label>
        <input
          id="file-input"
          type="file"
          multiple
          accept=".pdf"
          onChange={onFiles}
          style={{ marginBottom: 10 }}
        />
        {files.length > 0 && (
          <div style={{ marginBottom: 10 }}>
            {files.map((f) => (
              <div
                key={f.name}
                style={{
                  display: 'flex',
                  gap: 8,
                  alignItems: 'center',
                  marginBottom: 4,
                  fontSize: 14,
                }}>
                <span style={{ color: '#666' }}>&#128194; {f.name}</span>
                <button
                  type="button"
                  onClick={() => removeFile(f.name)}
                  style={{
                    marginLeft: 'auto',
                    color: '#c00',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: 0,
                    fontSize: 14,
                  }}>
                  remove
                </button>
              </div>
            ))}
          </div>
        )}
        <button
          type="button"
          disabled={!files.length || converting}
          onClick={convert}
          style={{ padding: '8px 14px', cursor: 'pointer' }}>
          {converting ? 'Converting\u2026' : 'Convert to Markdown'}
        </button>
        {error && <div style={{ color: '#c00', marginTop: 8 }}>{error}</div>}
      </div>

      {results.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <div
            style={{
              display: 'flex',
              gap: 8,
              alignItems: 'center',
              marginBottom: 10,
            }}>
            <h2 style={{ margin: 0, fontSize: 18 }}>
              Converted ({results.length})
            </h2>
            <button
              type="button"
              onClick={downloadAll}
              style={{
                marginLeft: 'auto',
                padding: '6px 12px',
                cursor: 'pointer',
              }}>
              Download all (.zip)
            </button>
          </div>
          {results.map((r) => (
            <div
              key={r.name}
              style={{
                border: '1px solid #ddd',
                padding: 12,
                marginBottom: 10,
                borderRadius: 6,
              }}>
              <div style={{ fontWeight: 600, marginBottom: 6, fontSize: 15 }}>
                {r.name}
              </div>
              {r.error ? (
                <div style={{ color: '#c00', fontSize: 13, marginBottom: 6 }}>
                  {r.error}
                </div>
              ) : (
                <>
                  <textarea
                    value={r.markdown}
                    readOnly
                    style={{
                      width: '100%',
                      height: 240,
                      fontFamily: 'ui-monospace, SFMono-Regular, monospace',
                      fontSize: 12,
                      marginBottom: 8,
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => download(r.name, r.markdown)}
                    style={{
                      padding: '6px 12px',
                      cursor: 'pointer',
                      marginRight: 6,
                    }}>
                    Download .md
                  </button>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Home;
