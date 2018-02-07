import os
from urllib.parse import urlparse
from flask import Flask, request, jsonify, Response
from rq import Queue
from worker import conn
from move import parse_url

app = Flask(__name__)
q = Queue(connection=conn)

def get_status(job):
    status = {
        'id': job.id,
        'result': job.result,
        'status': 'failed' if job.is_failed else 'pending' if job.result == None else 'completed'
    }
    status.update(job.meta)
    return status

@app.route("/", methods=['GET', 'POST'])
def handle_job():
    query_id = request.values.get('job')
    if query_id:
        found_job = q.fetch_job(query_id)
        if found_job:
            output = get_status(found_job)
        else:
            output = { 'id': None, 'error_message': 'No job exists with the id number ' + query_id }
    else:
        new_job = q.enqueue(parse_url, timeout='1h', kwargs={key: request.values.get(key) for key in request.values})
        output = get_status(new_job)
    response = jsonify(output)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)