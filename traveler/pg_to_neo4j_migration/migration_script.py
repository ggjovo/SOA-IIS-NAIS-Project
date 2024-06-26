import psycopg2
from neo4j import GraphDatabase

# PostgreSQL connection parameters
pg_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'
}

# Neo4j connection parameters
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "123456789"

# Connect to PostgreSQL
def connect_to_postgres():
    try:
        conn = psycopg2.connect(**pg_config)
        return conn
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL:", e)

# Connect to Neo4j
def connect_to_neo4j():
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        return driver
    except Exception as e:
        print("Error connecting to Neo4j:", e)

# Helper function to check if a table exists in PostgreSQL
def table_exists(conn, table_name):
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='{table_name}');")
            return cursor.fetchone()[0]
    except psycopg2.Error as e:
        print(f"Error checking existence of table {table_name}:", e)
        return False

# Migrate users from PostgreSQL to Neo4j
def migrate_users(conn, driver):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        CREATE (u:User {
                            id: $id, username: $username, role: $role
                        })
                        """,
                        id=row[0], username=row[1], role=row[4]
                    )
        print("Users migrated successfully.")
    except psycopg2.Error as e:
        print("Error migrating users:", e)

# Migrate blogs from PostgreSQL to Neo4j
def migrate_blogs(conn, driver):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM blogs")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        MATCH (u:User {id: $user_id})
                        CREATE (u)-[:AUTHOR_OF]->(b:Blog {
                            id: $id, title: $title, description: $description, 
                            created_at: $created_at
                        })
                        """,
                        id=row[0], title=row[2], description=row[3], created_at=row[4], user_id=row[1]
                    )
        print("Blogs migrated successfully.")
    except psycopg2.Error as e:
        print("Error migrating blogs:", e)
        
# Migrate posts from PostgreSQL to Neo4j
def migrate_posts(conn, driver):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM posts")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        MATCH (b:Blog {id: $blog_id})
                        CREATE (b)-[:CONTAINS]->(p:Post {
                            id: $id, title: $title, description: $description, 
                            images: $images, status: $status, created_at: $created_at
                        })
                        """,
                        id=row[0], title=row[2], description=row[3], images=row[4], status=row[5], created_at=row[6], blog_id=row[1]
                    )
        print("Posts migrated successfully.")
    except psycopg2.Error as e:
        print("Error migrating posts:", e)

# Migrate comments from PostgreSQL to Neo4j
def migrate_comments(conn, driver):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM comments")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        MATCH (p:Post {id: $post_id}), (u:User {id: $user_id})
                        CREATE (p)-[:HAS_COMMENT]->(c:Comment {
                            id: $id, comment_text: $comment_text, likes: $likes, 
                            created_at: $created_at, last_edited_at: $last_edited_at
                        })
                        CREATE (u)-[:AUTHOR_OF]->(c)
                        """,
                        id=row[0], comment_text=row[4], likes=row[5], created_at=row[6], last_edited_at=row[7], post_id=row[1], user_id=row[3]
                    )
        print("Comments migrated successfully.")
    except psycopg2.Error as e:
        print("Error migrating comments:", e)

# Migrate likes from PostgreSQL to Neo4j
def migrate_likes(conn, driver):
    try:
        with conn.cursor() as cursor:
            # Likes on posts
            cursor.execute("SELECT user_id, post_id FROM post_likes")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        MATCH (u:User {id: $user_id}), (p:Post {id: $post_id})
                        CREATE (u)-[:LIKED]->(p)
                        """,
                        user_id=row[0], post_id=row[1]
                    )
            # Likes on comments
            cursor.execute("SELECT user_id, comment_id FROM comment_likes")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        MATCH (u:User {id: $user_id}), (c:Comment {id: $comment_id})
                        CREATE (u)-[:LIKED]->(c)
                        """,
                        user_id=row[0], comment_id=row[1]
                    )
        print("Likes migrated successfully.")
    except psycopg2.Error as e:
        print("Error migrating likes:", e)

