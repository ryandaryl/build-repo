import os, json
from flask import Flask, request, render_template
from rq import Queue
from worker import conn
from worker_tasks import run_script

app = Flask(__name__)
q = Queue(connection=conn)

def get_status(job):
    app_url = 'https://tensor-rdm.herokuapp.com'
    status = {
        'id': job.id,
        'result': job.result,
        'status': '',
        'message': '',
        'link': ''
    }
    options = {
        'status': 'failed'
    } if job.is_failed else {
        'status': 'pending',
        'message': 'Still working. Wait a few minutes and click the link to see if the job is ready.',
        'link': '<a href="{}?job={}">Click here.</a>'.format(app_url, job.id)
    } if job.result == None else {
        'status': 'completed'
    }
    status.update(options)
    status.update(job.meta)
    return status

@app.route("/")
def handle_job():
    query_id = request.args.get('job')
    if query_id:
        found_job = q.fetch_job(query_id)
        if found_job:
            if found_job.result:
                response = render_template('output.html', output=found_job.result)
            else:
                response = render_template('wait.html', status=get_status(found_job))
        else:
            response = { 'id': None, 'error_message': 'No job exists with the id number ' + query_id }
    else:
        new_job = q.enqueue(run_script, timeout='1h')
        response = render_template('wait.html', status=get_status(new_job))
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)