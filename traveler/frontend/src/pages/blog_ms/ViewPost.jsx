import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "../../css/view-post.css";
import axios from "axios";

const ViewPost = () => {
  const { id } = useParams();
  const [post, setPost] = useState({});
  const [comments, setComments] = useState([]);

  const getPostComments = async () => {
    try {
      const { data } = await axios.get(`http://localhost:8083/post/${id}/comments`, {
        withCredentials: true,
        headers: { 'Content-Type': 'application/json' }
      });

      setComments(data.comments);
      console.log(data.comments);
    } catch (err) {
      console.log(err);
    }
  };

  const viewPostById = async () => {
    try {
      const { data } = await axios.get(`http://localhost:8083/post/${id}`, {
        withCredentials: true,
        headers: { 'Content-Type': 'application/json' }
      });

      setPost(data.post);
    } catch (err) {
      console.error("Error fetching blog:", err);
    }
  };

  useEffect(() => {
    viewPostById();
    getPostComments();
  }, [id]);

  return (
    <>
      <h1 className="post-title">View Post</h1>
      <div className="post-wrapper">
        <div className="post-container">
          <div className="post-info-card">
            <p>Post Title: <span>{post.title}</span></p>
            <p>Post Description: <span>{post.description}</span></p>
            <p>Date Published: <span>{new Date(post.created_at).toLocaleDateString()}</span></p>
          </div>

          <div className="comments-container">
            <h3>Comments Section</h3>
            <button className="like-post-btn">Like Post</button>
            {comments.length > 0 ? (
              comments.map(comment => (
                <div className="comment-card" key={comment.comment_id}>
                  <p>Author: {comment.author.username}</p>
                  <p>Comment: {comment.comment_text}</p>
                  <button className="reply-btn">Reply</button>
                  {comment.replies && comment.replies.map(reply => (
                    <div className="reply-card" key={reply.comment_id}>
                      <p>Author: {reply.author.username}</p>
                      <p>Reply: {reply.comment_text}</p>
                    </div>
                  ))}
                </div>
              ))
            ) : (
              <p className="empty-comments">No comments right now.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default ViewPost;
