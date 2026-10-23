import Link from 'next/link';

const NotFound = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h2>Not Found</h2>
    <p>Could not find the requested resource</p>
    <Link href="/">Return Home</Link>
  </div>
);

export default NotFound;
