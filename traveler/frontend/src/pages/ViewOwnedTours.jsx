import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, Typography, Button, Chip, Grid, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { GoogleMap, LoadScript, Marker, InfoWindow, Polyline } from '@react-google-maps/api';
import { useNavigate } from 'react-router-dom';

function ViewOwnedTours() {
  const [ownedTours, setOwnedTours] = useState([]);
  const [selectedTour, setSelectedTour] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedMarker, setSelectedMarker] = useState(null);
  const navigate = useNavigate();
  const [map, setMap] = useState(null);
  const [deleteConfirmationOpen, setDeleteConfirmationOpen] = useState(false);

  const onLoad = (map) => {
    setMap(map);
  };

  const onMarkerClick = (marker) => {
    setSelectedMarker(marker);
  };

  useEffect(() => {
    const fetchOwnedTours = async () => {
      try {
        const response = await axios.get('http://localhost:8084/owned_tours', { withCredentials: true });
        setOwnedTours(response.data.owned_tours);
        setDeleteConfirmationOpen(false);
      } catch (error) {
        console.error('Error fetching owned tours:', error);
      }
    };

    fetchOwnedTours();
  }, []);

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

  const handleOpenModal = (tour) => {
    setSelectedTour(tour);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedTour(null);
  };

  const handleStartTour = (tour) => {
    navigate('/start-tour', { state: { tour } });
  };

  const handleDelete = async (ownedtours_id) => {
    try {
      const response = await axios.delete(`http://localhost:8084/delete_owned_tour/${ownedtours_id}`, { withCredentials: true });
      setOwnedTours(ownedTours.filter(tour => tour.ownedtours_id !== ownedtours_id));
    } catch (error) {
      console.error('Error deleting tour:', error);
    }
  };

  const containerStyle = {
    width: '100%',
    height: '400px',
  };

  const center = {
    lat: -34.397,
    lng: 150.644,
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

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', justifyContent: 'center' }}>
      <Grid container spacing={2}>
        {ownedTours.map((tour) => (
          <Grid item xs={12} sm={6} md={4} key={tour.id}>
            <Card variant="outlined" style={{ height: '300px', overflowY: 'auto', margin: '20px' }}>
              <Typography variant="h5" component="div" gutterBottom>
                {tour.title}
              </Typography>
              <Typography variant="body1" color="textSecondary">
                {tour.description}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Duration: {tour.duration}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Difficulty: {tour.difficulty}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Price: {tour.price}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Quantity: {tour.quantity}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Tags:{' '}
                {tour.tags.map((tag) => (
                  <Chip key={tag} label={tag} style={{ marginRight: '5px' }} />
                ))}
              </Typography>
              <Button onClick={() => handleOpenModal(tour)}>View Checkpoints</Button>
              <Button onClick={() => handleStartTour(tour)}>Start Tour</Button>
              <Button onClick={() => setDeleteConfirmationOpen(true)}>Delete</Button>
              <Dialog open={deleteConfirmationOpen} onClose={() => setDeleteConfirmationOpen(false)}>
                <DialogTitle>Confirm Deletion</DialogTitle>
                <DialogContent>
                  <Typography>Are you sure you want to delete {tour.title}?</Typography>
                </DialogContent>
                <DialogActions>
                  <Button onClick={() => setDeleteConfirmationOpen(false)}>Cancel</Button>
                  <Button onClick={() => handleDelete(tour.ownedtours_id)}>Confirm</Button>
                </DialogActions>
              </Dialog>
            </Card>
            <div style={{ height: '200px' }}>
              <LoadScript googleMapsApiKey="AIzaSyCufve6BuSX50Ep7dlucnuiiqKyqYgDSf4">
                <Dialog open={showModal} onClose={handleCloseModal} fullWidth maxWidth="md">
                  <DialogTitle>Checkpoints</DialogTitle>
                  <DialogContent>
                    <GoogleMap
                      mapContainerStyle={containerStyle}
                      center={center}
                      zoom={10}
                      onLoad={onLoad}
                    >
                      {selectedTour && selectedTour.checkpoint_names && selectedTour.checkpoint_names.map((name, index) => (
                        <Marker
                          key={`${name}-${index}`}
                          position={{ lat: selectedTour.checkpoint_latitude[index], lng: selectedTour.checkpoint_longitude[index] }}
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

export default ViewOwnedTours;
