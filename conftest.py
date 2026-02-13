import os
import sys
import types

# Minimal test-time stubs.

# Ensure environment variables exist so modules that read them don't error at import
for k in (
    "GEMINI_API_KEY",
    "AIRTABLE_PAT",
    "AIRTABLE_BASE_ID",
    "GOOGLE_API_KEY",
    "GOOGLE_CSE_ID",
    "NCBI_API_KEY",
):
    os.environ.setdefault(k, "")


# Stub chromedriver_autoinstaller.install()
if "chromedriver_autoinstaller" not in sys.modules:
    mod = types.ModuleType("chromedriver_autoinstaller")
    mod.install = lambda *a, **k: None
    sys.modules["chromedriver_autoinstaller"] = mod


# Stub google.generativeai with a tiny API used by the code
if "google.generativeai" not in sys.modules:
    google_mod = types.ModuleType("google")
    genai = types.ModuleType("google.generativeai")

    def _configure(api_key=None):
        return None

    class _DummyModel:
        def __init__(self, *args, **kwargs):
            pass

        def generate_content(self, prompt):
            return types.SimpleNamespace(text="MOCK_GENERATIVE_OUTPUT")

    genai.configure = _configure
    genai.GenerativeModel = _DummyModel
    sys.modules["google"] = google_mod
    sys.modules["google.generativeai"] = genai


# Stub pyairtable Table and Api so Airtable calls are no-ops during unit tests
if "pyairtable" not in sys.modules:
    pat_mod = types.ModuleType("pyairtable")

    class Table:
        def __init__(self, *args, **kwargs):
            pass

        def all(self, *a, **k):
            return []

        def update(self, *a, **k):
            return None

        def create(self, *a, **k):
            return None

    class Api:
        def __init__(self, *a, **k):
            pass

        def table(self, *a, **k):
            return Table()

    pat_mod.Table = Table
    pat_mod.Api = Api
    sys.modules["pyairtable"] = pat_mod
