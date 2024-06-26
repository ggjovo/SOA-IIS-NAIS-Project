import React, { useEffect, useState, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { GoogleMap, LoadScript, Marker, Polyline } from '@react-google-maps/api';
import axios from 'axios';
import { Button, Typography, Box, List, ListItem, ListItemText } from '@mui/material';

const StartTour = () => {
  const location = useLocation();
  const { tour } = location.state || {};
  const [userLocation, setUserLocation] = useState(null);
  const [currentCheckpoint, setCurrentCheckpoint] = useState(null);
  let tourExecutionId = 1;

  useEffect(() => {
    if (tour && tour.checkpoint_latitude && tour.checkpoint_latitude.length > 0) {
      axios.post(`http://localhost:8084/start_tour/${tour.id}`, {}, { withCredentials: true })
        .then(response => {
          const executionId = response.data.tour_execution_id;
          const newLocation = { lat: tour.checkpoint_latitude[0], lng: tour.checkpoint_longitude[0] };
          setUserLocation(newLocation);
          tourExecutionId = executionId;
          updatePosition(executionId, newLocation.lat, newLocation.lng);
        })
        .catch(error => {
          console.error('Error starting tour:', error);
        });
    }
  }, [tour]);

  const handleMapClick = useCallback((event) => {
    const newPosition = { lat: event.latLng.lat(), lng: event.latLng.lng() };
    setUserLocation(newPosition);
    if (tourExecutionId) {
      updatePosition(tourExecutionId, newPosition.lat, newPosition.lng);
    } else {
      console.error('Tour execution ID is null. Cannot update position.');
    }
  }, [tourExecutionId]);

  const updatePosition = (executionId, lat, lng) => {
    if (!executionId) {
      console.error('Tour execution ID is null. Cannot update position.');
      return;
    }

    axios.put(`http://localhost:8084/update_position/${executionId}`, {
      tour_id: tour.id,
      latitude: lat,
      longitude: lng
    }, { withCredentials: true })
      .then(response => {
        console.log('Location updated:', response.data);
    })
      .catch(error => {
        console.error('Error updating location:', error);
      });
  };

  const calculateRoute = () => {
    if (window.google && window.google.maps && tour && tour.checkpoint_names && tour.checkpoint_names.length > 1) {
      const sortedMarkers = tour.checkpoint_names.slice().sort((a, b) => {
        const indexA = tour.checkpoint_names.indexOf(a);
        const indexB = tour.checkpoint_names.indexOf(b);
        return tour.checkpoint_positions[indexA] - tour.checkpoint_positions[indexB];
      });

      const path = sortedMarkers.map((name, index) => ({
        lat: tour.checkpoint_latitude[index],
        lng: tour.checkpoint_longitude[index],
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

  if (!tour || !tour.checkpoint_latitude) {
    return <div>Loading...</div>;
  }

  const containerStyle = {
    width: '600px',
    height: '400px',
  };

  const center = {
    lat: tour.checkpoint_latitude[0] || 0,
    lng: tour.checkpoint_longitude[0] || 0,
  };

  return (
    <Box display="flex" flexDirection="row">
      <Box flex={1}>
        <LoadScript googleMapsApiKey="AIzaSyCufve6BuSX50Ep7dlucnuiiqKyqYgDSf4">
          <GoogleMap
            onLoad={(map) => {
              map.addListener('click', handleMapClick);
            }}
            mapContainerStyle={containerStyle}
            center={userLocation || center}
            zoom={10}
          >
            {userLocation && <Marker position={userLocation} />}
            {tour.checkpoint_latitude.map((lat, index) => (
              <Marker
                key={index}
                position={{ lat, lng: tour.checkpoint_longitude[index] }}
              />
            ))}
            {calculateRoute()}
          </GoogleMap>
        </LoadScript>
      </Box>
      <Box flex={1} padding="16px">
        <Typography variant="h6">Description</Typography>
        <Box padding="16px" border="1px solid #ccc" borderRadius="8px" minHeight="300px">
          {tour.description}
        </Box>
      </Box>
      <Box flex={1} padding="16px">
        <Typography variant="h6">Current Checkpoint</Typography>
        <Box padding="16px" border="1px solid #ccc" borderRadius="8px" minHeight="50px">
          {currentCheckpoint ? currentCheckpoint.name : 'No checkpoint reached yet'}
        </Box>
        <Typography variant="h6" marginTop="16px">Checkpoints</Typography>
        <List>
          {tour.checkpoint_names.map((name, index) => (
            <ListItem key={index} style={{ color: currentCheckpoint && currentCheckpoint.name === name ? 'red' : 'black' }}>
              <ListItemText primary={`Checkpoint #${index + 1} - ${name}`} />
            </ListItem>
          ))}
        </List>
        <Button variant="contained" color="primary" fullWidth>Finish Tour</Button>
      </Box>
    </Box>
  );
};

export default StartTour;
