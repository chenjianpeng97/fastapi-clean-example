import json
import sys

sys.path.insert(0, "src")
from app.setup.app_factory import create_web_app
from app.setup.config.settings import load_settings

settings = load_settings()
app = create_web_app(settings)
openapi = app.openapi()
with open("../docs/openapi.json", "w") as f:
    json.dump(openapi, f, indent=4)
print("openapi.json updated")
