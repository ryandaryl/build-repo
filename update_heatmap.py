
import matplotlib.cm
from PIL import Image
import numpy as np
import requests
from ftplib import FTP
import pytz
from io import BytesIO, StringIO
from hashlib import sha256
import datetime
import json
import os


def write_image_local(path, content):
    Image.fromarray(output_array).save(path)

def delete_image_local(path):
    os.remove(path)

def write_json_local(path, content):
    with open(path, 'w') as f:
        f.write(json.dumps(content, default=str))

def read_json_local(path):
    with open(path) as f:
        return json.load(f)

def write_image_ftp(path, content):
    buffer = BytesIO()
    Image.fromarray(output_array).save(buffer, format= 'PNG')
    buffer.seek(0)
    ftp.storbinary('STOR ' + path, buffer)

def delete_image_ftp(path):
    ftp.delete(path)

def write_json_ftp(path, content):
    ftp.storlines('STOR ' + path, BytesIO(bytes(json.dumps(content), encoding='utf8')))

def read_json_ftp(path):
    with StringIO() as f:
        ftp.retrlines('RETR '+ path, f.write)
        return(json.loads(f.getvalue()))

colours = [
    (255, 255, 255),
    (255, 255, 255),
    (199, 0, 254),
    (206, 0, 133),
    (176, 0, 1),
    (224, 0, 2),
    (253, 58, 5),
    (255, 160, 4),
    (255, 226, 1),
    (129, 204, 1),
    (0, 177, 3),
    (1, 228, 3),
    (0, 128, 129),
    (0, 79, 255),
    (4, 206, 250),
    (0, 0, 0)
]

ftp = FTP('1lmw.c1.biz')   # os.environ.get('BIZNF_URI', None))
ftp.login(
    user='2153020_rdm', # os.environ.get('BIZNF_USERNAME', None),
    passwd='(Password11)' # os.environ.get('BIZNF_PASSWORD', None)
)
ftp.cwd('/{}/{}/'.format(
    '1lmw.c1.biz', # os.environ.get('BIZNF_URI', None),
    'west-java' # os.environ.get('FTP_DIRECTORY', None)
))
write_image_func = write_image_ftp
delete_image_func = delete_image_ftp
write_json_func = write_json_ftp
read_json_func = read_json_ftp

palette_image = Image.new('P', (16, 16))
palette_image.putpalette(sum([list(i) for i in colours], []))
background_array = np.array(Image.open('west_java.png').convert('RGB'))
image_url = 'https://dataweb.bmkg.go.id/MEWS/Radar/TANG_SingleLayerCRefQC.png'
image_array = np.array(Image.open(BytesIO(requests.get(image_url).content)).convert('RGB'))
# image_array = np.array(Image.open('TANG_SingleLayerCRefQC_1.png').convert('RGB'))
timestamp_hash = sha256(image_array[:50, ...].tostring()).hexdigest()
radar_heatmap_list = read_json_func('radar_heatmap.json')
if any([timestamp_hash == heatmap_dict['timestamp_hash'] for heatmap_dict in radar_heatmap_list]):
    exit()
heatmap_array = np.zeros(image_array.shape)
grayscale_array = np.zeros(image_array.shape[:2], dtype=np.uint8)
heatmap_array[image_array != background_array] = image_array[image_array != background_array]
heatmap_array[:50, ...] = 0
heatmap_array = np.array(Image.fromarray(heatmap_array.astype(np.uint8)).quantize(palette=palette_image).convert('RGB'))
for i, colour_tuple in enumerate(reversed(colours)):
    grayscale_array[(heatmap_array == colour_tuple).all(axis = -1)] = i*255/(len(colours)-1)
output_array = (matplotlib.cm.get_cmap('coolwarm')(grayscale_array)*255).astype(np.uint8)
output_array[:, :, 3][grayscale_array == 0] = 0
timestamp = (datetime.datetime.now(tz=pytz.timezone('Asia/Jakarta'))
    - datetime.timedelta(minutes=6)).strftime('%Y-%m-%d %I:%M %p').replace(' 0', ' ')
if len(radar_heatmap_list) == 5:
    filename = radar_heatmap_list[0]['filename']
    files = []
    ftp.retrlines('LIST', callback=files.append)
    files = [line.split(' ')[-1] for line in files]
    if filename in files:
        delete_image_func(filename)
    radar_heatmap_list = radar_heatmap_list[1:]
radar_heatmap_list = radar_heatmap_list + [{
    'timestamp_hash': timestamp_hash,
    'timestamp': timestamp,
    'filename': timestamp_hash + '.png'
}]
write_json_func('radar_heatmap.json', radar_heatmap_list)
write_image_func(timestamp_hash + '.png', output_array)
