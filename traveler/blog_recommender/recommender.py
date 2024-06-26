from neo4j import GraphDatabase
from flask import jsonify
from auth import authenticate_user

# Neo4j connection parameters
neo4j_uri = "bolt://neo4j:7687"
neo4j_user = "neo4j"
neo4j_password = "123456789"


# Define Neo4j driver
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

def get_posts_for_user(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401
    
    user_id = int(user_info['id'])

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[:LIKED|AUTHOR_OF]->(entity)
            WITH collect(entity.id) AS user_interactions
            MATCH (post:Post)
            WHERE NOT post.id IN user_interactions
            OPTIONAL MATCH (post)<-[:LIKES]-(likers)
            WITH post, count(likers) AS like_count
            OPTIONAL MATCH (post)<-[:HAS_COMMENT]-(comments)
            WITH post, like_count, count(comments) AS comment_count
            RETURN post, like_count, comment_count
            ORDER BY like_count DESC, comment_count DESC, post.created_at DESC
            LIMIT 10;
            """,
            user_id=user_id
        )

        posts = []
        for record in result:
            post = dict(record['post'])
            post['like_count'] = record['like_count']
            post['comment_count'] = record['comment_count']
            if 'created_at' in post:
                post['created_at'] = str(post['created_at'])
            posts.append(post)

        return jsonify(posts)


def get_most_popular_blogs():
    '''
    1.
    Cold-start Query for Blogs (Most Popular Blogs by total post likes in that blog)
    ''' 
    with driver.session() as session:
        result = session.run(
            """
            MATCH (b:Blog)-[:CONTAINS]->(p:Post)<-[:LIKED]-(u:User)
            WITH b, count(p) AS postCount, count(u) AS totalLikes
            WHERE postCount > 0
            RETURN b.id AS blogId, b.title AS blogTitle, totalLikes
            ORDER BY totalLikes DESC
            LIMIT 10;
            """
        )

        posts_most_popular_blogs = [
            {
                "blogId": record["blogId"],
                "blogTitle": record["blogTitle"],
                "totalLikes": record["totalLikes"]
            }
            for record in result
        ]
        
        return jsonify(posts_most_popular_blogs)

def get_most_popular_posts():
    '''
    2.
    Cold-start Query for Posts (Most Popular Posts by total post likes)
    ''' 
    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Post)<-[:LIKED]-(u:User)
            WITH p, count(u) AS likeCount
            WHERE likeCount > 0
            RETURN p.id AS postId, p.title AS postTitle, likeCount
            ORDER BY likeCount DESC
            LIMIT 10;
            """
        )

        posts_most_popular_posts = [
            {
                "postId": record["postId"],
                "postTitle": record["postTitle"],
                "totalLikes": record["likeCount"]
            }
            for record in result
        ]
        
        return jsonify(posts_most_popular_posts)
    
def get_most_liked_blog_from_user(user_id):
    '''
    3.
    find the most liked blog by the user (in percent of all total posts liked)
    User Has Only Interactions with Blogs/Posts 
    '''
    with driver.session() as session:
        result = session.run(
            """
            MATCH (b:Blog)-[:CONTAINS]->(p:Post)<-[:LIKED]-(u:User {id: $userId})
            WITH b, u, count(p) AS totalPosts, collect(DISTINCT p) AS likedPosts
            WHERE size(likedPosts) > 0
            RETURN b.id AS blogId, b.title AS blogTitle, u.id AS userId,
                   size(likedPosts) * 100 / totalPosts AS percentLiked
            ORDER BY percentLiked desc
            LIMIT 10;
            """,
            userId = user_id
        )
        
        posts_most_liked_blogs = [
            {
                "blogId": record["blogId"],
                "blogTitle": record["blogTitle"],
                "percentLiked": record["percentLiked"]
            }
            for record in result
        ]
        
        return jsonify(posts_most_liked_blogs)
    
