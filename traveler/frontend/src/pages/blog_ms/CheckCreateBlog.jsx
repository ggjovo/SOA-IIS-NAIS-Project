import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ViewBlog from './MyBlog';
import CreateBlog from './CreateBlog';

const CheckCreateBlog = () => {
  const [userBlog, setUserBlog] = useState(null);
  const [loading, setLoading] = useState(true);
  

  useEffect(() => {
    const getUserBlog = async () => {
      try {
        const response = await axios.get('http://localhost:8083/get_user_blog', {
          withCredentials: true,
          headers: { 'Content-Type': 'application/json' }
        });
        setUserBlog(response.data || null);
      } catch (error) {
        console.error('Error retrieving user blog:', error);
      } finally {
        setLoading(false);
      }
    };

    getUserBlog();
  }, []);

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <>
      {userBlog !== null ? (
        <ViewBlog userBlog={userBlog.id} />
      ) : (
        <CreateBlog />
      )}
    </>
  );
};

export default CheckCreateBlog;
