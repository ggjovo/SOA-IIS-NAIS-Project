import React, { useState, useEffect } from 'react';
import { GoogleMap, Marker, InfoWindow, Polyline, DirectionsService, DirectionsRenderer, useJsApiLoader } from '@react-google-maps/api';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import {
  Button,
  TextField,
  Typography,
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
  DialogActions,
  Paper,
  Chip
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

const containerStyle = {
  width: '800px',
  height: '400px',
};

const center = {
  lat: -34.397,
  lng: 150.644,
};

const AddTour = () => {
  const navigate = useNavigate();
  const [tourData, setTourData] = useState({
    title: '',
    description: '',
    duration: '',
    durationUnit: 'minutes',
    difficulty: 'easy',
    tags: [],
    price: '',
    currency: 'din',
  });
  const [user, setUser] = useState({
    isLoggedIn: false,
    role: '',
    username: ''
  });
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newTag, setNewTag] = useState('');
  const [showTagPopup, setShowTagPopup] = useState(false);
  const [tourId, setTourId] = useState(0);

  const [map, setMap] = useState(null);
  const [markers, setMarkers] = useState([]);
  const [name, setName] = useState('');
  const [number, setNumber] = useState('');
  const [selectedMarker, setSelectedMarker] = useState(null);
  const [directionsResponse, setDirectionsResponse] = useState(null);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: "AIzaSyCufve6BuSX50Ep7dlucnuiiqKyqYgDSf4", // Replace with your API key
    libraries: ['places'],
  });

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
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
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setTourData({
      ...tourData,
      [name]: value,
    });
  };

  const handleDurationUnitChange = (e) => {
    setTourData({
      ...tourData,
      durationUnit: e.target.value,
    });
  };

  const handleAddTag = () => {
    setShowTagPopup(true);
  };

  const confirmAddTag = () => {
    if (newTag) {
      setTourData({
        ...tourData,
        tags: [...tourData.tags, newTag],
      });
      setNewTag('');
      setShowTagPopup(false);
    }
  };

  const removeTag = (tagToRemove) => {
    setTourData({
      ...tourData,
      tags: tourData.tags.filter((tag) => tag !== tagToRemove),
    });
  };

  const handleDelete = async (tourId) => {
    try {
      const response = await axios.delete(`http://localhost:8084/delete_tour/${tourId}`);
      if (response.status === 200) {
        setTourId(tourId);
      }
    } catch (error) {
      console.error('Error deleting tour:', error);
    }
  };

  const confirmCheckpoints = async () => {
    try {
      const checkpoints = [];
      for (const marker of markers) {
        const checkpointData = {
          tour_id: tourId,
          name: marker.name,
          position: marker.number,
          longitude: marker.lng,
          latitude: marker.lat
        };
        checkpoints.push(checkpointData);
      }
      
      const response = await axios.put(`http://localhost:8084/addcheckpoint/${tourId}`,
        checkpoints,
        {
          withCredentials: true,
        }
      );
  
      if (response.status === 201) {
          // Show success dialog
          setShowSuccessDialog(true);
  
          // Clear markers
          setMarkers([]);
  
          // Hide tour creation modal
          setShowModal(false);
      }
    } catch (error) {
      console.error('Error adding checkpoints to tour:', error);
    }
  };
  

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formattedPrice = `${tourData.price} ${tourData.currency}`;
      const response = await axios.post('http://localhost:8084/createtour', {
        title: tourData.title,
        description: tourData.description,
        duration: tourData.duration + ' ' + tourData.durationUnit,
        difficulty: tourData.difficulty,
        tags: tourData.tags,
        price: formattedPrice
      }, {
        withCredentials: true,
      });

      if (response.status === 201) {
        setTourId(response.data['tour_id']);
        setShowModal(true);
      }
    } catch (error) {
      console.error('Error creating tour:', error);
    }
  };

  const handleTagKeyDown = (e) => {
    if (e.key === 'Enter' && newTag.trim() !== '') {
      e.preventDefault();
      confirmAddTag();
    }
  };

  const onLoad = (map) => {
    setMap(map);
  };

  const onMarkerClick = (marker) => {
    setSelectedMarker(marker);
  };

  const onMarkerDragEnd = (e, markerIndex) => {
    const newMarkers = [...markers];
    newMarkers[markerIndex].lat = e.latLng.lat();
    newMarkers[markerIndex].lng = e.latLng.lng();
    setMarkers(newMarkers);
  };

  const handleAddLocation = () => {
    if (name && number) {
      const newMarker = {
        lat: center.lat,
        lng: center.lng,
        draggable: true,
        name: name,
        number: parseInt(number, 10),
      };
      setMarkers([...markers, newMarker]);
      setName('');
      setNumber('');
    } else {
      alert('Please enter name and number first.');
    }
  };

  const handleDeleteLocation = (index) => {
    const newMarkers = [...markers];
    newMarkers.splice(index, 1);
    setMarkers(newMarkers);
    setSelectedMarker(null);
  };

  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371;
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
    return distance;
  };

  const calculateTotalDistance = () => {
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

  const calculateRoute = () => {
    if (markers.length > 1) {
      const sortedMarkers = markers.slice().sort((a, b) => a.number - b.number); // Sort markers by number
      const path = sortedMarkers.map(marker => ({ lat: marker.lat, lng: marker.lng })); // Extract path from sorted markers
  
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
  
  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container">
      <Typography variant="h4">Add Tour</Typography>
      <form>
        <FormControl fullWidth margin="normal">
          <TextField
            label="Title"
            name="title"
            value={tourData.title}
            onChange={handleChange}
            required
          />
        </FormControl>
        <FormControl fullWidth margin="normal">
          <TextField
            label="Description"
            name="description"
            value={tourData.description}
            onChange={handleChange}
            required
          />
        </FormControl>
        <FormControl fullWidth margin="normal">
          <TextField
            label="Duration"
            name="duration"
            value={tourData.duration}
            onChange={handleChange}
            type="number"
            required
          />
          <Select
            value={tourData.durationUnit}
            onChange={handleDurationUnitChange}
            name="durationUnit"
            fullWidth
          >
            <MenuItem value="minutes">Minutes</MenuItem>
            <MenuItem value="hours">Hours</MenuItem>
          </Select>
        </FormControl>
        <FormControl component="fieldset" margin="normal">
          <FormLabel component="legend">Difficulty</FormLabel>
          <RadioGroup
            name="difficulty"
            value={tourData.difficulty}
            onChange={handleChange}
            row
          >
            <FormControlLabel value="easy" control={<Radio />} label="Easy" />
            <FormControlLabel value="medium" control={<Radio />} label="Medium" />
            <FormControlLabel value="hard" control={<Radio />} label="Hard" />
          </RadioGroup>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <TextField
            label="Price"
            name="price"
            value={tourData.price}
            onChange={handleChange}
            type="number"
            required
          />
          <Select
            value={tourData.currency}
            onChange={(e) => setTourData({ ...tourData, currency: e.target.value })}
            name="currency"
            fullWidth
          >
            <MenuItem value="din">Dinar</MenuItem>
            <MenuItem value="usd">USD</MenuItem>
            <MenuItem value="eur">EUR</MenuItem>
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <Typography variant="h6">Tags</Typography>
          {tourData.tags.map((tag, index) => (
            <Chip
              key={index}
              label={tag}
              onDelete={() => removeTag(tag)}
              color="primary"
              variant="outlined"
            />
          ))}
          <Button variant="outlined" color="primary" onClick={handleAddTag}>
            Add Tag
          </Button>
        </FormControl>
        <Button variant="contained" color="primary" type="submit" onClick={handleSubmit}>
          Create Tour
        </Button>
      </form>

      <Dialog open={showTagPopup} onClose={() => setShowTagPopup(false)}>
        <DialogTitle>Add a New Tag</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="New Tag"
            fullWidth
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            onKeyDown={handleTagKeyDown}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTagPopup(false)} color="primary">
            Cancel
          </Button>
          <Button onClick={confirmAddTag} color="primary">
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {showModal && (
        <Dialog open={showModal} onClose={() => setShowModal(false)}>
          <DialogTitle>Tour Locations</DialogTitle>
          <DialogContent>
            <form>
              <TextField
                label="Location Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <TextField
                label="Location Number"
                value={number}
                onChange={(e) => setNumber(e.target.value)}
              />
              <Button onClick={handleAddLocation}>Add Location</Button>
            </form>
            <GoogleMap
              mapContainerStyle={containerStyle}
              center={center}
              zoom={10}
              onLoad={onLoad}
            >
              {markers.map((marker, index) => (
                <Marker
                  key={index}
                  position={{ lat: marker.lat, lng: marker.lng }}
                  draggable={marker.draggable}
                  onDragEnd={(e) => onMarkerDragEnd(e, index)}
                  onClick={() => onMarkerClick(marker)}
                >
                  {selectedMarker === marker && (
                    <InfoWindow onCloseClick={() => setSelectedMarker(null)}>
                      <div>
                        <h4>Name: {marker.name}</h4>
                        <p>Number: {marker.number}</p>
                        <Button onClick={() => handleDeleteLocation(index)}>Delete</Button> {/* Delete button */}
                      </div>
                    </InfoWindow>
                  )}
                </Marker>
              ))}
              {calculateRoute()}
              {directionsResponse && (
                <DirectionsRenderer
                  options={{
                    directions: directionsResponse,
                  }}
                />
              )}
            </GoogleMap>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => { setShowModal(false); handleDelete(tourId); }} color="primary">Cancel</Button> {/* Add handleDelete here */}
            <Button onClick={confirmCheckpoints} color="primary">Confirm</Button> {/* Add confirmCheckpoints here */}
          </DialogActions>
        </Dialog>
      )}
      <Dialog open={showSuccessDialog} onClose={() => setShowSuccessDialog(false)}>
        <DialogTitle>Tour Created</DialogTitle>
        <DialogContent>
          <Typography variant="body1">Checkpoints added successfully!</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowSuccessDialog(false);
            navigate('/'); // Redirect to home page
          }} color="primary">
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default AddTour;