def get_most_liked_blog_from_user_follows(user_id):
    '''
    4.
    find the most followed and liked user blog from the user followed
    User Has Only Interactions with Other Users
    '''
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $userId})-[:FOLLOWS]->(f:User)-[:AUTHOR_OF]->(b:Blog)
            WITH b, count(f) AS followerCount
            MATCH (b)-[:CONTAINS]->(p:Post)<-[:LIKED]-(lu:User)
            WITH b, followerCount, count(lu) AS totalLikes
            WHERE followerCount > 0
            RETURN b.id AS blogId, b.title AS blogTitle, followerCount, totalLikes
            ORDER BY followerCount DESC, totalLikes DESC
            LIMIT 10;
            """,
            userId = user_id
        )

        result_list = [
            {
                "blogId": record["blogId"],
                "blogTitle": record["blogTitle"],
                "followerCount": record["followerCount"],
                "totalLikes": record["totalLikes"]
            }
            for record in result
        ]
        
        return jsonify(result_list)

def get_simular_blogs_from_user_likes(user_id):
    '''
    5.
    based on the liked posts it recommends simular blog (based on tags)
    Content-Based Recommendation for Blogs
    '''
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $userId})-[:LIKED]->(:Post)<-[:CONTAINS]-(b:Blog)-[:CONTAINS]->(t:Tag)
            WITH t, count(b) AS blogCount
            MATCH (recommendedBlog:Blog)-[:CONTAINS]->(t)
            WITH recommendedBlog, blogCount, count(recommendedBlog) AS recCount
            WHERE blogCount > 0
            RETURN recommendedBlog.id AS blogId, recommendedBlog.title AS blogTitle, recCount
            ORDER BY recCount DESC
            LIMIT 10;
            """,
            userId = user_id
        )

        result_list = [
            {
                "blogId": record["blogId"],
                "blogTitle": record["blogTitle"],
                "recCount": record["recCount"]
            }
            for record in result
        ]
        
        return jsonify(result_list)
    
def get_simular_post_from_user_likes(user_id):
    '''
    6.
    based on the liked posts it recommends simular posts (based on tags)
    Content-Based Recommendation for Posts
    '''
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $userId})-[:LIKED]->(:Post)-[:CONTAINS]->(t:Tag)
            WITH t, count(t) AS tagCount
            MATCH (recommendedPost:Post)-[:CONTAINS]->(t)
            WITH recommendedPost, tagCount, count(recommendedPost) AS recCount
            WHERE tagCount > 0
            RETURN recommendedPost.id AS postId, recommendedPost.title AS postTitle, recCount
            ORDER BY recCount DESC
            LIMIT 10;
            """,
            userId = user_id
        )

        result_list = [
            {
                "postId": record["postId"],
                "postTitle": record["postTitle"],
                "recCount": record["recCount"]
            }
            for record in result
        ]
        
        return jsonify(result_list)
    

  
def get_simular_blog_from_user_follows(user_id):
    '''
    7.
    based on the followed users it recommends most liked blogs
    Collaborative Filtering Recommendation of Blogs
    '''
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $userId})-[:FOLLOWS]->(f:User)-[:LIKED]->(:Post)<-[:CONTAINS]-(b:Blog)
            WITH b, count(f) AS followerCount
            MATCH (b)-[:CONTAINS]->(p:Post)<-[:LIKED]-(lu:User)
            WITH b, followerCount, count(lu) AS totalLikes
            WHERE followerCount > 0
            RETURN b.id AS blogId, b.title AS blogTitle, totalLikes
            ORDER BY totalLikes DESC
            LIMIT 10;
            """,
            userId = user_id
        )

        result_list = [
            {
                "blogId": record["blogId"],
                "blogTitle": record["blogTitle"],
                "totalLikes": record["totalLikes"]
            }
            for record in result
        ]
        
        return jsonify(result_list)
    
