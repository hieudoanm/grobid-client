export const metadata = {
  title: 'Grobid Web',
  description:
    'Convert research PDFs to Markdown via your self-hosted GROBID server',
};

const RootLayout = ({ children }: { children: React.ReactNode }) => (
  <html lang="en">
    <body>{children}</body>
  </html>
);

export default RootLayout;
