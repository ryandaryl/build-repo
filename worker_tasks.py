import base64
import requests
from cStringIO import StringIO

def png_encode(fig):
    io = StringIO()
    fig.savefig(io, format='png')
    return base64.encodestring(io.getvalue())

def run_script(filename):
    execfile(filename, globals())
    return png_encode(fig)