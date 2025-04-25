import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function ErrorPage() {
  const navigate = useNavigate();
  const [secondsLeft, setSecondsLeft] = useState(10);

  useEffect(() => {
    // Decrease the counter every second
    const interval = setInterval(() => {
      setSecondsLeft((prev) => prev - 1);
    }, 1000);

    // Redirect when the timer reaches 0
    const timeout = setTimeout(() => {
      navigate('/');
    }, 10000);

    // Cleanup both timers on unmount
    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [navigate]);

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h2>Oops! Page not found (404)</h2>
      <p>The page you are looking for doesn't exist.</p>
      <p>Redirecting to the homepage in {secondsLeft} seconds...</p>
      <p>
        Or you can <a href="/">click here</a> to go back immediately.
      </p>
    </div>
  );
}

export default ErrorPage;

