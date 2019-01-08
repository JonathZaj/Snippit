import os
from bottle import (get, post, request, route, run, static_file,
                    template, jinja2_view, error)
import python.utils as utils
import json
import python.config as config
from python.snippit_sql import sql_create_db_if_doesnt_exist
from python.snippit_sql import add_snippet
from python.search import search_snippet as search_snippet
from python.populate_db import populate_db
from python.suggested_search import suggested_search as suggested_search


# Static Routes
@get("/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="./js")


@get("/css/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="./css")


@get("/images/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    return static_file(filepath, root="./images")


@get("/font/<filepath:re:.*\.(eot|otf|svg|ttf|woff|woff2?)>")
def font(filepath):
    return static_file(filepath, root="./font")


@route('/')
def index():
    return template("/pages/index.html")


@route("/search", method='GET')
@jinja2_view('search.html', template_lookup=['templates'])
def display_results():
    search_query = request.params.get('query')
    results = search_snippet(search_query)
    #res_lst = jsone.snipp_json
    return {"results": results, "count": len(results)}


@route("/wide-search", method='GET')
@jinja2_view('search.html', template_lookup=['templates'])
def display_results():
    search_query = request.params.get('query')
    search_query = suggested_search(search_query)
    results = search_snippet(search_query)
    print(results)
    #res_lst = jsone.snipp_json
    return {"results": results}


@get("/post_snippet")
def display_post():
    return template("./templates/post_snippet.html")


@post("/add_snippet")
def add_snipet():
    snippet = request.forms.get("code").strip()
    language = [request.forms.get("language")]
    library = [request.forms.get("library")]
    topic = [request.forms.get("topic")]
    title = request.forms.get("title").strip()
    explanation = request.forms.get("explanation").strip()
    tags_info = [language, library, topic]

    add_snippet(title, snippet, explanation, 1, tags_info) # Hard coded user_id for now

    return template("/pages/index.html")


@error(404)
def error404(error):
    sectionTemplate = "./templates/404.tpl"
    return template("./pages/index.html", version=utils.getVersion(), sectionTemplate=sectionTemplate, sectionData={})


@error(500)
def error500(error):
    sectionTemplate = "./templates/404.tpl"
    return template("./pages/index.html", version=utils.getVersion(), sectionTemplate=sectionTemplate, sectionData={})


@route('/users/<user_id>')
def show_user_info(user_id):
    pass


@route('/login')
def login():
    return '''
        <form action="/login" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
    '''


@route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    user_id = check_login(username, password)
    if user_id:
        return "Welcome Back {}!.</p>".format(username)

    else:
        return "<p>Login failed.</p>"


# sql_create_db_if_doesnt_exist(True)
# populate_db()
sql_create_db_if_doesnt_exist()
run(host=config.HOST, debug=True, port=os.environ.get('PORT', config.PORT))
