from app import app
from app import FlaskConfig
# from werkzeug.serving import run_simple

if __name__ == '__main__':
    app.run(host=FlaskConfig.HOST, port=FlaskConfig.PORT)
    # run_simple('localhost', 5000, app)