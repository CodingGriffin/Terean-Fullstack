// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function ForbiddenPage() {
  const navigate = useNavigate();
  const [secondsLeft, setSecondsLeft] = useState(10);

  useEffect(() => {
    const interval = setInterval(() => {
      setSecondsLeft((prev) => prev - 1);
    }, 1000);

    const timeout = setTimeout(() => {
      navigate('/');
    }, 10000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [navigate]);

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h2>Access Denied (403)</h2>
      <p>You don't have permission to access this page.</p>
      <p>Redirecting to the homepage in {secondsLeft} seconds...</p>
      <p>
        Or you can <a href="/">click here</a> to return immediately.
      </p>
    </div>
  );
}

export default ForbiddenPage;
