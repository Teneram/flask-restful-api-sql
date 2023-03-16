from app.app import app
from app.configurators import configure_app

if __name__ == "__main__":
    app = configure_app(app)
    app.run(host="0.0.0.0", port=5000)
