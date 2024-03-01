from app import app
from website import Website

from json import load

if __name__ == "__main__":

    site = Website(app)
    for route in site.routes:
        app.add_url_rule(
            route,
            view_func=site.routes[route]["function"],
            methods=site.routes[route]["methods"],
        )

    app.run(host="0.0.0.0", port=5000, debug=True)
