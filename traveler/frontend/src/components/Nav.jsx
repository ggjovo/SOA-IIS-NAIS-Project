import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';

function HomePage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState({
    isLoggedIn: false,
    role: '',
    username: '',
  });

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const { data } = await axios.get('http://localhost:8082/checklogin', {
          withCredentials: true,
        });

        if (data.loggedIn) {
          setUser({
            isLoggedIn: true,
            role: data.role,
            username: data.username,
          });
        } else {
          setUser({
            isLoggedIn: false,
            role: '',
            username: '',
          });
        }
      } catch (error) {
        console.error('Error checking login status:', error);
      } finally {
        setLoading(false);
      }
    };

    checkLoginStatus();
  }, []);

  const handleLogout = async () => {
    try {
      const { status } = await axios.get('http://localhost:8082/logout', {
        withCredentials: true,
      });
      if (status === 200) {
        console.log('Logging out');
        setUser({
          isLoggedIn: false,
          role: '',
          username: '',
        });
        navigate('/login');
      }
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <div>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component={Link} to="/" style={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
            Tourist Platform
          </Typography>
          <Box>
            {!loading && (
              <React.Fragment>
                {/* Show Blog for all users */}
                <Typography variant="body1" component={Link} to="/all-blogs" style={{ textDecoration: 'none', color: 'inherit', marginRight: '20px' }}>
                  Blog
                </Typography>
                {/* Show My Blog for Tourists */}
                {user.isLoggedIn && user.role === 'tourist' && (
                  <Typography variant="body1" component={Link} to="/my-blog" style={{ textDecoration: 'none', color: 'inherit', marginRight: '20px' }}>
                    My Blog
                  </Typography>
                )}
                {/* Show Rate Platform for Tourists and Guides */}
                {(user.isLoggedIn && (user.role === 'tourist' || user.role === 'guide')) && (
                  <Typography variant="body1" component={Link} to="/rate-platform" style={{ textDecoration: 'none', color: 'inherit', marginRight: '20px' }}>
                    Rate Platform
                  </Typography>
                )}
                {/* Show Admin Page for Admins */}
                {user.isLoggedIn && user.role === 'admin' && (
                  <Typography variant="body1" component={Link} to="/admin-page" style={{ textDecoration: 'none', color: 'inherit', marginRight: '20px' }}>
                    Admin Page
                  </Typography>
                )}
                {/* Show Logout button if user is logged in */}
                {user.isLoggedIn && (
                  <Button variant="contained" onClick={handleLogout} color="secondary">
                    Log Out
                  </Button>
                )}
                {/* Show Login and Register buttons if user is not logged in */}
                {!user.isLoggedIn && (
                  <React.Fragment>
                    <Button variant="contained" component={Link} to="/login" color="primary" style={{ marginRight: '10px' }}>
                      Log In
                    </Button>
                    <Button variant="contained" component={Link} to="/register" color="primary">
                      Register
                    </Button>
                  </React.Fragment>
                )}
              </React.Fragment>
            )}
          </Box>
        </Toolbar>
      </AppBar>
      {loading && <Typography>Loading...</Typography>}
    </div>
  );
}

export default HomePage;
