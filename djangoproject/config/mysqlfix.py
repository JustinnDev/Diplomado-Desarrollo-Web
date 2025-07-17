# mysql_fix.py
from django.db.backends.mysql import features

features.DatabaseFeatures.supports_transactions = False
features.DatabaseFeatures.uses_savepoints = False