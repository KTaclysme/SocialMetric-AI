import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from app import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
