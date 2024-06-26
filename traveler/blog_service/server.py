from concurrent import futures
import grpc
import blog_pb2
import blog_pb2_grpc
import psycopg2
from auth import authenticate_user
from db_specs import db_config
from datetime import datetime

class BlogService(blog_pb2_grpc.BlogServiceServicer):

    def CreateBlog(self, request, context):
        token = request.token
        if not token:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return blog_pb2.BlogResponse()

        authenticated, user_info = authenticate_user(token)
        if not authenticated:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return blog_pb2.BlogResponse()

        user_id = int(user_info['id'])
        title = request.title
        description = request.description

        if not all([title, description]):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Incomplete data provided')
            return blog_pb2.BlogResponse()

        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO blogs (user_id, title, description) VALUES (%s, %s, %s)",
                           (user_id, title, description))
            conn.commit()
            cursor.close()
            conn.close()
            return blog_pb2.BlogResponse(message='Blog created successfully')
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error creating blog: ' + str(e))
            return blog_pb2.BlogResponse()

    def CreatePost(self, request, context):
        token = request.token
        if not token:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return blog_pb2.PostResponse()

        authenticated, user_info = authenticate_user(token)
        if not authenticated:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return blog_pb2.PostResponse()

        user_id = int(user_info['id'])
        blog_id = request.blog_id
        title = request.title
        description = request.description
        date = request.date
        images = request.images
        status = request.status or 'draft'

        if not all([title, description, date]):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Incomplete data provided')
            return blog_pb2.PostResponse()

        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM blogs WHERE id = %s", (blog_id,))
            blog_user_id = cursor.fetchone()
            if not blog_user_id or blog_user_id[0] != user_id:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('Unauthorized: Blog does not exist or does not belong to the user')
                return blog_pb2.PostResponse()

            cursor.execute("INSERT INTO posts (blog_id, title, description, images, status) VALUES (%s, %s, %s, %s, %s)",
                           (blog_id, title, description, images, status))
            conn.commit()
            cursor.close()
            conn.close()
            return blog_pb2.PostResponse(message='Post created successfully')
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error creating post: ' + str(e))
            return blog_pb2.PostResponse()

    def PostComment(self, request, context):
        token = request.token
        if not token:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return blog_pb2.CommentResponse()

        authenticated, user_info = authenticate_user(token)
        if not authenticated:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return blog_pb2.CommentResponse()

        user_id = int(user_info['id'])
        post_id = request.post_id
        comment_text = request.comment_text

        if not all([post_id, comment_text]):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Incomplete data provided')
            return blog_pb2.CommentResponse()

        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO comments (post_id, user_id, comment_text) VALUES (%s, %s, %s)",
                           (post_id, user_id, comment_text))
            conn.commit()
            cursor.close()
            conn.close()
            return blog_pb2.CommentResponse(message='Comment posted successfully')
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error posting comment: ' + str(e))
            return blog_pb2.CommentResponse()

    def EditComment(self, request, context):
        token = request.token
        if not token:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return blog_pb2.CommentResponse()

        authenticated, user_info = authenticate_user(token)
        if not authenticated:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return blog_pb2.CommentResponse()

        user_id = int(user_info['id'])
        comment_id = request.comment_id
        new_comment_text = request.comment_text

        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("UPDATE comments SET comment_text = %s, last_edited_at = CURRENT_TIMESTAMP WHERE id = %s AND user_id = %s",
                           (new_comment_text, comment_id, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return blog_pb2.CommentResponse(message='Comment edited successfully')
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error editing comment: ' + str(e))
            return blog_pb2.CommentResponse()

    def GetAllPosts(self, request, context):
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts")
            posts = cursor.fetchall()
            cursor.close()
            conn.close()

            formatted_posts = []
            for post in posts:
                post_dict = {
                    'id': post[0],
                    'blog_id': post[1],
                    'title': post[2],
                    'description': post[3],
                    'created_at': post[6].strftime("%Y-%m-%d %H:%M:%S") if isinstance(post[6], datetime) else str(post[6])
                }
                formatted_posts.append(post_dict)

            return blog_pb2.PostsResponse(posts=formatted_posts)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error retrieving posts: ' + str(e))
            return blog_pb2.PostsResponse()

    def GetAllBlogs(self, request, context):
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blogs")
            blogs = cursor.fetchall()
            cursor.close()
            conn.close()

            formatted_blogs = []
            for blog in blogs:
                blog_dict = {
                    'id': blog[0],
                    'user_id': blog[1],
                    'title': blog[2],
                    'description': blog[3],
                    'created_at': blog[4].strftime("%Y-%m-%d %H:%M:%S")
                }
                formatted_blogs.append(blog_dict)

            return blog_pb2.BlogsResponse(blogs=formatted_blogs)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error retrieving blogs: ' + str(e))
            return blog_pb2.BlogsResponse()

    def GetBlogById(self, request, context):
        blog_id = request.blog_id
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT b.id, b.user_id, b.title, b.description, b.created_at, u.username FROM blogs b INNER JOIN users u ON b.user_id = u.id WHERE b.id = %s", (blog_id,))
            blog = cursor.fetchone()
            cursor.close()
            conn.close()
            if blog:
                blog_dict = {
                    'id': blog[0],
                    'user_id': blog[1],
                    'title': blog[2],
                    'description': blog[3],
                    'created_at': blog[4].strftime("%Y-%m-%d %H:%M:%S"),
                    'author': blog[5]
                }
                return blog_pb2.BlogResponse(blog=blog_dict)
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('Blog not found')
                return blog_pb2.BlogResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error retrieving blog: ' + str(e))
            return blog_pb2.BlogResponse()

    def GetPostById(self, request, context):
        post_id = request.post_id
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT id, blog_id, title, description, images, status, created_at FROM posts WHERE id = %s", (post_id,))
            post = cursor.fetchone()
            cursor.close()
            conn.close()
            if post:
                post_dict = {
                    'id': post[0],
                    'blog_id': post[1],
                    'title': post[2],
                    'description': post[3],
                    'images': post[4],
                    'status': post[5],
                    'created_at': post[6].strftime("%Y-%m-%d %H:%M:%S"),
                }
                return blog_pb2.PostResponse(post=post_dict)
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('Post not found')
                return blog_pb2.PostResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error retrieving post: ' + str(e))
            return blog_pb2.PostResponse()

    def GetCommentsByPostId(self, request, context):
        post_id = request.post_id
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT c.id, c.parent_comment_id, c.user_id, c.comment_text, c.likes, c.created_at, u.username FROM comments c INNER JOIN users u ON c.user_id = u.id WHERE c.post_id = %s ORDER BY c.id", (post_id,))
            comments = cursor.fetchall()
            cursor.close()
            conn.close()

            comments_dict = {}
            for comment in comments:
                comment_id, parent_comment_id, user_id, comment_text, likes, created_at, username = comment
                if parent_comment_id is None:
                    comments_dict[comment_id] = {
                        'comment_id': comment_id,
                        'parent_comment_id': parent_comment_id,
                        'comment_text': comment_text,
                        'author': {'user_id': user_id, 'username': username},
                        'created_at': created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        'likes': likes,
                        'replies': []
                    }
                else:
                    if parent_comment_id in comments_dict:
                        comments_dict[parent_comment_id]['replies'].append({
                            'comment_id': comment_id,
                            'parent_comment_id': parent_comment_id,
                            'comment_text': comment_text,
                            'author': {'user_id': user_id, 'username': username},
                            'created_at': created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            'likes': likes
                        })

            return blog_pb2.CommentsResponse(comments=list(comments_dict.values()))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error retrieving comments for post: ' + str(e))
            return blog_pb2.CommentsResponse()

import logging

def serve():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    blog_pb2_grpc.add_BlogServiceServicer_to_server(BlogService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    logger.info("gRPC server is running on port 50053...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
