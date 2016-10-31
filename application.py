from lms import app

application = app

if __name__ == '__main__':
    application.run(
        host=application.config['BIND_IP'],
        port=application.config['BIND_PORT'],
        debug=application.config['DEBUG'])
