#this is the file that is invoked to start up a dev server. It gets a copy from your package and runs it.
#this won't be used in production
from templates import app
# Load this config object for development mode
app.config.from_object('configurations.DevelopmentConfig')
app.run()