from pathlib import Path

APPROOT = '/'

DB_PATH = Path(".") / "database" / "100hackerfragen.db"
IMPORT_PATH = Path("question_import")
IMPORT_FROM_FILES = False
IMPORT_PATH = Path("import")

# The following toggle allows users to add their own questions 
# to the pool
USER_SUBMITTED_QUESTIONS = False

SALUTATION = "Hacker*innen"
