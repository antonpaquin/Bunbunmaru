from server import app as application, set_db

set_db('/data/bunbunmaru.db')

if __name__ == '__main__':
    application.run()
