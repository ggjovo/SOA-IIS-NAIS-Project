import grpc
from concurrent import futures
import psycopg2
from pymongo import MongoClient
from auth import authenticate_user
from db_specs import db_config
import tour_pb2
import tour_pb2_grpc


class TourServiceServicer(tour_pb2_grpc.TourServiceServicer):

    def __init__(self):
        uri = "mongodb://traveler-mongodb-1"
        self.client = MongoClient(uri)
        self.db = self.client['tourist']
        self.tours_collection = self.db['tours']
        self.tags_collection = self.db['tags']
        self.checkpoint_collection = self.db['checkpoints']

    def GetAllToursGuide(self, request, context):
        try:
            token = request.cookies.get('token')
            if not token:
                context.set_code(grpc.StatusCode.UNAUTHORIZED)
                context.set_details("Unauthorized")
                return tour_pb2.TourList()

            authenticated, user_info = authenticate_user(token)
            if not authenticated:
                context.set_code(grpc.StatusCode.UNAUTHORIZED)
                context.set_details("Unauthorized")
                return tour_pb2.TourList()

            if user_info['role'] != 'guide':
                context.set_code(grpc.StatusCode.UNAUTHORIZED)
                context.set_details("Unauthorized")
                return tour_pb2.TourList()

            user_id = user_info['id']

            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    tours.id,
                    tours.title, 
                    tours.description, 
                    tours.duration, 
                    tours.price, 
                    tours.difficulty, 
                    tours.status, 
                    tags.tags,
                    checkpoints.checkpoint_names,
                    checkpoints.checkpoint_longitude,
                    checkpoints.checkpoint_latitude,
                    checkpoints.checkpoint_positions
                FROM tours
                LEFT JOIN (
                    SELECT tour_id, array_agg(name) AS tags
                    FROM tags
                    GROUP BY tour_id
                ) AS tags ON tours.id = tags.tour_id
                LEFT JOIN (
                    SELECT tour_id,
                        array_agg(name) AS checkpoint_names,
                        array_agg(longitude) AS checkpoint_longitude,
                        array_agg(latitude) AS checkpoint_latitude,
                        array_agg(position) AS checkpoint_positions
                    FROM checkpoints
                    GROUP BY tour_id
                ) AS checkpoints ON tours.id = checkpoints.tour_id
                WHERE tours.guide_id = %s;
            """, (user_id,))

            tours_with_tags = []
            columns = [desc[0] for desc in cursor.description]

            for row in cursor.fetchall():
                tour = {columns[i]: value for i, value in enumerate(row)}
                tour['tags'] = tour['tags'] if tour['tags'] is not None else []
                tours_with_tags.append(tour)

            cursor.close()
            conn.close()

            return tour_pb2.TourList(tours=tours_with_tags)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error retrieving tours: " + str(e))
            return tour_pb2.TourList()

    def GetAllToursTourist(self, request, context):
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            token = request.cookies.get('token')
            if not token:
                context.set_code(grpc.StatusCode.UNAUTHORIZED)
                context.set_details("Unauthorized")
                return tour_pb2.TourList()

            authenticated, user_info = authenticate_user(token)
            if not authenticated:
                context.set_code(grpc.StatusCode.UNAUTHORIZED)
                context.set_details("Unauthorized")
                return tour_pb2.TourList()

            if user_info['role'] != 'tourist':
                context.set_code(grpc.StatusCode.UNAUTHORIZED)
                context.set_details("Unauthorized")
                return tour_pb2.TourList()

            cursor.execute("""
                SELECT 
                    tours.id,
                    tours.title, 
                    tours.description, 
                    tours.duration, 
                    tours.price, 
                    tours.difficulty, 
                    tours.status, 
                    array_agg(tags.name) AS tags,
                    first_checkpoint.checkpoint_names AS first_checkpoint_name,
                    first_checkpoint.checkpoint_latitude AS first_checkpoint_latitude,
                    first_checkpoint.checkpoint_longitude AS first_checkpoint_longitude,
                    first_checkpoint.checkpoint_positions AS first_checkpoint_position
                FROM tours
                LEFT JOIN (
                    SELECT tour_id,
                        array_agg(name) AS checkpoint_names,
                        array_agg(longitude) AS checkpoint_longitude,
                        array_agg(latitude) AS checkpoint_latitude,
                        array_agg(position) AS checkpoint_positions
                    FROM (
                        SELECT tour_id, name, longitude, latitude, position
                        FROM checkpoints
                        WHERE (tour_id, position) IN (
                            SELECT tour_id, MIN(position)
                            FROM checkpoints
                            GROUP BY tour_id
                        )
                    ) AS min_position_checkpoints
                    GROUP BY tour_id
                ) AS first_checkpoint ON tours.id = first_checkpoint.tour_id
                LEFT JOIN tags ON tours.id = tags.tour_id
                GROUP BY tours.id, tours.title, tours.description, tours.duration, tours.price, tours.difficulty, tours.status, first_checkpoint.checkpoint_names, first_checkpoint.checkpoint_latitude, first_checkpoint.checkpoint_longitude, first_checkpoint.checkpoint_positions;

            """)

            tours_with_tags = []
            columns = [desc[0] for desc in cursor.description]

            for row in cursor.fetchall():
                tour = {columns[i]: value for i, value in enumerate(row)}
                tour['tags'] = tour['tags'] if tour['tags'] is not None else []
                tours_with_tags.append(tour)

            cursor.close()
            conn.close()

            return tour_pb2.TourList(tours=tours_with_tags)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error retrieving tours: " + str(e))
            return tour_pb2.TourList()

    def CreateTour(self, request, context):
        try:
            token = request.cookies.get('token')
            if not token:
                context.set_code(grpc.StatusCode.UNAUTHORIZED)
                context.set_details("Unauthorized")
                return tour_pb2.TourCreationResponse(message="Unauthorized")

            authenticated, user_info = authenticate_user(token)
            if not authenticated:
                context.set_code(grpc.StatusCode.UNAUTHORIZED)
                context.set_details("Unauthorized")
                return tour_pb2.TourCreationResponse(message="Unauthorized")
            
            if user_info['role'] != 'guide':
                context.set_code(grpc.StatusCode.UNAUTHORIZED)
                context.set_details("Unauthorized")
                return tour_pb2.TourCreationResponse(message="Unauthorized")

            title = request.title
            description = request.description
            duration = request.duration
            difficulty = request.difficulty
            tags = request.tags
            price = request.price
            status = request.status or 'draft'

            if not all([title, description, duration, difficulty, price]):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Incomplete data provided")
                return tour_pb2.TourCreationResponse(message="Incomplete data provided")

            user_id = int(user_info['id'])

            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tours (title, description, duration, difficulty, price, status, guide_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                           (title, description, duration, difficulty, price, status, user_id))

            tour_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()

            tour_data = {
                '_id': tour_id,
                'title': title,
                'description': description,
                'duration': duration,
                'difficulty': difficulty,
                'price': price,
                'status': status
            }

            self.tours_collection.insert_one(tour_data)

            # Insert tags for the newly created tour
            self.insert_tags_for_tour(tour_id, tags)

            return tour_pb2.TourCreationResponse(message="Tour created successfully", tour_id=tour_id)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error creating tour: " + str(e))
            return tour_pb2.TourCreationResponse(message="Error creating tour")

    def AddCheckpoint(self, tour_id):
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT id, tour_id, latitude, longitude, name, position FROM checkpoints WHERE tour_id = %s", (tour_id,))
            checkpoints = []
            for row in cursor.fetchall():
                checkpoint_id, tour_id, latitude, longitude, name, position = row
                checkpoint_data = {
                    '_id': checkpoint_id,
                    'tour_id': tour_id,
                    'latitude': float(latitude),
                    'longitude': float(longitude),
                    'name': name,
                    'position': int(position)
                }
                checkpoints.append(checkpoint_data)

            cursor.close()
            conn.close()

            return checkpoints
        except Exception as e:
            print("Error fetching checkpoints:", e)
            return None

    def insert_tags_for_tour(self, tour_id, tags):
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            for tag in tags:
                cursor.execute("INSERT INTO tags (name, tour_id) VALUES (%s, %s)",
                               (tag, tour_id))

            conn.commit()
            cursor.close()
            conn.close()

            tag_ids = self.get_tag_ids_by_tour_id(tour_id)

            for tag_id in tag_ids:
                self.tags_collection.insert_one({'_id': tag_id ,'tour_id': tour_id, 'name': tag})

            return True
        except Exception as e:
            print("Error inserting tags:", e)
            return False

    def get_tag_ids_by_tour_id(self, tour_id):
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tags WHERE tour_id = %s", (tour_id,))
            tag_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return tag_ids
        except Exception as e:
            print("Error fetching tag ids:", e)
            return []

import logging

def serve():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tour_pb2_grpc.add_TourServiceServicer_to_server(TourServiceServicer(), server)
    server.add_insecure_port('[::]:50054')
    server.start()
    logger.info("gRPC server for tour service is running on port 50054...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
