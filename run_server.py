import os, time
from subprocess import Popen, PIPE
from gunicorn.app.base import BaseApplication
from project import app

#https://programtalk.com/python-examples/gunicorn.app.base.BaseApplication/
def run_server(app, host, port):
    import gunicorn.app.base
 
    class FlaskGUnicornApp(gunicorn.app.base.BaseApplication):
        options = {
            'bind': '{}:{}'.format(host, port),
            'workers': 1
        }
 
        def load_config(self):
            for k, v in self.options.items():
                self.cfg.set(k.lower(), v)
 
        def load(self):
            return app
 
    FlaskGUnicornApp().run()

def run_gunicorn():
    from subprocess import Popen, PIPE
    process = Popen(['gunicorn', 'project:app'])
    stdout, stderr = process.communicate()
    print(stdout)

def run_behave():
    os.chdir('tests')
    os.system('(sleep 10 && behave &)')
    '''
    time.sleep(30)
    os.chdir('tests')
    process = Popen(['behave'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    '''

if __name__ == '__main__':
    #run_behave()
    run_server(app, '0.0.0.0', int(os.environ.get('PORT', 8000)))