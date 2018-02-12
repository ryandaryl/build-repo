
import os, base64, io, datetime
import requests
import pymongo
from PIL import Image

def resize_to_width(pil_img, width):
    wpercent = (basewidth/float(pil_img.size[0]))
    hsize = int((float(pil_img.size[1])*float(wpercent)))
    return pil_img.resize((basewidth,hsize), Image.ANTIALIAS)

def save_to_mongo(img):
    time_now = datetime.datetime.now()
    url = 'mongodb://genincweather:INFO30005@weather-shard-00-00-hifln.mongodb.net:27017,weather-shard-00-01-hifln.mongodb.net:27017,weather-shard-00-02-hifln.mongodb.net:27017/<DATABASE>?ssl=true&replicaSet=weather-shard-0&authSource=admin'
    client = pymongo.MongoClient(url)
    db = client.test_db
    col = db.test_col
    db.posts.insert_one({'timestamp': datetime.datetime.now(), 'img': img})
    for post in db.posts.find():
        delta = time_now - post['timestamp']
        if delta.seconds > 3600:
            db.posts.remove(post)

def get_image(url):
    basewidth = 100
    response = requests.get(url, stream=True)
    pil_img = Image.open(io.BytesIO(response.content))
    buffer = io.BytesIO()
    pil_img = pil_img.crop((300, 200, 600, 400))
    pil_img.save(buffer, format="PNG")
    png_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    save_to_mongo(png_b64)
    return '<img src="data:image/png;base64,' + png_b64 + '" />'

if __name__ == "__main__":
    url = 'http://dataweb.bmkg.go.id/MEWS/Radar/Citra_Radar_TANG.png'
    get_image(url)
