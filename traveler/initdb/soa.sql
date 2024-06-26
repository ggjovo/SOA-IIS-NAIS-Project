-- Drop the existing tables if they exist
DROP TABLE IF EXISTS post_likes;
DROP TABLE IF EXISTS comment_likes;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS blogs;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS user_followings;
DROP TABLE IF EXISTS tours;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS checkpoints;
DROP TABLE IF EXISTS shoppingcart;
DROP TABLE IF EXISTS checkout;
DROP TABLE IF EXISTS PlatformReview;
DROP TABLE IF EXISTS ownedTours;
DROP TABLE IF EXISTS tourExecution;
DROP TABLE IF EXISTS tourExecutionCheckpoints;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS blog_ratings;
DROP TABLE IF EXISTS BlogTags;
DROP TABLE IF EXISTS PostTags;

-- Create a new table for users
CREATE TABLE users (
    ID SERIAL PRIMARY KEY,
    Username VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    Role VARCHAR(50) NOT NULL,
    Blocked BOOLEAN DEFAULT FALSE
);

-- Create a new table for blogs
CREATE TABLE blogs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create a new posts table with updated columns
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    blog_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    images JSONB DEFAULT '[]'::JSONB,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'closed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (blog_id) REFERENCES blogs(id)
);

-- Create a new comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER,
    parent_comment_id INTEGER,
    user_id INTEGER NOT NULL,
    comment_text TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create a new table for tracking likes on posts
