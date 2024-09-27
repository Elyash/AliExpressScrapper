import pika
import json
from pymongo import MongoClient
import os

# MongoDB setup
mongo_client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = mongo_client['MyFullstackProject']
gifts_collection = db['Gifts']

# RabbitMQ setup
rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
channel = connection.channel()

def callback(ch, method, properties, body):
    gift_request = json.loads(body)
    gift = {
        "link": gift_request['link'],
        "user_email": gift_request['user_email'],
        "name": "Gift Name",  # Placeholder, you might want to scrape the data here
        "price": "Gift Price",  # Placeholder
        "image": "Gift Image"  # Placeholder
    }
    gifts_collection.insert_one(gift)
    print(f"Gift added to MongoDB: {gift}")

channel.basic_consume(queue='gift_requests', on_message_callback=callback, auto_ack=True)

print('Waiting for gift requests...')
channel.start_consuming()
