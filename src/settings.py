DOMAIN = {'time_series': {}}

# Please note that MONGO_HOST and MONGO_PORT could very well be left
# out as they already default to a bare bones local 'mongod' instance.
MONGO_HOST = 'localhost'
MONGO_PORT = 27017

# Skip this block if your db has no auth. But it really should.
# MONGO_USERNAME = '<your username>'
# MONGO_PASSWORD = '<your password>'
# Name of the database on which the user can be authenticated,
# needed if --auth mode is enabled.
# MONGO_AUTH_SOURCE = '<dbname>'

MONGO_DBNAME = 'corona'

RESOURCE_METHODS = ['GET']
ITEM_METHODS = ['GET']

ALLOW_UNKNOWN = True
SERVER_NAME = None