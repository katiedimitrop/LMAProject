from flask import Flask

app = Flask(__name__,
            static_folder = './public',
            template_folder="./static")

from templates.etree.views import etree_blueprint

app.register_blueprint(etree_blueprint)