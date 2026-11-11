import os

from . import create_app

app = create_app()

if __name__ == "__main__":
    debug_enabled = os.environ.get("HELPSPACE_DEBUG", "0") == "1"
    app.run(
        host=os.environ.get("HELPSPACE_HOST", "127.0.0.1"),
        port=8080,
        debug=debug_enabled,
        use_reloader=False,
    )