CREATE TABLE post_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create a new table for tracking likes on comments
CREATE TABLE comment_likes (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES comments(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE user_followings (
    id SERIAL PRIMARY KEY,
    follower_id INT NOT NULL,
    following_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_follower FOREIGN KEY (follower_id) REFERENCES users(id),
    CONSTRAINT fk_following FOREIGN KEY (following_id) REFERENCES users(id),
    CONSTRAINT unique_follow UNIQUE (follower_id, following_id)
);

CREATE TABLE blog_ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    blog_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    UNIQUE (user_id, blog_id)
);

CREATE TABLE PlatformReview (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create a new table for tags
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    tag_name VARCHAR(255) NOT NULL
);

-- Create a new table for BlogTags
CREATE TABLE BlogTags (
    id SERIAL PRIMARY KEY,
    blog_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (blog_id) REFERENCES blogs(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- Create a new table for PostTags
CREATE TABLE PostTags (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

CREATE TABLE tours (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    duration VARCHAR(255) NOT NULL,
    difficulty VARCHAR(255) NOT NULL,
    price VARCHAR(255) NOT NULL,
    status VARCHAR(255) NOT NULL,
    guide_id INTEGER NOT NULL,
    FOREIGN KEY (guide_id) REFERENCES users(ID)
);

CREATE TABLE checkpoints (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    position INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    FOREIGN KEY (tour_id) REFERENCES tours(id)
);

CREATE TABLE shoppingcart (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    quantity INT,
    checkout_id INT DEFAULT 0,
    FOREIGN KEY (tour_id) REFERENCES tours(id)
);

CREATE TABLE checkout (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    total_price VARCHAR(255),
    checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ownedTours (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    tour_id INTEGER,
    quantity INTEGER,
    UNIQUE (user_id, tour_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (tour_id) REFERENCES tours(id)
);

CREATE TABLE tourExecution (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (tour_id) REFERENCES tours(id)
);

CREATE TABLE tourExecutionCheckpoints (
    id SERIAL PRIMARY KEY,
    tour_execution_id INTEGER NOT NULL,
    checkpoint_id INTEGER NOT NULL,
    reached_at TIMESTAMP,
    FOREIGN KEY (tour_execution_id) REFERENCES tourExecution(id),
    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id)
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER REFERENCES tours(id),
    user_id INTEGER REFERENCES users(id),
    review_text TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert users with roles
INSERT INTO users (Username, Password, Email, Role) VALUES ('admin', 'admin', 'admin@example.com', 'admin');
INSERT INTO users (Username, Password, Email, Role) VALUES ('guide1', 'password', 'guide1@example.com', 'guide');
INSERT INTO users (Username, Password, Email, Role) VALUES ('guide2', 'password', 'guide2@example.com', 'guide');
INSERT INTO users (Username, Password, Email, Role) VALUES ('tourist1', 'password', 'tourist1@example.com', 'tourist');
INSERT INTO users (Username, Password, Email, Role) VALUES ('tourist2', 'password', 'tourist2@example.com', 'tourist');
INSERT INTO users (Username, Password, Email, Role) VALUES ('tourist3', 'password', 'tourist3@example.com', 'tourist');
INSERT INTO users (Username, Password, Email, Role) VALUES ('tourist4', 'password', 'tourist4@example.com', 'tourist');
INSERT INTO users (Username, Password, Email, Role) VALUES ('tourist5', 'password', 'tourist5@example.com', 'tourist');
INSERT INTO users (Username, Password, Email, Role) VALUES ('tourist6', 'password', 'tourist6@example.com', 'tourist');
INSERT INTO users (Username, Password, Email, Role) VALUES ('tourist7', 'password', 'tourist7@example.com', 'tourist');

-- Insert blogs with posts for some users
INSERT INTO blogs (user_id, title, description) VALUES (1, 'First Blog by Admin', 'This is the first blog by Admin');
INSERT INTO blogs (user_id, title, description) VALUES (2, 'First Blog by Guide 1', 'This is the first blog by Guide 1');
INSERT INTO blogs (user_id, title, description) VALUES (3, 'First Blog by Guide 2', 'This is the first blog by Guide 2');
INSERT INTO blogs (user_id, title, description) VALUES (4, 'First Blog by Tourist 1', 'This is the first blog by Tourist 1');
INSERT INTO blogs (user_id, title, description) VALUES (5, 'First Blog by Tourist 2', 'This is the first blog by Tourist 2');

INSERT INTO posts (blog_id, title, description) VALUES (1, 'Post 1 by Admin', 'This is post 1 by Admin');
INSERT INTO posts (blog_id, title, description) VALUES (1, 'Post 2 by Admin', 'This is post 2 by Admin');
INSERT INTO posts (blog_id, title, description) VALUES (1, 'Post 3 by Admin', 'This is post 3 by Admin');
INSERT INTO posts (blog_id, title, description) VALUES (2, 'Post 1 by Guide 1', 'This is post 1 by Guide 1');
INSERT INTO posts (blog_id, title, description) VALUES (2, 'Post 2 by Guide 1', 'This is post 2 by Guide 1');
INSERT INTO posts (blog_id, title, description) VALUES (3, 'Post 1 by Guide 2', 'This is post 1 by Guide 2');
INSERT INTO posts (blog_id, title, description) VALUES (3, 'Post 2 by Guide 2', 'This is post 2 by Guide 2');
INSERT INTO posts (blog_id, title, description) VALUES (4, 'Post 1 by Tourist 1', 'This is post 1 by Tourist 1');
INSERT INTO posts (blog_id, title, description) VALUES (4, 'Post 2 by Tourist 1', 'This is post 2 by Tourist 1');
INSERT INTO posts (blog_id, title, description) VALUES (5, 'Post 1 by Tourist 2', 'This is post 1 by Tourist 2');
INSERT INTO posts (blog_id, title, description) VALUES (5, 'Post 2 by Tourist 2', 'This is post 2 by Tourist 2');

-- Insert comments on other users' blogs
INSERT INTO comments (post_id, user_id, comment_text) VALUES (1, 2, 'Comment by Guide 1 on Admin Post 1');
INSERT INTO comments (post_id, user_id, comment_text) VALUES (2, 3, 'Comment by Guide 2 on Admin Post 2');
INSERT INTO comments (post_id, user_id, comment_text) VALUES (3, 4, 'Comment by Tourist 1 on Admin Post 3');
INSERT INTO comments (post_id, user_id, comment_text) VALUES (4, 5, 'Comment by Tourist 2 on Guide 1 Post 1');
INSERT INTO comments (post_id, user_id, comment_text) VALUES (5, 6, 'Comment by Tourist 3 on Guide 1 Post 2');
INSERT INTO comments (post_id, user_id, comment_text) VALUES (6, 7, 'Comment by Tourist 4 on Guide 2 Post 1');
INSERT INTO comments (post_id, user_id, comment_text) VALUES (7, 8, 'Comment by Tourist 5 on Guide 2 Post 2');
INSERT INTO comments (post_id, user_id, comment_text) VALUES (8, 9, 'Comment by Tourist 6 on Tourist 1 Post 1');
INSERT INTO comments (post_id, user_id, comment_text) VALUES (9, 10, 'Comment by Tourist 7 on Tourist 1 Post 2');
INSERT INTO comments (post_id, user_id, comment_text) VALUES (10, 1, 'Comment by Admin on Tourist 2 Post 1');

-- Insert replies to comments
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES (1, 1, 3, 'Reply by Guide 2 to Comment 1');
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES (2, 2, 4, 'Reply by Tourist 1 to Comment 2');
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES (3, 3, 5, 'Reply by Tourist 2 to Comment 3');
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES (4, 4, 6, 'Reply by Tourist 3 to Comment 4');
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES (5, 5, 7, 'Reply by Tourist 4 to Comment 5');
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES (6, 6, 8, 'Reply by Tourist 5 to Comment 6');
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES (7, 7, 9, 'Reply by Tourist 6 to Comment 7');
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES (8, 8, 10, 'Reply by Tourist 7 to Comment 8');
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES (9, 9, 1, 'Reply by Admin to Comment 9');
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES (10, 10, 2, 'Reply by Guide 1 to Comment 10');

-- Insert likes on posts
INSERT INTO post_likes (post_id, user_id) VALUES (1, 2);
INSERT INTO post_likes (post_id, user_id) VALUES (2, 3);
INSERT INTO post_likes (post_id, user_id) VALUES (3, 4);
INSERT INTO post_likes (post_id, user_id) VALUES (4, 5);
INSERT INTO post_likes (post_id, user_id) VALUES (5, 6);
INSERT INTO post_likes (post_id, user_id) VALUES (6, 7);
INSERT INTO post_likes (post_id, user_id) VALUES (7, 8);
INSERT INTO post_likes (post_id, user_id) VALUES (8, 9);
INSERT INTO post_likes (post_id, user_id) VALUES (9, 10);
INSERT INTO post_likes (post_id, user_id) VALUES (10, 1);

-- Insert likes on comments
INSERT INTO comment_likes (comment_id, user_id) VALUES (1, 2);
INSERT INTO comment_likes (comment_id, user_id) VALUES (2, 3);
INSERT INTO comment_likes (comment_id, user_id) VALUES (3, 4);
INSERT INTO comment_likes (comment_id, user_id) VALUES (4, 5);
INSERT INTO comment_likes (comment_id, user_id) VALUES (5, 6);
INSERT INTO comment_likes (comment_id, user_id) VALUES (6, 7);
INSERT INTO comment_likes (comment_id, user_id) VALUES (7, 8);
INSERT INTO comment_likes (comment_id, user_id) VALUES (8, 9);
INSERT INTO comment_likes (comment_id, user_id) VALUES (9, 10);
INSERT INTO comment_likes (comment_id, user_id) VALUES (10, 1);

-- Insert example data into PlatformReview table
INSERT INTO PlatformReview (user_id, rating, comment) VALUES 
(1, 5, 'Great app!'),
(2, 4, 'Very useful, but needs some improvements.'),
(3, 5, 'Excellent!'),
(4, 4, 'Pretty good!'),
(5, 3, 'Not bad.'),
(6, 5, 'Love it!'),
(7, 4, 'Very handy.'),
(8, 3, 'Could be better.'),
(9, 5, 'Awesome!'),
(10, 4, 'Really useful.');

-- Insert blog ratings
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (1, 2, 5);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (1, 3, 4);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (2, 1, 4);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (2, 3, 5);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (3, 1, 3);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (3, 2, 5);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (4, 1, 4);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (4, 2, 5);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (5, 1, 5);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (5, 2, 4);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (6, 1, 5);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (6, 2, 3);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (7, 1, 5);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (7, 2, 4);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (8, 1, 5);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (8, 2, 4);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (9, 1, 5);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (9, 2, 3);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (10, 1, 5);
INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (10, 2, 4);

-- Insert user followings after all users are inserted
INSERT INTO user_followings (follower_id, following_id) VALUES (1, 2);
INSERT INTO user_followings (follower_id, following_id) VALUES (2, 1);
INSERT INTO user_followings (follower_id, following_id) VALUES (3, 4);
INSERT INTO user_followings (follower_id, following_id) VALUES (4, 5);
INSERT INTO user_followings (follower_id, following_id) VALUES (5, 6);
INSERT INTO user_followings (follower_id, following_id) VALUES (6, 7);
INSERT INTO user_followings (follower_id, following_id) VALUES (7, 8);
INSERT INTO user_followings (follower_id, following_id) VALUES (8, 9);
INSERT INTO user_followings (follower_id, following_id) VALUES (9, 10);

-- Insert tags related to touristic topics
INSERT INTO tags (tag_name) VALUES ('Culture');
INSERT INTO tags (tag_name) VALUES ('Adventure');
INSERT INTO tags (tag_name) VALUES ('Nature');
INSERT INTO tags (tag_name) VALUES ('History');
INSERT INTO tags (tag_name) VALUES ('Food');
INSERT INTO tags (tag_name) VALUES ('Entertainment');
INSERT INTO tags (tag_name) VALUES ('Shopping');
INSERT INTO tags (tag_name) VALUES ('Accommodation');
INSERT INTO tags (tag_name) VALUES ('Transportation');
INSERT INTO tags (tag_name) VALUES ('Nightlife');
INSERT INTO tags (tag_name) VALUES ('Tech');
INSERT INTO tags (tag_name) VALUES ('Fitness');

-- Connect each blog with 1 to 5 tags
INSERT INTO BlogTags (blog_id, tag_id) VALUES (1, 1);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (1, 2);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (1, 3);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (2, 2);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (2, 4);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (3, 3);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (3, 5);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (4, 4);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (4, 6);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (4, 7);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (5, 8);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (5, 9);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (5, 10);

-- Connect each post with 0 to 3 tags
INSERT INTO PostTags (post_id, tag_id) VALUES (1, 1);
INSERT INTO PostTags (post_id, tag_id) VALUES (1, 2);
INSERT INTO PostTags (post_id, tag_id) VALUES (2, 3);
INSERT INTO PostTags (post_id, tag_id) VALUES (3, 4);
INSERT INTO PostTags (post_id, tag_id) VALUES (4, 5);
INSERT INTO PostTags (post_id, tag_id) VALUES (4, 6);
INSERT INTO PostTags (post_id, tag_id) VALUES (5, 7);
INSERT INTO PostTags (post_id, tag_id) VALUES (6, 8);
INSERT INTO PostTags (post_id, tag_id) VALUES (7, 9);
INSERT INTO PostTags (post_id, tag_id) VALUES (7, 10);
INSERT INTO PostTags (post_id, tag_id) VALUES (8, 1);
INSERT INTO PostTags (post_id, tag_id) VALUES (9, 2);
INSERT INTO PostTags (post_id, tag_id) VALUES (10, 3);


-- Insert users
INSERT INTO users (Username, Password, Email, Role) VALUES
('alice', 'password1', 'alice@example.com', 'tourist'),
('bob', 'password2', 'bob@example.com', 'tourist'),
('charlie', 'password3', 'charlie@example.com', 'tourist'),
('dave', 'password4', 'dave@example.com', 'tourist'),
('eve', 'password5', 'eve@example.com', 'tourist'),
('frank', 'password6', 'frank@example.com', 'tourist'),
('grace', 'password7', 'grace@example.com', 'tourist'),
('heidi', 'password8', 'heidi@example.com', 'tourist'),
('ivan', 'password9', 'ivan@example.com', 'tourist');

-- Insert blogs
INSERT INTO blogs (user_id, title, description) VALUES
(11, 'Alice Adventures in Blogging', 'Exploring the world of blogs with Alice.'),
(12, 'Bobs Tech Talk', 'Bob shares his insights on the latest in technology.'),
(13, 'Charlies Culinary Corner', 'Delicious recipes and cooking tips from Charlie.'),
(14, 'Daves Travel Diaries', 'Join Dave as he travels the world.'),
(15, 'Eves Fashion Finds', 'Stay stylish with Eves fashion tips.'),
(16, 'Franks Fitness Blog', 'Get fit with Franks workout routines.'),
(17, 'Graces Garden', 'Gardening tips and tricks from Grace.'),
(18, 'Heidis Book Nook', 'Book reviews and recommendations by Heidi.'),
(19, 'Ivans Investment Insights', 'Ivan shares his knowledge on investing.');

-- Connect each blog with tags
INSERT INTO BlogTags (blog_id, tag_id) VALUES (6, 1);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (6, 2);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (6, 3);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (6, 5);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (6, 6);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (6, 7);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (6, 8);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (6, 9);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (6, 10);

INSERT INTO BlogTags (blog_id, tag_id) VALUES (7, 11);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (7, 6);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (7, 7);

INSERT INTO BlogTags (blog_id, tag_id) VALUES (8, 1);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (8, 2);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (8, 4);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (8, 5);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (8, 6);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (8, 7);

INSERT INTO BlogTags (blog_id, tag_id) VALUES (9, 2);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (9, 3);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (9, 5);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (9, 6);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (9, 10);

INSERT INTO BlogTags (blog_id, tag_id) VALUES (10, 6);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (10, 7);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (10, 10);

INSERT INTO BlogTags (blog_id, tag_id) VALUES (11, 5);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (11, 12);

INSERT INTO BlogTags (blog_id, tag_id) VALUES (12, 5);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (12, 3);

INSERT INTO BlogTags (blog_id, tag_id) VALUES (13, 1);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (13, 4);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (13, 6);

INSERT INTO BlogTags (blog_id, tag_id) VALUES (14, 5);
INSERT INTO BlogTags (blog_id, tag_id) VALUES (14, 12);

-- Posts

-- Blog 1: Alice Adventures in Blogging
INSERT INTO posts (blog_id, title, description) VALUES
(6, 'Exploring Local Parks', 'A review of some beautiful parks in the city.'),
(6, 'A Day in the Life', 'A glimpse into my daily routine.'),
(6, 'Photography Tips', 'How to take stunning photos for your blog.'),
(6, 'Favorite Coffee Shops', 'My top picks for coffee shops.'),
(6, 'DIY Projects', 'Simple DIY projects to try at home.'),
(6, 'Book Review: Blog Like a Pro', 'My thoughts on this blogging guide.'),
(6, 'Interview with a Fellow Blogger', 'An inspiring conversation with another blogger.'),
(6, 'Travel Essentials', 'Must-have items for every trip.'),
(6, 'Healthy Living Tips', 'How to maintain a healthy lifestyle while blogging.'),
(6, 'Weekend Getaway Ideas', 'Perfect spots for a quick escape.'),
(6, 'Social Media Strategies', 'Tips to grow your blog’s social media presence.'),
(6, 'Blogging on a Budget', 'How to blog without breaking the bank.'),
(6, 'Guest Post: Blogging Myths', 'Debunking common blogging myths.'),
(6, 'Holiday Gift Guide', 'Great gifts for bloggers.'),
(6, 'Year in Review', 'Reflecting on the past year of blogging.');

-- Blog 2: Bob's Tech Talk
INSERT INTO posts (blog_id, title, description) VALUES
(7, 'Latest Smartphone Review', 'A detailed review of the newest smartphone.'),
(7, 'Top 5 Programming Languages', 'Which programming languages you should learn.'),
(7, 'Building a Custom PC', 'Step-by-step guide to building your own PC.'),
(7, 'Tech Trends 2024', 'Predictions for the upcoming tech trends.'),
(7, 'AI in Everyday Life', 'How AI is changing the way we live.'),
(7, 'Best Laptops for Developers', 'Top picks for developer-friendly laptops.'),
(7, 'Interview with a Software Engineer', 'Insights from a professional in the field.'),
(7, 'Cybersecurity Tips', 'How to protect yourself online.'),
(7, 'Open Source vs. Proprietary Software', 'The pros and cons of each.'),
(7, 'Gadgets for Gamers', 'Must-have gadgets for gaming enthusiasts.'),
(7, 'Future of Quantum Computing', 'What to expect from quantum computing.'),
(7, 'Review: Smart Home Devices', 'Making your home smarter with these devices.'),
(7, 'How to Start Coding', 'Beginner’s guide to coding.'),
(7, 'Tech Conferences to Attend', 'Top tech conferences you shouldn’t miss.'),
(7, 'Year in Tech', 'A look back at the biggest tech developments.');

-- Blog 3: Charlie's Culinary Corner
INSERT INTO posts (blog_id, title, description) VALUES
(8, 'Easy Weeknight Dinners', 'Quick and delicious meals for busy evenings.'),
(8, 'Baking Bread at Home', 'A step-by-step guide to baking bread.'),
(8, 'Vegan Recipes to Try', 'Delicious and healthy vegan recipes.'),
(8, 'Cooking with Kids', 'Fun and easy recipes for cooking with children.'),
(8, 'Holiday Baking', 'Festive treats for the holiday season.'),
(8, 'Global Cuisine', 'Exploring dishes from around the world.'),
(8, 'Healthy Snacks', 'Nutritious and tasty snack ideas.'),
(8, 'Meal Prep Tips', 'How to efficiently prepare meals for the week.'),
(8, 'Farmers Market Finds', 'Best ingredients to buy at your local market.'),
(8, 'Hosting a Dinner Party', 'Tips for a successful dinner party.'),
(8, 'Cooking on a Budget', 'Delicious meals that won’t break the bank.'),
(8, 'Essential Kitchen Tools', 'Must-have tools for every home cook.'),
(8, 'Interview with a Chef', 'Insights from a professional chef.'),
(8, 'Decadent Desserts', 'Indulgent dessert recipes to try.'),
(8, 'Cooking for Two', 'Perfect recipes for couples.');

-- Blog 4: Dave's Travel Diaries
INSERT INTO posts (blog_id, title, description) VALUES
(9, 'Top Travel Destinations 2024', 'Must-visit places for the new year.'),
(9, 'Traveling on a Budget', 'How to see the world without spending a fortune.'),
(9, 'Solo Travel Tips', 'Advice for traveling alone safely and enjoyably.'),
(9, 'Best Beaches', 'A guide to the world’s most beautiful beaches.'),
(9, 'Cultural Experiences', 'Immersive cultural activities to try.'),
(9, 'Travel Photography', 'How to take amazing travel photos.'),
(9, 'Packing Essentials', 'What to pack for any trip.'),
(9, 'Traveling with Pets', 'Tips for bringing your furry friend along.'),
(9, 'Adventure Travel', 'Thrilling destinations for adventure seekers.'),
(9, 'Eco-Friendly Travel', 'How to travel sustainably.'),
(9, 'Luxury Travel', 'Indulgent experiences for luxury travelers.'),
(9, 'Road Trip Tips', 'Planning the perfect road trip.'),
(9, 'Travel Scams to Avoid', 'How to stay safe and avoid scams while traveling.'),
(9, 'Traveling with Kids', 'How to make family travel fun and stress-free.'),
(9, 'Hidden Gems', 'Lesser-known travel destinations worth visiting.');

-- Blog 5: Eve's Fashion Finds
INSERT INTO posts (blog_id, title, description) VALUES
(10, 'Summer Fashion Trends', 'What to wear this summer.'),
(10, 'Wardrobe Essentials', 'Must-have items for every closet.'),
(10, 'Styling Tips', 'How to style different outfits.'),
(10, 'Thrift Shopping', 'Finding great fashion deals at thrift stores.'),
(10, 'Fashion on a Budget', 'Looking stylish without spending a lot.'),
(10, 'Seasonal Outfits', 'Perfect outfits for every season.'),
(10, 'Accessorizing Your Look', 'How to accessorize like a pro.'),
(10, 'Sustainable Fashion', 'Eco-friendly fashion choices.'),
(10, 'Interview with a Designer', 'Insights from a fashion designer.'),
(10, 'Fashion Week Highlights', 'The best of fashion week.'),
(10, 'DIY Fashion Projects', 'Create your own fashion pieces.'),
(10, 'Dressing for Work', 'Professional yet stylish work attire.'),
(10, 'Evening Wear', 'Choosing the perfect outfit for a night out.'),
(10, 'Shoes to Love', 'A guide to the best shoes for any outfit.'),
(10, 'Fashion Icons', 'Inspiration from fashion icons.');

-- Blog 6: Frank's Fitness Blog
INSERT INTO posts (blog_id, title, description) VALUES
(11, 'Home Workout Routines', 'Effective workouts you can do at home.'),
(11, 'Building Muscle', 'Tips for gaining muscle mass.'),
(11, 'Healthy Eating', 'How to eat healthy for fitness success.'),
(11, 'Yoga for Beginners', 'Starting your yoga journey.'),
(11, 'Cardio Workouts', 'The best cardio exercises.'),
(11, 'Interview with a Personal Trainer', 'Fitness advice from a professional.'),
(11, 'Staying Motivated', 'How to keep up with your fitness goals.'),
(11, 'Gym Etiquette', 'Proper behavior in the gym.'),
(11, 'Fitness Myths Debunked', 'Common fitness myths and the truth behind them.'),
(11, 'Stretching Exercises', 'Important stretches for flexibility.'),
(11, 'Weight Loss Tips', 'Effective strategies for losing weight.'),
(11, 'Sports Nutrition', 'What to eat for peak performance.'),
(11, 'Workout Gear', 'Choosing the right gear for your workouts.'),
(11, 'Recovery and Rest', 'The importance of rest in your fitness routine.'),
(11, 'Training for a Marathon', 'How to prepare for a marathon.');

-- Blog 7: Grace's Garden
INSERT INTO posts (blog_id, title, description) VALUES
(12, 'Starting a Garden', 'How to begin your gardening journey.'),
(12, 'Best Plants for Beginners', 'Easy-to-grow plants for new gardeners.'),
(12, 'Seasonal Gardening Tips', 'What to do in your garden each season.'),
(12, 'Organic Gardening', 'Growing plants without chemicals.'),
(12, 'Indoor Plants', 'How to care for plants inside your home.'),
(12, 'Composting 101', 'The basics of composting.'),
(12, 'Garden Design Ideas', 'Inspiration for your garden layout.'),
(12, 'Pest Control', 'Natural ways to deal with garden pests.'),
(12, 'Herb Garden', 'Growing your own herbs.'),
(12, 'Flower Arrangements', 'Creating beautiful flower arrangements.'),
(12, 'Vegetable Gardening', 'Tips for growing your own vegetables.'),
(12, 'Watering Tips', 'How to properly water your plants.'),
(12, 'Interview with a Botanist', 'Expert advice on gardening.'),
(12, 'Pruning Techniques', 'How to prune plants for better growth.'),
(12, 'Garden Tools', 'Essential tools for every gardener.');

-- Blog 8: Heidi's Book Nook
INSERT INTO posts (blog_id, title, description) VALUES
(13, 'Best Books of 2024', 'Top picks for the year.'),
(13, 'Reading Tips', 'How to read more books.'),
(13, 'Book Club Guide', 'Starting and running a successful book club.'),
(13, 'Interview with an Author', 'Insights from a published author.'),
(13, 'Classic Literature', 'Why you should read the classics.'),
(13, 'Fantasy Novels', 'Top fantasy books to get lost in.'),
(13, 'Non-Fiction Gems', 'Must-read non-fiction books.'),
(13, 'Young Adult Favorites', 'Best young adult novels.'),
(13, 'Historical Fiction', 'Top historical fiction books.'),
(13, 'Mystery and Thrillers', 'Edge-of-your-seat reads.'),
(13, 'Romance Novels', 'Heartwarming romance books.'),
(13, 'Sci-Fi Adventures', 'Exploring the best sci-fi books.'),
(13, 'Children’s Books', 'Great books for kids.'),
(13, 'Book Reviews', 'In-depth reviews of popular books.'),
(13, 'Author Spotlights', 'Profiles of amazing authors.');

-- Blog 9: Ivan's Investment Insights
INSERT INTO posts (blog_id, title, description) VALUES
(14, 'Investment Basics', 'Getting started with investing.'),
(14, 'Stock Market Tips', 'How to navigate the stock market.'),
(14, 'Real Estate Investing', 'Tips for investing in real estate.'),
(14, 'Interview with a Financial Advisor', 'Expert financial advice.'),
(14, 'Retirement Planning', 'How to plan for a comfortable retirement.'),
(14, 'Cryptocurrency', 'Understanding and investing in cryptocurrencies.'),
(14, 'Diversifying Your Portfolio', 'Why and how to diversify your investments.'),
(14, 'Risk Management', 'How to manage investment risks.'),
(14, 'Long-Term vs. Short-Term Investments', 'Pros and cons of each strategy.'),
(14, 'Investment Mistakes to Avoid', 'Common mistakes and how to avoid them.'),
(14, 'Analyzing Stocks', 'How to evaluate stocks before investing.'),
(14, 'Passive Income', 'Ways to generate passive income.'),
(14, 'Economic Indicators', 'How economic indicators affect investments.'),
(14, 'Tax Strategies', 'Tax-efficient investment strategies.'),
(14, 'Year in Review: Investments', 'A look back at the year’s investment trends.');

-- Insert additional users who will act as commentators
INSERT INTO users (Username, Password, Email, Role) VALUES
('jake', 'password10', 'jake@example.com', 'tourist'),
('lily', 'password11', 'lily@example.com', 'tourist'),
('mike', 'password12', 'mike@example.com', 'tourist'),
('nina', 'password13', 'nina@example.com', 'tourist'),
('oliver', 'password14', 'oliver@example.com', 'tourist'),
('paula', 'password15', 'paula@example.com', 'tourist'),
('john123', 'password16', 'john123@example.com', 'tourist'),
('johnn1234', 'password17', 'john1234@example.com', 'tourist'),
('zoi123', 'password18', 'zoi123@example.com', 'tourist'),
('temp1', 'password19', 'temp1@example.com', 'tourist'),
('temp2', 'password20', 'temp2@example.com', 'tourist'),
('temp3', 'password21', 'temp3@example.com', 'tourist'),
('temp4', 'password22', 'temp4@example.com', 'tourist'),
('temp5', 'password23', 'temp5@example.com', 'tourist'),
('temp6', 'password24', 'temp6@example.com', 'tourist'),
('temp7', 'password25', 'temp7@example.com', 'tourist'),
('temp8', 'password26', 'temp8@example.com', 'tourist'),
('temp9', 'password27', 'temp9@example.com', 'tourist'),
('temp10', 'password28', 'temp10@example.com', 'tourist'),
('temp11', 'password29', 'temp11@example.com', 'tourist'),
('temp12', 'password30', 'temp12@example.com', 'tourist'),
('temp13', 'password31', 'temp13@example.com', 'tourist');

-- Post tags 
DO $$
DECLARE
    post_id INT;
BEGIN
    -- Post IDs 12-26 with tag IDs (1,2,3,5,6,7,8,9,10)
    FOR post_id IN 12..26 LOOP
        INSERT INTO PostTags (post_id, tag_id)
        VALUES (post_id, 1), (post_id, 2), (post_id, 3), 
               (post_id, 5), (post_id, 6), (post_id, 7), 
               (post_id, 8), (post_id, 9), (post_id, 10);
    END LOOP;

    -- Post IDs 27-41 with tag IDs (6,7,11)
    FOR post_id IN 27..41 LOOP
        INSERT INTO PostTags (post_id, tag_id)
        VALUES (post_id, 6), (post_id, 7), (post_id, 11);
    END LOOP;

    -- Post IDs 42-56 with tag IDs (1,2,3,4,5,6,7)
    FOR post_id IN 42..56 LOOP
        INSERT INTO PostTags (post_id, tag_id)
        VALUES (post_id, 1), (post_id, 2), (post_id, 3), 
               (post_id, 4), (post_id, 5), (post_id, 6), 
               (post_id, 7);
    END LOOP;

    -- Post IDs 57-71 with tag IDs (2,3,5,6,10)
    FOR post_id IN 57..71 LOOP
        INSERT INTO PostTags (post_id, tag_id)
        VALUES (post_id, 2), (post_id, 3), (post_id, 5), 
               (post_id, 6), (post_id, 10);
    END LOOP;

    -- Post IDs 72-86 with tag IDs (6,7,10)
    FOR post_id IN 72..86 LOOP
        INSERT INTO PostTags (post_id, tag_id)
        VALUES (post_id, 6), (post_id, 7), (post_id, 10);
    END LOOP;

    -- Post IDs 87-101 with tag IDs (5,12)
    FOR post_id IN 87..101 LOOP
        INSERT INTO PostTags (post_id, tag_id)
        VALUES (post_id, 5), (post_id, 12);
    END LOOP;

    -- Post IDs 102-116 with tag IDs (5,3)
    FOR post_id IN 102..116 LOOP
        INSERT INTO PostTags (post_id, tag_id)
        VALUES (post_id, 5), (post_id, 3);
    END LOOP;

    -- Post IDs 117-131 with tag IDs (1,4,6)
    FOR post_id IN 117..131 LOOP
        INSERT INTO PostTags (post_id, tag_id)
        VALUES (post_id, 1), (post_id, 4), (post_id, 6);
    END LOOP;

    -- Post IDs 132-146 with tag IDs (5,12)
    FOR post_id IN 132..146 LOOP
        INSERT INTO PostTags (post_id, tag_id)
        VALUES (post_id, 5), (post_id, 12);
    END LOOP;
END $$;

-- Comments 

-- Insert comments for the first blog
INSERT INTO comments (post_id, user_id, comment_text) VALUES
(12, 20, 'Great Parks Info'),
(13, 20, 'You da best'),
(14, 20, 'Check out the waffle place nearby'),
(15, 20, 'Love this travel tip!'),
(16, 20, 'Can’t wait to try this recipe'),
(17, 20, 'Amazing workout routine!'),
(18, 20, 'Helpful gardening tips'),
(19, 20, 'I need to read this book'),
(20, 20, 'Very informative article on investing'),
(21, 20, 'Fantastic tech review!'),
(22, 20, 'This makeup tutorial is awesome!'),
(23, 20, 'Great advice on fashion!'),
(24, 20, 'These fitness tips are very useful'),
(25, 20, 'I learned a lot from this gardening post'),
(26, 20, 'Wonderful book recommendations!');

INSERT INTO comments (post_id, user_id, comment_text) VALUES
(12, 21, 'Great Parks Info'),
(13, 21, 'You da best'),
(17, 21, 'Amazing workout routine!'),
(25, 21, 'I learned a lot from this gardening post'),
(26, 21, 'Great!');

INSERT INTO comments (post_id, user_id, comment_text) VALUES
(15, 22, 'Great Parks Info'),
(15, 22, 'You da best'),
(15, 22, 'Amazing workout routine!'),
(17, 22, 'I learned a lot from this gardening post'),
(15, 22, 'Great Parks Info'),
(15, 22, 'You da best'),
(15, 22, 'Amazing workout routine!'),
(25, 22, 'I learned a lot from this gardening post'),
(15, 22, 'Great Parks Info'),
(15, 22, 'You da best'),
(15, 22, 'Amazing workout routine!'),
(18, 22, 'I learned a lot from this gardening post'),
(20, 22, 'Great!');

INSERT INTO comments (post_id, user_id, comment_text) VALUES
(24, 23, 'Great Parks Info'),
(14, 23, 'You da best'),
(25, 23, 'Amazing workout routine!'),
(26, 23, 'I learned a lot from this gardening post');

INSERT INTO comments (post_id, user_id, comment_text) VALUES
(15, 24, 'Great Parks Info'),
(12, 24, 'You da best');

INSERT INTO comments (post_id, user_id, comment_text) VALUES
(26, 25, 'Great Parks Info'),
(19, 25, 'You da best');

-- Comment inside comment argument
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES 
(16, 25, 22, 'Stupid comment'),
(16, 62, 21, 'Does your doors dont have locks?'),
(16, 63, 22, 'Does youre english havent good?'),
(16, 64, 21, 'You speak english because its the only language you know. I speak english because its the only language you know. We are not the same'),
(16, 65, 23, 'WOOO'),
(16, 65, 24, 'DAMNN'),
(16, 65, 25, 'GOOGLE TRANSLATE COOKED'),
(16, 65, 26, 'BRO CHILL');

INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES 
(16, 25, 27, 'Stupid comment'),
(16, 70, 28, 'Does your doors dont have locks?'),
(16, 71, 27, 'Does youre english havent good?'),
(16, 72, 28, 'You speak english because its the only language you know. I speak english because its the only language you know. We are not the same'),
(16, 73, 29, 'WOOO'),
(16, 73, 29, 'DAMNN'),
(16, 72, 29, 'GOOGLE TRANSLATE COOKED'),
(16, 72, 29, 'BRO CHILL');


-- comments for blog12

INSERT INTO comments (post_id, user_id, comment_text) VALUES
(27, 28, 'Great Parks Info'),
(28, 29, 'You da best'),
(29, 29, 'Check out the waffle place nearby'),
(30, 29, 'Love this travel tip!'),
(31, 29, 'Can’t wait to try this recipe'),
(32, 29, 'Amazing workout routine!'),
(33, 29, 'Helpful gardening tips'),
(34, 29, 'I need to read this book'),
(35, 29, 'Very informative article on investing'),
(36, 29, 'Fantastic tech review!'),
(37, 29, 'This makeup tutorial is awesome!'),
(38, 29, 'Great advice on fashion!'),
(39, 29, 'These fitness tips are very useful'),
(40, 29, 'I learned a lot from this gardening post'),
(41, 29, 'Wonderful book recommendations!');


INSERT INTO comments (post_id, user_id, comment_text) VALUES
(27, 21, 'This article is very helpful!'),
(28, 22, 'I love the insights shared here.'),
(29, 23, 'Great read, thanks for sharing!'),
(30, 24, 'This post helped me a lot.'),
(31, 25, 'Fantastic write-up!'),
(32, 26, 'Very well explained.'),
(33, 27, 'I learned something new today.'),
(34, 28, 'This is very informative.'),
(35, 29, 'Thanks for the tips!'),
(36, 30, 'Excellent post.'),
(37, 31, 'I appreciate the detailed explanation.'),
(38, 20, 'This is quite insightful.'),
(39, 21, 'A very well-written article.'),
(40, 22, 'I found this very useful.'),
(41, 23, 'Great advice!'),
(42, 24, 'Thank you for sharing this.'),
(43, 25, 'Very enlightening post.'),
(44, 26, 'I will definitely apply this.'),
(45, 27, 'This article is spot on!'),
(46, 28, 'Great tips, very helpful.'),
(47, 29, 'I agree with this post.'),
(48, 30, 'This is a must-read.'),
(49, 31, 'A very interesting read.'),
(50, 20, 'Thanks for the information.');

-- Level 2 replies to root comments above
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES
(27, 93, 22, 'I completely agree!'),
(27, 93, 23, 'Thanks for sharing this.'),
(27, 93, 24, 'This was helpful.'),
(27, 93, 25, 'I learned a lot from this post.'),
(27, 93, 26, 'Very informative!'),

(27, 117, 23, 'Yes, very insightful.'),
(27, 117, 24, 'I love this too!'),
(27, 117, 25, 'Thanks for the info.'),
(27, 117, 26, 'Great article!'),

(27, 122, 24, 'Glad you found it useful!'),
(27, 122, 25, 'This is awesome.'),
(27, 122, 26, 'Thanks for sharing.'),
(27, 122, 27, 'I agree with your points.');

INSERT INTO comments (post_id, user_id, comment_text) VALUES
(28, 30, 'random comment 7'),
(28, 30, 'great!'),
(28, 31, 'i mean its ok!'),
(29, 31, 'damn it!'),
(29, 32, 'anoying'),
(29, 33, '123'),
(29, 34, 'random comment 1'),
(31, 31, 'random comment 2'),
(31, 32, 'random comment 3'),
(31, 33, 'random comment 4'),
(31, 34, 'random comment 5'),
(31, 35, 'random comment 6'),
(32, 21, 'random comment 8'),
(32, 19, 'random comment 9'),
(33, 11, 'random comment 10'),
(34, 12, 'random comment 11'),
(33, 31, 'random comment 12'),
(35, 32, 'random comment 13'),
(35, 30, 'random comment 14'),
(35, 11, 'random comment 15'),
(35, 12, 'random comment 16'),
(36, 19, 'a really long comment to test the look in neo4j just for fun xd max bodovi mejbi ??? mozda ne idk jova ker 123'),
(37, 13, 'jovoker123'),
(38, 13, 'Cybersecurityradovan'),
(39, 18, 'komentar123'),
(40, 33, 'random comment 17'),
(40, 32, 'random comment 18'),
(40, 30, 'random comment 19'),
(40, 30, 'random comment 20'),
(40, 31, 'random comment 21'),
(41, 25, 'random comment 22'),
(42, 24, 'random comment 23'),
(44, 29, 'random comment 24'),
(45, 29, 'random comment 25'),
(45, 31, 'random comment 26'),
(45, 16, 'random comment 27'),
(45, 17, 'random comment 28'),
(45, 18, 'random comment 29'),
(46, 23, 'random comment 30'),
(47, 27, 'random comment 31');

-- Comments for post IDs 12-26, 27-41, 42-56, 72-86 by users (28-34) (repeated) and across blog IDs 6, 7, 8, 10

-- Blog ID 6 (post IDs 12-26)
INSERT INTO comments (post_id, user_id, comment_text) VALUES
(12, 28, 'Interesting insights on blog 6 post 12.'),
(13, 29, 'Great post on blog 6 post 13.'),
(14, 30, 'Well articulated on blog 6 post 14.'),
(15, 31, 'I agree with this on blog 6 post 15.'),
(16, 32, 'Thought-provoking on blog 6 post 16.'),
(17, 33, 'Deep analysis on blog 6 post 17.'),
(18, 34, 'Impressive work on blog 6 post 18.'),
(19, 28, 'Really liked the content on blog 6 post 19.'),
(20, 29, 'Interesting perspective on blog 6 post 20.'),
(21, 30, 'Enjoyed reading this on blog 6 post 21.'),
(22, 31, 'Good points made on blog 6 post 22.'),
(23, 32, 'Insightful commentary on blog 6 post 23.'),
(24, 33, 'Well-explained on blog 6 post 24.'),
(25, 34, 'Solid content on blog 6 post 25.');

-- Blog ID 7 (post IDs 27-41)
INSERT INTO comments (post_id, user_id, comment_text) VALUES
(27, 28, 'Engaging topic on blog 7 post 27.'),
(28, 29, 'Interesting insights on blog 7 post 28.'),
(29, 30, 'Good points made on blog 7 post 29.'),
(30, 31, 'Well-explained on blog 7 post 30.'),
(31, 32, 'Detailed analysis on blog 7 post 31.'),
(32, 33, 'I learned something new on blog 7 post 32.'),
(33, 34, 'Thoughtful insights on blog 7 post 33.'),
(34, 28, 'Well-presented on blog 7 post 34.'),
(35, 29, 'Thought-provoking on blog 7 post 35.'),
(36, 30, 'Detailed commentary on blog 7 post 36.'),
(37, 31, 'Solid argument on blog 7 post 37.'),
(38, 32, 'Impressive insights on blog 7 post 38.'),
(39, 33, 'Deep thoughts on blog 7 post 39.'),
(40, 34, 'Enjoyed reading this on blog 7 post 40.');

-- Blog ID 8 (post IDs 42-56)
INSERT INTO comments (post_id, user_id, comment_text) VALUES
(42, 28, 'Well said on blog 8 post 42.'),
(43, 29, 'Great thoughts on blog 8 post 43.'),
(44, 30, 'I appreciate this on blog 8 post 44.'),
(45, 31, 'Well done on blog 8 post 45.'),
(46, 32, 'Solid content on blog 8 post 46.'),
(47, 33, 'Impressive work on blog 8 post 47.'),
(48, 34, 'Engaging topic on blog 8 post 48.'),
(49, 28, 'Detailed analysis on blog 8 post 49.'),
(50, 29, 'Thought-provoking on blog 8 post 50.'),
(51, 30, 'Deep insights on blog 8 post 51.'),
(52, 31, 'Well-explained on blog 8 post 52.'),
(53, 32, 'Interesting read on blog 8 post 53.'),
(54, 33, 'Detailed commentary on blog 8 post 54.'),
(55, 34, 'Impressive insights on blog 8 post 55.');

-- Blog ID 10 (post IDs 72-86)
INSERT INTO comments (post_id, user_id, comment_text) VALUES
(72, 28, 'Enjoyed reading this on blog 10 post 72.'),
(73, 29, 'Good points made on blog 10 post 73.'),
(74, 30, 'Interesting read on blog 10 post 74.'),
(75, 31, 'Insightful commentary on blog 10 post 75.'),
(76, 32, 'I learned something new on blog 10 post 76.'),
(77, 33, 'Provocative discussion on blog 10 post 77.'),
(78, 34, 'Well-presented on blog 10 post 78.'),
(79, 28, 'Engaging topic on blog 10 post 79.'),
(80, 29, 'Thought-provoking on blog 10 post 80.'),
(81, 30, 'Detailed commentary on blog 10 post 81.'),
(82, 31, 'Solid argument on blog 10 post 82.'),
(83, 32, 'Impressive insights on blog 10 post 83.'),
(84, 33, 'Deep thoughts on blog 10 post 84.'),
(85, 34, 'Thoughtful insights on blog 10 post 85.');

-- Comments for post IDs 87-101 and 132-146 by users 35-37

-- Blog ID 16 (post IDs 87-101)
INSERT INTO comments (post_id, user_id, comment_text) VALUES
(87, 35, 'Interesting insights on blog 16 post 87.'),
(88, 36, 'Great post on blog 16 post 88.'),
(89, 37, 'Well articulated on blog 16 post 89.'),
(90, 35, 'I agree with this on blog 16 post 90.'),
(91, 36, 'Thought-provoking on blog 16 post 91.'),
(92, 37, 'Deep analysis on blog 16 post 92.'),
(93, 35, 'Impressive work on blog 16 post 93.'),
(94, 36, 'Really liked the content on blog 16 post 94.'),
(95, 37, 'Interesting perspective on blog 16 post 95.'),
(96, 35, 'Enjoyed reading this on blog 16 post 96.'),
(97, 36, 'Good points made on blog 16 post 97.'),
(98, 37, 'Insightful commentary on blog 16 post 98.'),
(99, 35, 'WOOO on blog 16 post 99.'),
(100, 36, 'DAMNN on blog 16 post 100.'),
(101, 37, 'GOOGLE TRANSLATE COOKED on blog 16 post 101.');

-- Blog ID 19 (post IDs 132-146)
INSERT INTO comments (post_id, user_id, comment_text) VALUES
(132, 35, 'Stupid comment on blog 19 post 132.'),
(133, 36, 'Does your doors dont have locks? on blog 19 post 133.'),
(134, 37, 'Does your English haven''t good? on blog 19 post 134.'),
(135, 35, 'You speak English because it''s the only language you know. I speak English because it''s the only language you know. We are not the same on blog 19 post 135.'),
(136, 36, 'WOOO on blog 19 post 136.'),
(137, 37, 'DAMNN on blog 19 post 137.'),
(138, 35, 'GOOGLE TRANSLATE COOKED on blog 19 post 138.'),
(139, 36, 'BRO CHILL on blog 19 post 139.'),
(140, 37, 'Stupid comment on blog 19 post 140.'),
(141, 35, 'Does your doors dont have locks? on blog 19 post 141.'),
(142, 36, 'Does your English haven''t good? on blog 19 post 142.'),
(143, 37, 'You speak English because it''s the only language you know. I speak English because it''s the only language you know. We are not the same on blog 19 post 143.'),
(144, 35, 'WOOO on blog 19 post 144.'),
(145, 36, 'DAMNN on blog 19 post 145.'),
(146, 37, 'GOOGLE TRANSLATE COOKED on blog 19 post 146.');

-- replies to some comments 
INSERT INTO comments (post_id, parent_comment_id, user_id, comment_text) VALUES 
(132, 222, 37, 'Stupid comment'),
(132, 222, 38, 'Stupid comment'),
(132, 222, 36, 'Stupid comment'),
(132, 252, 35, 'Its not stupid'),
(132, 253, 35, 'Its not stupid'),
(132, 255, 36, '123'),
(132, 256, 36, '123'),
(132, 257, 37, 'random'),
(132, 257, 37, 'random reply'),
(132, 258, 37, 'reply to myself');

-- Likes for posts 117-131 by user 39
DO $$
DECLARE
    post_id INT;
BEGIN
    FOR post_id IN 117..131 LOOP
        INSERT INTO post_likes (post_id, user_id)
        VALUES (post_id, 39);
    END LOOP;
END $$;

-- Likes for posts 42-56
DO $$
DECLARE
    post_id INT;
BEGIN
    FOR post_id IN 42..56 LOOP
        INSERT INTO post_likes (post_id, user_id)
        VALUES (post_id, 39);
    END LOOP;
END $$;


-- For comments made by user 31 liked by user 40
INSERT INTO comment_likes (comment_id, user_id)
SELECT id, 40
FROM comments
WHERE user_id = 31;

-- For comments made by user 37 like by user 40
INSERT INTO comment_likes (comment_id, user_id)
SELECT id, 40
FROM comments
WHERE user_id = 37;

-- User 40 follows users 20, 18, 11, 14, 37, and 31
INSERT INTO user_followings (follower_id, following_id)
VALUES (40, 20), (40, 18), (40, 11), (40, 14), (40, 37), (40, 31);

-- User 30 follows users 20, 18, 11, 14, 37, and 31
INSERT INTO user_followings (follower_id, following_id)
VALUES (30, 20), (30, 18), (30, 11), (30, 14), (30, 37), (30, 31);

-- User 25 follows users 20, 18, 11, 14, 37, and 31
INSERT INTO user_followings (follower_id, following_id)
VALUES (25, 20), (25, 18), (25, 11), (25, 14), (25, 37), (25, 31);

-- User 24 follows users 20, 18, 11, 14, 37, and 31
INSERT INTO user_followings (follower_id, following_id)
VALUES (24, 20), (24, 18), (24, 11), (24, 14), (24, 37), (24, 31);


-- some comments on blog 8
INSERT INTO comments (post_id, user_id, comment_text)
SELECT post_id, user_id, comment_text
FROM (
    VALUES
        (8, 10, 'Comment from user 10 on blog 8'),
        (8, 9, 'Comment from user 9 on blog 8'),
        (8, 8, 'Comment from user 8 on blog 8'),
        (8, 7, 'Comment from user 7 on blog 8'),
        (8, 6, 'Comment from user 6 on blog 8'),
        (8, 5, 'Comment from user 5 on blog 8')
) AS c(post_id, user_id, comment_text);

INSERT INTO users (username, password, email, role) VALUES
('jake_new', 'password10', 'jake_new@example.com', 'tourist'),
('lily_new', 'password11', 'lily_new@example.com', 'tourist'),
('mike_new', 'password12', 'mike_new@example.com', 'tourist'),
('nina_new', 'password13', 'nina_new@example.com', 'tourist'),
('oliver_new', 'password14', 'oliver_new@example.com', 'tourist'),
('paula_new', 'password15', 'paula_new@example.com', 'tourist'),
('john123_new', 'password16', 'john123_new@example.com', 'tourist'),
('johnn1234_new', 'password17', 'john1234_new@example.com', 'tourist'),
('zoi123_new', 'password18', 'zoi123_new@example.com', 'tourist'),
('temp1_new', 'password19', 'temp1_new@example.com', 'tourist'),
('temp2_new', 'password20', 'temp2_new@example.com', 'tourist'),
('temp3_new', 'password21', 'temp3_new@example.com', 'tourist'),
('temp4_new', 'password22', 'temp4_new@example.com', 'tourist'),
('temp5_new', 'password23', 'temp5_new@example.com', 'tourist'),
('temp6_new', 'password24', 'temp6_new@example.com', 'tourist'),
('temp7_new', 'password25', 'temp7_new@example.com', 'tourist'),
('temp8_new', 'password26', 'temp8_new@example.com', 'tourist'),
('temp9_new', 'password27', 'temp9_new@example.com', 'tourist'),
('temp10_new', 'password28', 'temp10_new@example.com', 'tourist'),
('temp11_new', 'password29', 'temp11_new@example.com', 'tourist'),
('temp12_new', 'password30', 'temp12_new@example.com', 'tourist'),
('temp13_new', 'password31', 'temp13_new@example.com', 'tourist');

INSERT INTO post_likes (post_id, user_id) VALUES
(14, 2),
(23, 3),
(32, 4),
(41, 5),
(45, 6),
(66, 7),
(75, 8),
(84, 9),
(92, 10),
(120, 1),
(131, 41),
(132, 41),
(123, 41),
(34, 41),
(54, 41),
(65, 41),
(79, 41),
(91, 24),
(29, 25),
(93, 26),
(94, 27),
(59, 28),
(69, 29);


INSERT INTO user_followings (follower_id, following_id) VALUES
(41, 31),
(41, 23),
(41, 33),
(41, 40),
(24, 12),
(25, 21),
(26, 33),
(27, 40),
(28, 15),
(29, 16),
(30, 17),
(31, 18),
(32, 19),
(33, 30),
(34, 13),
(35, 17);

INSERT INTO post_likes (post_id, user_id) VALUES
-- User 12 likes
(20, 12),
(22, 12),
(23, 12),
(42, 12),
(43, 12),

-- User 13 likes
(21, 13),
(24, 13),
(25, 13),
(40, 13),
(44, 13),

-- User 14 likes
(20, 14),
(26, 14),
(27, 14),
(41, 14),
(45, 14),

-- User 15 likes
(21, 15),
(28, 15),
(29, 15),
(42, 15),
(46, 15),

-- User 16 likes
(22, 16),
(30, 16),
(31, 16),
(43, 16),
(47, 16),

-- User 17 likes
(23, 17),
(32, 17),
(33, 17),
(44, 17),
(48, 17),

-- User 18 likes
(24, 18),
(34, 18),
(35, 18),
(45, 18),
(49, 18),

-- User 19 likes
(25, 19),
(36, 19),
(37, 19),
(46, 19),
(50, 19),

-- User 20 likes
(26, 20),
(38, 20),
(39, 20),
(47, 20),
(51, 20),

-- User 50 likes
(27, 50),
(40, 50),
(41, 50),
(48, 50),
(52, 50),

-- User 22 likes
(28, 22),
(42, 22),
(43, 22),
(49, 22),
(53, 22),
(54, 22),
(55, 22),
(56, 22);
-- Insert likes for user 59 on posts from user 19
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 59 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 19;

-- Insert likes for user 59 on posts from user 17
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 59 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 17;

-- Insert likes for user 31 on posts from user 13
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 31 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 13;

-- Insert likes for user 21 on posts from user 11
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 21 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 11;

-- Insert likes for user 12 on posts from user 11
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 12 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 11;

-- Insert likes for user 30 on posts from user 16
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 30 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 16;

-- Insert likes for user 33 on posts from user 19
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 33 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 19;

-- Insert likes for user 52 on posts from user 17
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 52 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 17;

-- Insert likes for user 21 on posts from user 15
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 21 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 15;

-- Insert likes for user 52 on posts from user 12
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 52 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 12;

-- Insert likes for user 21 on posts from user 13
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 21 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 13;

-- Insert likes for user 32 on posts from user 14
INSERT INTO post_likes (post_id, user_id)
SELECT p.id AS post_id, 32 AS user_id
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.user_id = 14;

INSERT INTO post_likes (post_id, user_id) VALUES
(45, 58),
(45, 56),
(45, 54),
(45, 55);

INSERT INTO user_followings(follower_id, following_id) VALUES
(55, 11),
(54, 10),
(54, 11),
(56, 11),
(57, 12),
(57, 13),
(57, 14),
(57, 15),
(57, 16),
(57, 17),
(57, 18),
(53, 19),
(52, 20),
(51, 21);