# Migrate follows from PostgreSQL to Neo4j
def migrate_follows(conn, driver):
    try:
        if table_exists(conn, "user_followings"):
            with conn.cursor() as cursor:
                cursor.execute("SELECT follower_id, following_id FROM user_followings")
                for row in cursor.fetchall():
                    with driver.session() as session:
                        session.run(
                            """
                            MATCH (follower:User {id: $follower_id}), (following:User {id: $following_id})
                            CREATE (follower)-[:FOLLOWS]->(following)
                            """,
                            follower_id=row[0], following_id=row[1]
                        )
            print("Follows migrated successfully.")
        else:
            print("Table 'user_followings' does not exist, skipping follows migration.")
    except psycopg2.Error as e:
        print("Error migrating follows:", e)

# Migrate comment replies from PostgreSQL to Neo4j
def migrate_comment_replies(conn, driver):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, parent_comment_id FROM comments WHERE parent_comment_id IS NOT NULL")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        MATCH (c:Comment {id: $comment_id}), (parent:Comment {id: $parent_comment_id})
                        CREATE (c)-[:REPLY_TO]->(parent)
                        """,
                        comment_id=row[0], parent_comment_id=row[1]
                    )
        print("Comment replies migrated successfully.")
    except psycopg2.Error as e:
        print("Error migrating comment replies:", e)

# Migrate blog ratings from PostgreSQL to Neo4j
def migrate_blog_ratings(conn, driver):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, blog_id, rating FROM blog_ratings")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        MATCH (u:User {id: $user_id}), (b:Blog {id: $blog_id})
                        CREATE (u)-[:RATED {rating: $rating}]->(b)
                        """,
                        user_id=row[0], blog_id=row[1], rating=row[2]
                    )
        print("Blog ratings migrated successfully.")
    except psycopg2.Error as e:
        print("Error migrating blog ratings:", e)

# Migrate tags from PostgreSQL to Neo4j
def migrate_tags(conn, driver):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tags")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        CREATE (t:Tag {
                            id: $id, tag_name: $tag_name
                        })
                        """,
                        id=row[0], tag_name=row[1]
                    )
        print("Tags migrated successfully.")
    except psycopg2.Error as e:
        print("Error migrating tags:", e)

# Migrate blog tags from PostgreSQL to Neo4j
def migrate_blog_tags(conn, driver):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT blog_id, tag_id FROM BlogTags")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        MATCH (b:Blog {id: $blog_id}), (t:Tag {id: $tag_id})
                        CREATE (b)-[:CONTAINS]->(t)
                        """,
                        blog_id=row[0], tag_id=row[1]
                    )
        print("Blog tags migrated successfully.")
    except psycopg2.Error as e:
        print("Error migrating blog tags:", e)

# Migrate post tags from PostgreSQL to Neo4j
def migrate_post_tags(conn, driver):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT post_id, tag_id FROM PostTags")
            for row in cursor.fetchall():
                with driver.session() as session:
                    session.run(
                        """
                        MATCH (p:Post {id: $post_id}), (t:Tag {id: $tag_id})
                        CREATE (p)-[:CONTAINS]->(t)
                        """,
                        post_id=row[0], tag_id=row[1]
                    )
        print("Post tags migrated successfully.")
    except psycopg2.Error as e:
        print("Error migrating post tags:", e)

# Main migration function
def migrate_data():
    pg_conn = connect_to_postgres()
    neo4j_driver = connect_to_neo4j()
    if pg_conn and neo4j_driver:
        migrate_users(pg_conn, neo4j_driver)
        migrate_blogs(pg_conn, neo4j_driver)
        migrate_posts(pg_conn, neo4j_driver)
        migrate_comments(pg_conn, neo4j_driver)
        migrate_likes(pg_conn, neo4j_driver)
        migrate_follows(pg_conn, neo4j_driver)
        migrate_comment_replies(pg_conn, neo4j_driver)
        migrate_blog_ratings(pg_conn, neo4j_driver)
        migrate_tags(pg_conn, neo4j_driver)
        migrate_blog_tags(pg_conn, neo4j_driver)
        migrate_post_tags(pg_conn, neo4j_driver)
        pg_conn.close()
        neo4j_driver.close()

# Execute migration
migrate_data()
