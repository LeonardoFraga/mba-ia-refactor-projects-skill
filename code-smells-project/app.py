"""Top-level entry point. Boots the MVC app defined under src/.

Run with: python app.py
"""
from src.app import create_app
from src.config import settings

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:%s" % settings.PORT)
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
