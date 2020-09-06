from flask import Flask
from flask_cors import CORS, cross_origin
import configparser

from routes import *

config = configparser.ConfigParser()
config.read('config.ini')

# Create the application.
app = Flask(__name__)

app.register_blueprint(routes)
cors = CORS(app, resources={r"/*": {"origins": "*"}})




if __name__ == '__main__':

    app.debug = True
    # app.run(port=5000, host='0.0.0.0')
    app.run()



