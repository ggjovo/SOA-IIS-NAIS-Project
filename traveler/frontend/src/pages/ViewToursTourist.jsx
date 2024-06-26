import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, Typography, Button, Chip, Grid, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { GoogleMap, LoadScript, Marker, InfoWindow } from '@react-google-maps/api';
import { useNavigate } from 'react-router-dom';
import '../css/cart.css';

function ViewToursTourist() {
  const [tours, setTours] = useState([]);
  const [selectedTour, setSelectedTour] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedMarker, setSelectedMarker] = useState(null);
  const [quantity, setQuantity] = useState('');
  const [showCartModal, setShowCartModal] = useState(false);
  const [cartItems, setCartItems] = useState([]);
  const [amount, setAmount] = useState(1);


  const navigate = useNavigate();
  const [map, setMap] = useState(null);

  const onLoad = (map) => {
    setMap(map);
  };

  useEffect(() => {
    const fetchTours = async () => {
      try {
        const response = await axios.get('http://localhost:8084/show_tours_tourist', { withCredentials: true });
        setTours(response.data.tours);
        console.log(response.data)
      } catch (error) {
        console.error('Error fetching tours:', error);
      }
    };

    fetchTours();
  }, []);

  const onMarkerClick = (marker) => {
    setSelectedMarker(marker);
  };

  const handleOpenModal = (tour) => {
    console.log(tour);
    setSelectedTour(tour);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedTour(null);
  };

  const getCartItems = async () => {
      try {
        const response = await axios.get('http://localhost:8084/view_cart', { withCredentials: true });

        console.log(response.data)

        setCartItems(response.data.tours)
        setAmount(response.data.total_price);

      } catch (error) {
        console.error('Error fetching tours:', error);
      }
  }

  useEffect(() => {
    const interval = setInterval(() => {
      getCartItems();
    }, 3500); 

    return () => clearInterval(interval); 
  }, []);

  const containerStyle = {
    width: '100%',
    height: '400px',
  };

  const center = {
    lat: -34.397,
    lng: 150.644,
  };



  const handleAddToCart = async (id) => {
    getCartItems();
    console.log('quantity for certain item: ', quantity);
    console.log('tour id: ', id);

    try {
        const response = await axios.put(`http://localhost:8084/add_to_cart/${id}`, 
            { quantity: String(quantity) },  
            {
                withCredentials: true,
                headers: {
                    'Content-Type': 'application/json',
                }
            }
        );

        const data = response.data;
        console.log('data: ', data);

    } catch (error) {
        console.error('Error adding to cart: ', error);
    }
};


const handleCheckOut = async () => {
  try {
      const response = await axios.delete('http://localhost:8084/check_out', {
          withCredentials: true,
          headers: {
              'Content-Type': 'application/json',
          }
      });

      const data = response.data;
      console.log(data);
  } catch (error) {
      console.error('Error during checkout: ', error);
  }
};

const removeOneItemFromCart = async (id) => {
  try {
      const response = await axios.delete(`http://localhost:8084/remove_from_cart/${id}`, {
          withCredentials: true,
          headers: {
              'Content-Type': 'application/json',
          }
      });

      const data = response.data;
      console.log(data);
  } catch (error) {
      console.error('Error removing item from cart: ', error);
  }
};


const removeAllQuantityFromCart = async (id) => {
  try {
      const response = await axios.delete(`http://localhost:8084/remove_all_from_cart/${id}`, {
          withCredentials: true,
          headers: {
              'Content-Type': 'application/json',
          }
      });

      const data = response.data;
      console.log(data);
  } catch (error) {
      console.error('Error removing all quantities from cart: ', error);
  }
};
  return (
    <>
    {showCartModal ? <div className='cart-modal-on'><h2>Your Cart</h2> 
    <div className='card-items'>
    {cartItems.length > 0 && cartItems.map((tour) => (
              <div className="card-item" key={tour.id}>
                <p>Title: {tour.title}</p>
                <p>Description: {tour.description}</p>
                <p>Difficulty: {tour.difficulty}</p>
                <p>Quantity: {tour.quantity}</p>
                <p>Price: {tour.price}</p>
                <button className='remove-one' onClick={() => removeOneItemFromCart(tour.id)}>Remove One</button>
                <button className='remove-all' onClick={() => removeAllQuantityFromCart(tour.id)}>Remove All</button>
              </div>
            ))}
            <p>Total price: {amount}</p>
      <button className='checkout-btn' onClick={handleCheckOut}> Checkout</button>
      </div> <button className='close-cart' onClick={()=> setShowCartModal(false)}>X</button></div> : ''}
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', justifyContent: 'center' }}>
        <button className='check-card-btn' onClick={()=> setShowCartModal(true)} >Check Card</button>
      <Grid container spacing={-20}>
        {tours.map((tour) => (
          <Grid item xs={12} sm={6} md={4} key={tour.id}>
            <Card variant="outlined" style={{ height: '300px', overflowY: 'auto', margin: '20px' }}>
              <Typography variant="h5" component="div" gutterBottom>
                {tour.title}
              </Typography>
              <Typography variant="body1" color="textSecondary">
                {tour.description}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Duration  : {tour.duration}
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
              <button onClick={() => {handleAddToCart(tour.id)}} className='add-to-cart-btn'>Add to cart</button>
              <input type="number" className='quantity-cart' onChange={(e)=>{
                setQuantity(e.target.value)
              }} placeholder='Enter quatity...' />
            </Card>
            <div style={{ height: '200px' }}>
            <LoadScript googleMapsApiKey="AIzaSyCufve6BuSX50Ep7dlucnuiiqKyqYgDSf4">
              <Dialog
                open={showModal}
                onClose={() => setShowModal(false)}
                fullWidth
                maxWidth="md"
              >
              <DialogTitle>Starting Checkpoint</DialogTitle>
              <DialogContent>
                <GoogleMap
                  mapContainerStyle={containerStyle}
                  center={center}
                  zoom={10}
                  onLoad={onLoad}
                >
      
                  {/* Render markers for each checkpoint */}
                  {selectedTour && selectedTour.first_checkpoint_name && selectedTour.first_checkpoint_name?.map((name, index) => (
                    <Marker
                      key={`${name}-${index}`}
                      position={{
                        lat: selectedTour.first_checkpoint_latitude[index],
                        lng: selectedTour.first_checkpoint_longitude[index],
                      }}
                      onClick={() => onMarkerClick(name)}
                    >
                      {selectedMarker === name && (
                      <InfoWindow onCloseClick={() => setSelectedMarker(null)}>
                        <div>
                          <h4>Name: {name}</h4>
                          <p>Position: {selectedTour.first_checkpoint_position[index]}</p>
                        </div>
                      </InfoWindow>
                      )}
                    </Marker>
                  ))}
                </GoogleMap>
                </DialogContent>
              </Dialog>
            </LoadScript>
          </div>
        </Grid>
      ))}
    </Grid>
  </div>
  </>
  );
}

export default ViewToursTourist;
