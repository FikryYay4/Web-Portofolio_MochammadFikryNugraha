import sys
import traceback

try:
    from app import create_app
    app = create_app()
except Exception as e:
    traceback.print_exc(file=sys.stdout)
    sys.stdout.flush()
    raise
