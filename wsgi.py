"""Application entry point."""
from application import create_app
from flask import Flask

def main():
    app = create_app()
    app.run(host = '0.0.0.0', debug = True)


if __name__ == "__main__":
    main()
