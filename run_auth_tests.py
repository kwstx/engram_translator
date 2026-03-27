import sys
from unittest.mock import MagicMock
sys.modules["pyswip"] = MagicMock()

import pytest
retcode = pytest.main(["tests/test_auth.py", "-v"])
sys.exit(retcode)
