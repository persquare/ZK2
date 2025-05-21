import argparse

from . import server

def app():
    long_desc = """
    Serve a ZK "database"
    """

    parser = argparse.ArgumentParser(description=long_desc)

    parser.add_argument('--debug', action="store_true", default=False,
                       help='Run Flask server with debug option')

    parser.add_argument('--port', default=9075,
                       help='Port to serve on')

    args = parser.parse_args()

    app = server.create_app()
    app.run(debug = args.debug, port=args.port)


if __name__ == '__main__':
    app()