def get_simular_posts_from_user_follows(user_id):
    '''
    8.
    based on the followed users it recommends most liked posts
    Collaborative Filtering Recommendation for Posts
    '''
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $userId})-[:FOLLOWS]->(f:User)-[:LIKED]->(p:Post)
            WITH p, count(f) AS followerCount
            MATCH (p)<-[:LIKED]-(lu:User)
            WITH p, followerCount, count(lu) AS totalLikes
            WHERE followerCount > 0
            RETURN p.id AS postId, p.title AS postTitle, totalLikes
            ORDER BY totalLikes DESC
            LIMIT 10;
            """,
            userId = user_id
        )

        result_list = [
            {
                "postId": record["postId"],
                "postTitle": record["postTitle"],
                "totalLikes": record["totalLikes"]
            }
            for record in result
        ]
        
        return jsonify(result_list)
    

def get_simular_users_from_user_follows(user_id):
    '''
    9.
    based on the followed users it recommends users that have followers incommon
    Recommendation for Users to Follow
    '''
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $userId})-[:FOLLOWS]->(f:User)-[:FOLLOWS]->(recommendedUser:User)
            WITH u, recommendedUser, count(f) AS commonFollowers
            WHERE NOT (u)-[:FOLLOWS]->(recommendedUser)
            RETURN recommendedUser.id AS userId, recommendedUser.username AS username, commonFollowers
            ORDER BY commonFollowers DESC
            LIMIT 10;
            """,
            userId = user_id
        )

        result_list = [
            {
                "userId": record["userId"],
                "username": record["username"],
                "commonFollowers": record["commonFollowers"]
            }
            for record in result
        ]
        
        return jsonify(result_list)
    
def get_most_active_user():
    '''
    10.
    based on the comment likes, posts, post likes and comment posts.
    Most active user
    '''
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User)
            OPTIONAL MATCH (u)-[:AUTHOR_OF]->(b:Blog)-[:CONTAINS]->(p:Post)
            OPTIONAL MATCH (u)-[:LIKED]->(l:Post)
            OPTIONAL MATCH (u)-[:AUTHOR_OF]->(c:Comment)
            WITH u, count(DISTINCT p) AS postCount, count(DISTINCT l) AS likeCount, count(DISTINCT c) AS commentCount
            RETURN u.id AS userId, u.username AS userName, 
                (postCount + likeCount + commentCount) AS totalActivity,
                postCount, likeCount, commentCount
            ORDER BY totalActivity DESC
            LIMIT 10;
            """
        )

        result_list = [
            {
                "userId": record["userId"],
                "userName": record["userName"],
                "totalActivity": record["totalActivity"],
                "postCount": record["postCount"],
                "likeCount": record["likeCount"],
                "commentCount": record["commentCount"]
            }
            for record in result
        ]
        
        return jsonify(result_list)
    
def get_best_rated_blogs():
    '''
    11.
    get the best rated blogs as well as their rating
    Best rated blogs
    '''

    with driver.session() as session:
        result = session.run(
            """
            MATCH (b:Blog)<-[r:RATED]-(u:User)
            WITH b, avg(r.rating) AS avgRating, count(r) AS ratingCount
            WHERE ratingCount > 0
            RETURN b.id AS blogId, b.title AS blogTitle, avgRating, ratingCount
            ORDER BY avgRating DESC
            LIMIT 10;
            """
        )

        result_list = [
            {
                "blogId": record["blogId"],
                "blogTitle": record["blogTitle"],
                "avgRating": record["avgRating"],
                "ratingCount": record["ratingCount"],
            }
            for record in result
        ]
        
        return jsonify(result_list)

def get_most_popular_tags():
    '''
    12.
    Get most popular tags
    '''

    with driver.session() as session:
        result = session.run(
            """
            MATCH (t:Tag)<-[:CONTAINS]-(p:Post)
            WITH t, count(p) AS postCount
            WHERE postCount > 0
            RETURN t.id AS tagId, t.tag_name AS tagName, postCount
            ORDER BY postCount DESC
            LIMIT 10;
            """
        )

        result_list = [
            {
                "tagId": record["tagId"],
                "tagName": record["tagName"],
                "postCount": record["postCount"],
            }
            for record in result
        ]
        
        return jsonify(result_list)
    
