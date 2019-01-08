from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


if __name__ == '__main__':
    code = """
            from flask import Flask
            app = Flask(__name__)
            
            @app.route('/')
            def hello_world():
                return 'Hello, World!'
            """
    print(highlight(code, PythonLexer(), HtmlFormatter()))
    print(HtmlFormatter().get_style_defs('.highlight'))
