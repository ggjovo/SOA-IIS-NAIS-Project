import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Box, CircularProgress, Grid, Paper, Typography, Button } from '@mui/material'; // Import Button from @mui/material
import ExploreIcon from '@mui/icons-material/Explore';
import AdventureIcon from '@mui/icons-material/Explore';
import SightseeingIcon from '@mui/icons-material/LocationOn';
import { Link } from 'react-router-dom';

function HomePage() {
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null); // Initialize user as null

  useEffect(() => {
    const fetchData = async () => {
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
        console.error('Error fetching user data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <Grid container justifyContent="center" spacing={4}>
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Grid item xs={12}>
            <Typography variant="h3" align="center" gutterBottom>Welcome to the Tourist Platform!</Typography>
            <Typography variant="body1" align="center" gutterBottom>
              Explore and discover amazing tours offered by local guides. Whether you're looking for an adventurous
              trekking experience, a cultural immersion, or a leisurely sightseeing tour, we have something for everyone!
            </Typography>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <Paper elevation={3} sx={{ padding: '20px', textAlign: 'center', backgroundColor: '#F0F4F8' }}>
              <Typography variant="h5" gutterBottom>Explore</Typography>
              <ExploreIcon style={{ fontSize: 60, color: '#3F51B5' }} />
              <Typography variant="body1" gutterBottom>
                Discover new destinations and uncover hidden gems with our diverse range of tours.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <Paper elevation={3} sx={{ padding: '20px', textAlign: 'center', backgroundColor: '#F0F4F8' }}>
              <Typography variant="h5" gutterBottom>Adventure</Typography>
              <AdventureIcon style={{ fontSize: 60, color: '#FF5722' }} />
              <Typography variant="body1" gutterBottom>
                Embark on thrilling adventures and adrenaline-pumping activities with experienced guides.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <Paper elevation={3} sx={{ padding: '20px', textAlign: 'center', backgroundColor: '#F0F4F8' }}>
              <Typography variant="h5" gutterBottom>Sightseeing</Typography>
              <SightseeingIcon style={{ fontSize: 60, color: '#009688' }} />
              <Typography variant="body1" gutterBottom>
                Immerse yourself in the beauty of iconic landmarks and scenic wonders on our sightseeing tours.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12}>
            <Box mt={4} textAlign="center">
              {user && user.isLoggedIn ? (
                <Box>
                  <Typography variant="h4" gutterBottom>Hello, {user.username}!</Typography>
                  <Typography variant="body1" gutterBottom>
                    You are logged in as a {user.role}.
                  </Typography>
                  {user.role === 'guide' && (
                    <Button component={Link} to="/create-tour" variant="contained" color="primary" sx={{ marginRight: '10px' }}>Create a New Tour</Button>
                  )}
                  {user.role === 'tourist' && (
                    <Button component={Link} to="/view-owned-tours" variant="contained" color="primary">View Owned Tours</Button>
                  )}
                </Box>
              ) : (
                <Box>
                  <Typography variant="body1" gutterBottom>
                    Sign in or register to explore and book amazing tours!
                  </Typography>
                  <Button component={Link} to="/login" variant="contained" color="primary" sx={{ marginRight: '10px' }}>Sign In</Button>
                  <Button component={Link} to="/register" variant="outlined" color="primary">Register</Button>
                </Box>
              )}
            </Box>
          </Grid>
        </>
      )}
    </Grid>
  );
}

export default HomePage;
