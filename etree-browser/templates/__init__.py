from flask import Flask

app = Flask(__name__,
            static_folder = './public',
            template_folder="./static")

from templates.etree.views import etree_blueprint, page_not_found, internal_error
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_error)
app.register_blueprint(etree_blueprint)