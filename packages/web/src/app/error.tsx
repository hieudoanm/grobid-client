'use client';

const Error = ({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h2>Something went wrong!</h2>
    <p>{error.message}</p>
    <button onClick={() => reset()}>Try again</button>
  </div>
);

export default Error;
