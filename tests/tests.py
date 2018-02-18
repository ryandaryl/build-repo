import os
from gunicorn.app.base import BaseApplication
import project

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

if __name__ == '__main__':
    host = '0.0.0.0'
    port = os.environ.get('PORT', 8000)
    run_server(project.app, host, port)