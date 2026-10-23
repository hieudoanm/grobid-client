import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Home from '../page';

global.fetch = vi.fn();

describe('Home page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders title and upload section', () => {
    render(<Home />);
    expect(screen.getByText('Grobid Web')).toBeInTheDocument();
    expect(screen.getByText('Select PDF files')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Convert to Markdown/i })
    ).toBeInTheDocument();
  });

  it('disables convert button when no files selected', () => {
    render(<Home />);
    const button = screen.getByRole('button', { name: /Convert to Markdown/i });
    expect(button).toBeDisabled();
  });

  it('handles file selection', () => {
    render(<Home />);
    const input = screen.getByLabelText('Select PDF files') as HTMLInputElement;
    const file = new File(['pdf content'], 'test.pdf', {
      type: 'application/pdf',
    });
    fireEvent.change(input, { target: { files: [file] } });
    expect(screen.getByText(/test\.pdf/)).toBeInTheDocument();
  });
});
