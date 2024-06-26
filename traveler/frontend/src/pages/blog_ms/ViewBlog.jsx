import React, { useEffect, useState } from "react";
import { useParams, Link  } from "react-router-dom";
import axios from 'axios';
import "../../css/view-blog.css";

const ViewBlog = () => {
    const { id } = useParams();
    const [blog, setBlog] = useState({});
    const [posts, setPosts] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [postData, setPostData] = useState({
        title: "",
        description: "",
        images: [],
        date: new Date().toISOString().slice(0, 10),
        status: "draft"
    });

    const openCreatePostModal = () => {
            setShowModal(true);
        };

        const closeCreatePostModal = () => {
            setShowModal(false);
        };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setPostData({ ...postData, [name]: value });
    };

    const handleCreatePost = async () => {
        // e.preventDefault();
        const { title, description, images, date, status } = postData;
        console.log({ title, description, images, date, status });
    
        try {
            const response = await axios.post(`http://localhost:8083/post/${id}`, {
                title,
                description,
                images,
                date,
                status
            }, {
                withCredentials: true,
                headers: {
                    'Content-Type': 'application/json'
                }
            });
    
            if (response.status === 200) {
                // const data = response.data;
                alert('Post created successfully!');
            }
    
        } catch (err) {
            console.error(err);
        }
    
        closeCreatePostModal();
    };
    


    const getAllPosts = async () => {
        try {
            const response = await fetch("http://localhost:8083/posts", {
                method: "GET",
                headers: { 'Content-Type': 'application/json' },
                withCredentials: true
            });

            if (response.ok) {
                const data = await response.json();
                setPosts(data.posts);
            }

        } catch (err) {
            console.error(err);
        }
    }

    const viewBlogById = async () => {
        try {
            const response = await fetch(`http://localhost:8083/blog/${id}`, {
                method: "GET",
                headers: { 'Content-Type': 'application/json' },
                withCredentials: true
            });

            if (response.ok) {
                const data = await response.json();
                setBlog(data.blog);

            } else {
                throw new Error("Error fetching blog");
            }
        } catch (err) {
            console.error(err);
        }
    }
    useEffect(()=>{
        getAllPosts();
    },[]);

    useEffect(() => {
        viewBlogById();
    },[]);

    return (
        <>
            <h1 className="blog-title">View Blog</h1>
            <div className="blog-wrapper">
                <div className="blog-container">
                    <div className="blog-info">
                        <p>Blog Title: <span>{blog.title}</span></p>
                        <p>Blog Description: <span>{blog.description}</span></p>
                        <p>Blog Author: <span>{blog.author}</span></p>
                    </div>
                    <div className="posts-container">
                        {posts
                            .filter(post => post.blog_id === +id)
                            .map(post => (
                                <div className="post-card" key={post.id}>
                                    <div className="post-info">
                                        <p>Title: {post.title}</p>
                                        <p>Description: {post.description}</p>
                                        <p>Post Content (To Be Done)</p>
                                        <Link to={`post/${post.id}`} className="see-post-btn">See More</Link>
                                    </div>
                                </div>
                            ))}
                        {posts.filter(post => post.blog_id === +id).length === 0 && (
                            <p className="no-posts-found">No posts found!</p>
                        )}
                    </div>
                </div>
            </div>
            {showModal && (
                <div className="modal">
                    <div className="modal-content">
                        <span className="close-btn" onClick={closeCreatePostModal}>X</span>
                        
                            <div className="form-input">
                                <label>Title:</label>
                                <input type="text" name="title" value={postData.title} onChange={handleInputChange} />
                            </div>
                            <div className="form-input">
                                <label>Description:</label>
                                <input type="text" name="description" value={postData.description} onChange={handleInputChange} />
                            </div>
                            <button className="create-post" type="button" onClick={handleCreatePost}>Create</button>
                       
                    </div>
                </div>
            )}
        </>
    );
}

export default ViewBlog;