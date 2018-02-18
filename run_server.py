import os
from gunicorn.app.base import BaseApplication
from gettingstarted.wsgi import application as app

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
    run_server(app, '0.0.0.0', os.environ.get('PORT', 8000))