import { useState, useEffect } from "react";
import "../../css/create-blog.css";
import axios from 'axios';

const RatePlatform = () => {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [existingReview, setExistingReview] = useState(null);

  useEffect(() => {
    // Fetch the existing review when the component mounts
    const fetchReview = async () => {
      try {
        const response = await axios.get("http://localhost:8083/get_review", {
          withCredentials: true,
        });

        if (response.status === 200 && response.data) {
          setExistingReview(response.data);
          setRating(response.data.rating);
          setComment(response.data.comment);
        }
      } catch (err) {
        if (err.response && err.response.status === 404) {
          // No review found for the user
          setExistingReview(null);
        } else {
          console.error('Error fetching review:', err);
        }
      }
    };

    fetchReview();
  }, []);

  const handleStarClick = (index) => {
    setRating(index + 1);
  };

  const submitRating = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        "http://localhost:8083/platform_review",
        { rating, comment },
        {
          withCredentials: true,
          headers: { 'Content-Type': 'application/json' }
        }
      );

      if (response.status === 201) {
        alert(response.data.message || 'Rating submitted successfully!');
      } else {
        console.error(`Unexpected response code: ${response.status}`, response.data);
        alert('An unexpected error occurred. Please try again later.');
      }
    } catch (err) {
      console.error('Error submitting rating:', err);
      if (err.response) {
        console.error('Server responded with an error:', err.response.data);
        console.error('Status code:', err.response.status);
        alert(`Server error: ${err.response.data.message || 'An error occurred.'}`);
      } else if (err.request) {
        console.error('No response received:', err.request);
        alert('No response received from the server. Please try again later.');
      } else {
        console.error('Error setting up the request:', err.message);
        alert(`Error setting up the request: ${err.message}`);
      }
    }
  };

  const starStyles = {
    display: 'flex',
    gap: '5px',
    fontSize: '24px',
    cursor: 'pointer',
  };

  const starBaseStyle = {
    color: '#ccc',
  };

  const starFilledStyle = {
    color: '#ff0',
  };

  const existingReviewStyle = {
    marginBottom: '20px',
    padding: '10px',
    border: '1px solid #ccc',
    borderRadius: '5px',
  };

  return (
    <>
      <h1 className="create-blog-title">Rate Our Platform</h1>
      <div className="create-blog-wrapper">
        {existingReview && (
          <div className="existing-review" style={existingReviewStyle}>
            <h2>Your Current Review</h2>
            <div>
              <strong>Rating:</strong>
              <div className="star-rating" style={starStyles}>
                {[...Array(5)].map((star, index) => (
                  <span
                    key={index}
                    style={index < existingReview.rating ? starFilledStyle : starBaseStyle}
                  >
                    &#9733;
                  </span>
                ))}
              </div>
            </div>
            <div>
              <strong>Comment:</strong> <p>{existingReview.comment}</p>
            </div>
          </div>
        )}
        <div className="create-blog-form">
          <form onSubmit={submitRating}>
            <div className="form-input">
              <label>Rating:</label>
              <div className="star-rating" style={starStyles}>
                {[...Array(5)].map((star, index) => {
                  return (
                    <span
                      key={index}
                      style={index < rating ? starFilledStyle : starBaseStyle}
                      onClick={() => handleStarClick(index)}
                    >
                      &#9733;
                    </span>
                  );
                })}
              </div>
            </div>
            <div className="form-input">
              <label>Comment:</label>
              <textarea
                placeholder="Enter your comment here..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                required
              />
            </div>
            <button className="create-blog" type="submit">Submit</button>
          </form>
        </div>
      </div>
    </>
  );
};

export default RatePlatform;
