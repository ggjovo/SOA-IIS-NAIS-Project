import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from 'react-router-dom';
import '../css//LoginForm.css'; // Import custom CSS file for styling

function LoginForm() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  
  useEffect(() => {
    const checkLogin = async () => {
      try {
        const { data } = await axios.get('http://localhost:8082/checklogin', {
          withCredentials: true,
        });
        if (data.loggedIn) {
          navigate('/');
        }
      } catch (error) {
        if (error.response) {
          const { data, status } = error.response;
          console.error('Server responded with an error:', data);
          console.error('Status code:', status);
        } else if (error.request) {
          console.error('No response received:', error.request);
        } else {
          console.error('Error setting up the request:', error.message);
        }
      }
    };

    checkLogin();
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const { data } = await axios.post(
        "http://localhost:8082/login",
        {
          username,
          password,
        },
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true
        }
      );

      navigate('/');
    } catch (error) {
      setSuccessMessage("Wrong username or password!");
    }
  };

  return (
    <div className="login-container">
      <h2 className="login-heading">Login</h2>
      <form className="login-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username:</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {successMessage && <p className="error-message">{successMessage}</p>}
        <button type="submit" className="login-button">Login</button>
      </form>
    </div>
  );
}

export default LoginForm;
