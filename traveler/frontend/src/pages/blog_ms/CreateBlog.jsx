import { useState } from "react";
import "../../css/create-blog.css";
import axios from 'axios';

const CreateBlog = () => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const createBlog = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        "http://localhost:8083/blog",
        { title, description },
        {
          withCredentials: true,
          headers: { 'Content-Type': 'application/json' }
        }
      );

      if (response.status === 201) {
        alert(response.data.message || 'Blog created successfully!');
      } else {
        console.error(`Unexpected response code: ${response.status}`, response.data);
        alert('An unexpected error occurred. Please try again later.');
      }
    } catch (err) {
      console.error('Error creating blog:', err);
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Server responded with an error:', err.response.data);
        console.error('Status code:', err.response.status);
        alert(`Server error: ${err.response.data.message || 'An error occurred.'}`);
      } else if (err.request) {
        // The request was made but no response was received
        console.error('No response received:', err.request);
        alert('No response received from the server. Please try again later.');
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Error setting up the request:', err.message);
        alert(`Error setting up the request: ${err.message}`);
      }
    }
  };

  return (
    <>
      <h1 className="create-blog-title">Create Personal Blog</h1>
      <div className="create-blog-wrapper">
        <div className="create-blog-form">
          <form onSubmit={createBlog}>
            <div className="form-input">
              <label>Blog Title:</label>
              <input
                type="text"
                placeholder="Enter your title here..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="form-input">
              <label>Blog Description:</label>
              <input
                type="text"
                placeholder="Enter your description here..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>
            <button className="create-blog" type="submit">Create</button>
          </form>
        </div>
      </div>
    </>
  );
};

export default CreateBlog;
