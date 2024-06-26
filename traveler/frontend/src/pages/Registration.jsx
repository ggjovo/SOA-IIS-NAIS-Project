import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from 'react-router-dom';
import '../css/LoginForm.css'; // Import custom CSS file for styling

function RegistrationForm() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== repeatPassword) {
      setErrorMessage("Passwords do not match!");
      return;
    }

    if (!["tourist", "guide", "admin"].includes(role)) {
      setErrorMessage("Invalid role selected!");
      return;
    }

    try {
      const { data } = await axios.post(
        "http://localhost:8082/register",
        {
          username,
          password,
          email,
          role,
        },
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true
        }
      );

      navigate('/login');
    } catch (error) {
      setErrorMessage("Registration failed. Please try again.");
    }
  };

  return (
    <div className="login-container">
      <h2 className="login-heading">Register</h2>
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
        <div className="form-group">
          <label htmlFor="repeatPassword">Repeat Password:</label>
          <input
            id="repeatPassword"
            type="password"
            value={repeatPassword}
            onChange={(e) => setRepeatPassword(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="role">Role:</label>
          <select
            id="role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            required
          >
            <option value="">Select Role</option>
            <option value="tourist">Tourist</option>
            <option value="guide">Guide</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        {errorMessage && <p className="error-message">{errorMessage}</p>}
        <button type="submit" className="login-button">Register</button>
      </form>
    </div>
  );
}

export default RegistrationForm;
