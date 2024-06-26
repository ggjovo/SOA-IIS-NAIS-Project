import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "../../css/view-blogs.css";

const ViewBlogs = () => {
    const [blogs, setBlogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [recommendedBlogs, setRecommendedBlogs] = useState([]);

    useEffect(() => {
        const getAllBlogs = async () => {
            try {
                const { data } = await axios.get("http://localhost:8083/blogs", {
                    headers: { 'Content-Type': 'application/json' },
                    withCredentials: true
                });
                setBlogs(data.blogs);
                setLoading(false);
                fetchBlogDetails(data.blogs); // Fetch details for each blog
            } catch (error) {
                console.error("Error fetching blogs:", error);
                setLoading(false);
            }
        };

        const fetchBlogDetails = async (blogs) => {
            try {
                const blogDetailsPromises = blogs.map(async (blog) => {
                    const { data } = await axios.get(`http://localhost:8083/blog/${blog.id}`, {
                        headers: { 'Content-Type': 'application/json' },
                        withCredentials: true
                    });
                    return data.blog;
                });
                const blogDetails = await Promise.all(blogDetailsPromises);
                setBlogs(blogDetails);
            } catch (error) {
                console.error("Error fetching blog details:", error);
            }
        };

        const getRecommendedBlogs = async () => {
            try {
                const { data } = await axios.get("http://localhost:8085/recommend", {
                    withCredentials: true,
                    headers: { 'Content-Type': 'application/json' }
                });
                setRecommendedBlogs(data);
            } catch (error) {
                console.error("Error fetching recommended blogs:", error);
            }
        };

        getAllBlogs();
        getRecommendedBlogs();
    }, []);

    return (
        <>
            <h1 className="blogs-title">Blogs</h1>
            <button className="sort-blogs-btn">Sort Blogs</button>
            <div className="blogs-wrapper">
                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <>
                        {blogs.map(({ id, title, author, created_at }) => (
                            <div className="blog-card" key={id}>
                                {recommendedBlogs.some(blog => blog.id === id) && <span className="recommended-mark">Recommended</span>}
                                <div className="blogs-info">
                                    <p>Title: <span>{title}</span></p>
                                    <p>Author: <span>{author}</span></p>
                                    <p>Date Published: <span>{new Date(created_at).toLocaleDateString()}</span></p>
                                    <Link to={`/blog/${id}`} className="see-more-btn" id={id}>See More</Link>
                                </div>
                            </div>
                        ))}
                    </>
                )}
            </div>
        </>
    );
}

export default ViewBlogs;
