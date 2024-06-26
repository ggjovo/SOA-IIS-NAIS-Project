import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from '../css/TourForm.css';
import { Card, CardContent, Typography, Button, Chip, Divider, Grid } from '@mui/material';
import {
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  Radio,
  FormControlLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  DialogActions
} from '@mui/material';
import { GoogleMap, LoadScript, Marker, InfoWindow, Polyline } from '@react-google-maps/api';
import { useNavigate } from 'react-router-dom';

function TourList() {
  const [tours, setTours] = useState([]);
  const navigate = useNavigate();
  const calculateTotalDistance = (markers) => {
    const sortedMarkers = [...markers].sort((a, b) => a.number - b.number);
    let totalDistance = 0;
    for (let i = 0; i < sortedMarkers.length - 1; i++) {
      totalDistance += calculateDistance(
        sortedMarkers[i].lat,
        sortedMarkers[i].lng,
        sortedMarkers[i + 1].lat,
        sortedMarkers[i + 1].lng
      );
    }
    return totalDistance.toFixed(2);
  };
  const handleOpenModal = (tour) => {
    setSelectedTour(tour);
    setShowModal(true);
  };
  
  const calculateRoute = () => {
  if (selectedTour && selectedTour.checkpoint_names && selectedTour.checkpoint_names.length > 1) {
    const sortedMarkers = selectedTour.checkpoint_names.slice().sort((a, b) => {
      const indexA = selectedTour.checkpoint_names.indexOf(a);
      const indexB = selectedTour.checkpoint_names.indexOf(b);
      return selectedTour.checkpoint_positions[indexA] - selectedTour.checkpoint_positions[indexB];
    });

    const path = sortedMarkers.map((name, index) => ({
      lat: selectedTour.checkpoint_latitude[index],
      lng: selectedTour.checkpoint_longitude[index],
    }));

    return (
      <Polyline
        path={path}
        options={{
          strokeColor: "#FF0000",
          strokeOpacity: 1,
          strokeWeight: 2,
          icons: [
            {
              icon: { path: window.google.maps.SymbolPath.FORWARD_CLOSED_ARROW },
              offset: "100%",
              repeat: "100px",
            },
          ],
        }}
      />
    );
  }
  return null;
};

  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Radius of the Earth in km
    const dLat = (lat2 - lat1) * (Math.PI / 180);
    const dLon = (lon2 - lon1) * (Math.PI / 180);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * (Math.PI / 180)) *
        Math.cos(lat2 * (Math.PI / 180)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c;
    return distance; // Distance in km
  };

  const containerStyle = {
    width: 'calc(100% / 3 * 2)',
    height: '560px',
  };

  const center = {
    lat: -34.397,
    lng: 150.644,
  };

  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newTag, setNewTag] = useState('');
  const [showTagPopup, setShowTagPopup] = useState(false);
  const [tourId, setTourId] = useState(0);
  const [selectedTour, setSelectedTour] = useState(null); // To store the selected tour data
  
  const [map, setMap] = useState(null);
  const [selectedMarker, setSelectedMarker] = useState(null);
  const [user, setUser] = useState({
    isLoggedIn: false,
    role: '',
    username: ''
  });
  const onLoad = (map) => {
    setMap(map);
  };

  const onMarkerClick = (marker) => {
    setSelectedMarker(marker);
  };


  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        // Make a request to check if user is logged in
        const response = await axios.get('http://localhost:8082/checklogin', {
          withCredentials: true 
        });

        if (response.data.loggedIn) {
          setUser({
            isLoggedIn: true,
            role: response.data.role,
            username: response.data.username,
          });
        }
      } catch (error) {
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    checkLoginStatus();

    const fetchTours = async () => {
      try {
        const response = await axios.get('http://localhost:8084/show_tours_guide', {
          withCredentials: true,
        });
        setTours(response.data.tours);
      } catch (error) {
        console.error('Error fetching tours:', error);
      }
    };
  
    fetchTours();
  }, []);

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', justifyContent: 'center' }}>
      <Grid container spacing={-20}>
      {tours.map((tour) => (
        <Grid item xs={12} sm={6} md={4} key={tour.id}>
          <Card variant="outlined" style={{ height: '200px', overflowY: 'auto', margin: '20px' }}>
            <Typography variant="h5" component="div" gutterBottom>
              {tour.title}
            </Typography>
            <Typography variant="body1" color="textSecondary">
              {tour.description}
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Duration: {tour.duration} min
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Status: {tour.status}
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
                Difficulty: {tour.difficulty}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Price: {tour.price}
              </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Tags:{' '}
              {tour.tags.map((tag) => (
                <Chip key={tag} label={tag} style={{ marginRight: '5px' }} />
              ))}
            </Typography>
            <Button onClick={() => handleOpenModal(tour)}>View Checkpoints</Button>
          </Card>
          <div style={{ height: '200px' }}>
            <LoadScript googleMapsApiKey="AIzaSyCufve6BuSX50Ep7dlucnuiiqKyqYgDSf4">
              <Dialog
                open={showModal}
                onClose={() => setShowModal(false)}
                fullWidth
                maxWidth="md"
              >
                <DialogTitle>Checkpoints</DialogTitle>
                <DialogContent>
                  <GoogleMap
                    mapContainerStyle={containerStyle}
                    center={center}
                    zoom={10}
                    onLoad={onLoad}
                  >
                    {/* Render markers for each checkpoint */}
                    {selectedTour && selectedTour.checkpoint_names && selectedTour.checkpoint_names.map((name, index) => (
                      <Marker
                        key={`${name}-${index}`}
                        position={{
                          lat: selectedTour.checkpoint_latitude[index],
                          lng: selectedTour.checkpoint_longitude[index],
                        }}
                        onClick={() => onMarkerClick(name)}
                      >
                         {selectedMarker === name && (
                          <InfoWindow onCloseClick={() => setSelectedMarker(null)}>
                            <div>
                              <h4>Name: {name}</h4>
                              <p>Position: {selectedTour.checkpoint_positions[index]}</p>
                            </div>
                          </InfoWindow>
                      )}
                      </Marker>
                    ))}
                  {calculateRoute()}
                </GoogleMap>
              </DialogContent>
            </Dialog>
          </LoadScript>
          </div>
        </Grid>
      ))}
      </Grid>
    </div>
  );
}  

export default TourList;
