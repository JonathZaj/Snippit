import python.config as config
from python.config import output as output
from python.config import TerminalColors as TerminalColors
import mysql
import mysql.connector
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


cnx = mysql.connector.connect(user=config.MYSQL_USERNAME,
                              passwd=config.MYSQL_PASSWORD,
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()


def run_query(sql, no_results=False, verbose=False):
    results = None
    if verbose:
        output("Running Query: '%s'" % sql)

    try:
        # Execute the SQL command
        if no_results:
            cursor.execute(sql)
            cnx.commit()
            if verbose:
                output('Success - ' + str(cursor.rowcount) + ' rows affected')
        else:
            cursor.execute(sql)
            # Fetch all the rows in a list of lists.
            results = cursor.fetchall()
            # results are in an array containing the content of your query.
            # Use it as you wish ...

    except mysql.connector.Error as err:
        output(TerminalColors.FAIL + "ERROR: unable to fetch data. ##{}".format(err) + TerminalColors.ENDC, 'Error')
        output(TerminalColors.FAIL + "While running query: '%s' '%s'" % (sql, TerminalColors.ENDC), 'Error')
        return

    return results


def run_query_to_json(query):
    try:
        cursor.execute(query)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        # results are in an array containing the content of your query.
        # Use it as you wish ...
    except mysql.connector.Error as err:
        output(TerminalColors.FAIL + "ERROR: unable to fetch data. ##{}".format(err) + TerminalColors.ENDC, 'Error')
        output(TerminalColors.FAIL + "While running query: '%s' '%s'" % (query, TerminalColors.ENDC), 'Error')
        return

    row_headers = [x[0] for x in cursor.description]  # this will extract row headers
    json_data = []
    for result in results:
        json_data.append(dict(zip(row_headers, result)))

    return json_data


def sql_create_db_if_doesnt_exist(force_create=False):
    """Creates the db """
    database = config.DATABASE
    if force_create:
        run_query('DROP DATABASE IF EXISTS %s;' % database, True)
    run_query('CREATE DATABASE IF NOT EXISTS %s CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;' % database, True)
    run_query('USE %s;' % database, True)

    # USERS
    query = """
            CREATE TABLE IF NOT EXISTS Users (
                user_id MEDIUMINT(7) UNSIGNED NOT NULL AUTO_INCREMENT, 
                username varchar(150) NOT NULL UNIQUE,
                password varchar(150) NOT NULL,
                score MEDIUMINT(7) UNSIGNED NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id)); 
            """
    run_query(query, True)

    # Snippets
    query = """
            CREATE TABLE IF NOT EXISTS Snippets (
                snippet_id MEDIUMINT(6) UNSIGNED NOT NULL AUTO_INCREMENT,
                title varchar(150) NOT NULL UNIQUE,
                snippet TEXT NOT NULL,
                explanation TEXT, 
                date_added DATETIME NOT NULL, 
                user_id MEDIUMINT(7) UNSIGNED NOT NULL, 
                PRIMARY KEY (snippet_id),  
                FOREIGN KEY (user_id) REFERENCES Users (user_id));
            """
    run_query(query, True)

    # TAGS
    query = """
            CREATE TABLE IF NOT EXISTS Tags (
                tag_id SMALLINT(4) UNSIGNED NOT NULL AUTO_INCREMENT, 
                tag_name varchar(150) NOT NULL,
                type varchar(150) NOT NULL,
                PRIMARY KEY (tag_id),
                UNIQUE KEY (tag_name, type)); 
            """
    run_query(query, True)

    # TAGS-SNIPPET MAPPING
    query = """
            CREATE TABLE IF NOT EXISTS Tags_Snippet (
                id SMALLINT(4) UNSIGNED NOT NULL AUTO_INCREMENT,
                tag_id SMALLINT(4) UNSIGNED NOT NULL,
                snippet_id MEDIUMINT(6) UNSIGNED NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY (tag_id) REFERENCES Tags(tag_id), 
                FOREIGN KEY (snippet_id) REFERENCES Snippets(snippet_id),
                UNIQUE KEY (tag_id, snippet_id));
            """
    run_query(query, True)

    # SNIPPET SEARCH
    query = """
            CREATE TABLE IF NOT EXISTS Snippet_Search (
                search_id SMALLINT(4) UNSIGNED NOT NULL AUTO_INCREMENT,
                snippet_id MEDIUMINT(6) UNSIGNED NOT NULL UNIQUE,
                search_text TEXT NOT NULL,
                PRIMARY KEY (search_id), 
                FOREIGN KEY (snippet_id) REFERENCES Snippets(snippet_id));
            """
    run_query(query, True)

    query = 'ALTER TABLE Snippet_Search ADD FULLTEXT(search_text);'
    run_query(query, no_results=True)

    # Votes
    query = """
            CREATE TABLE IF NOT EXISTS Votes (
                vt_id MEDIUMINT(6) UNSIGNED NOT NULL AUTO_INCREMENT, 
                date_added DATETIME, 
                vote MEDIUMINT(1) NOT NULL,
                snippet_id MEDIUMINT(6) UNSIGNED NOT NULL,
                user_id MEDIUMINT(7) UNSIGNED NOT NULL,
                PRIMARY KEY (vt_id), 
                FOREIGN KEY (snippet_id) REFERENCES Snippets(snippet_id), 
                FOREIGN KEY (user_id) REFERENCES Users(user_id));
            """
    run_query(query, True)

    # Comments
    query = """
            CREATE TABLE IF NOT EXISTS Comments (
                comment_id MEDIUMINT(6) UNSIGNED NOT NULL AUTO_INCREMENT, 
                date_added DATETIME NOT NULL,
                snippet_id MEDIUMINT(6) UNSIGNED NOT NULL,
                user_id MEDIUMINT(7) UNSIGNED NOT NULL, 
                comment TEXT NOT NULL, 
                PRIMARY KEY (comment_id), 
                FOREIGN KEY (snippet_id) REFERENCES Snippets(snippet_id), 
                FOREIGN KEY (user_id) REFERENCES Users(user_id));
            """
    run_query(query, True)

    # Downloads
    query = """
            CREATE TABLE IF NOT EXISTS Downloads (
                download_id MEDIUMINT(6) UNSIGNED NOT NULL AUTO_INCREMENT, 
                date_added DATETIME, 
                snippet_id MEDIUMINT(6) UNSIGNED NOT NULL,
                user_id MEDIUMINT(7) UNSIGNED NOT NULL,
                PRIMARY KEY (download_id), 
                FOREIGN KEY (snippet_id) REFERENCES Snippets(snippet_id), 
                FOREIGN KEY (user_id) REFERENCES Users(user_id));
            """
    run_query(query, True)


def insert_unknown_user():
    # Unknown User
    query = """
            INSERT IGNORE INTO Users( 
                username,
                password)
            VALUES('Unknown User', 0);
            """
    run_query(query, True)


def insert_query(query, insert_string):
    """Generic insert query"""
    try:
        cursor.execute(query, insert_string)
        cnx.commit()

    except mysql.connector.Error as err:
        output(TerminalColors.FAIL + "ERROR: unable to fetch data. ##{}".format(err) + TerminalColors.ENDC, 'Error')
        output(TerminalColors.FAIL + "While running query: '%s' '%s'" % (query, TerminalColors.ENDC), 'Error')
        return


def insert_user(username, password):
    """Create insert query to add a user to database"""
    # Create insert string
    insert_string = (username, password)

    # Insert User
    query = """
            INSERT IGNORE INTO Users( 
                username,
                password)
            VALUES(%s, %s);
            """
    insert_query(query, insert_string)


def insert_snippet(title, snippet, explanation, user_id):
    """Create insert snippet to add to snippet database"""
    # Create insert string
    insert_string = (title, snippet, explanation, user_id)

    # Create query
    query = """
            INSERT IGNORE INTO snippets( 
                title,
                snippet,
                explanation,
                date_added,
                user_id
                )
            VALUES(%s, %s, %s, NOW(), %s);
            """
    # Check if explanation is empty
    if not explanation:
        # Create insert string
        insert_string = (title, snippet, user_id)
        # Create query
        query = """
                INSERT IGNORE INTO snippets( 
                    title,
                    snippet,
                    date_added,
                    user_id
                    )
                VALUES(%s, %s, NOW(), %s);
                """

    else:
        # Create insert string
        insert_string = (title, snippet, explanation, user_id)
        # Create query
        query = """
                INSERT IGNORE INTO snippets( 
                    title,
                    snippet,
                    explanation,
                    date_added,
                    user_id
                    )
                VALUES(%s, %s, %s, NOW(), %s);
                """
    insert_query(query, insert_string)


def insert_tag(tag_name, tag_type):
    """Create insert query to add a tag to the database"""
    # Create insert string
    insert_string = (tag_name, tag_type)

    # Create query
    query = """
            INSERT IGNORE INTO Tags( 
                tag_name,
                type)
            VALUES(%s, %s);
            """
    insert_query(query, insert_string)


def insert_tag_snippet(info):
    """Create insert query to add a tag_to_snippets to the tag_to_snippets database"""
    # Create insert string
    insert_string = (info['tag_id'], info['snippet_id'])

    # Create query
    query = """
            INSERT IGNORE INTO tags_snippet( 
                tag_id,
                snippet_id)
            VALUES(%s, %s);
            """
    insert_query(query, insert_string)


def insert_vote(info):
    """Create insert query to add a vote on snippet to database"""
    # Create insert string
    insert_string = (info['vote'], info['snippet_id'], info['user_id'])

    # Create query
    query = """
            INSERT IGNORE INTO Votes( 
                date_added, 
                vote,
                snippet_id, 
                user_id)
            VALUES(NOW(), %s, %s, %s);
            """
    insert_query(query, insert_string)


def insert_comment(info):
    """Create insert query to add a comment on a snippet to database"""
    # Create insert string
    insert_string = (info['snippet_id'], info['user_id'], info['comment'])

    # Create query
    query = """
            INSERT IGNORE INTO Comments( 
                date_added,
                snippet_id,
                user_id, 
                comment)
            VALUES(NOW(), %s, %s, %s);
            """
    insert_query(query, insert_string)


def insert_download(info):
    """Create insert query to add a download record to database"""
    # Create insert string
    insert_string = (info['snippet_id'],
                     info['user_id'])

    # Insert User
    query = """
            INSERT IGNORE INTO Downloads( 
                date_added,
                snippet_id,
                user_id)
            VALUES(NOW(), %s, %s);
            """
    insert_query(query, insert_string)


def insert_snippet_search(snippet_search_info):
    """Create insert query to add a tag to the database"""
    # Create insert string
    insert_string = (snippet_search_info['snippet_id'], snippet_search_info['search_text'])

    # Create query
    query = """
            INSERT IGNORE INTO Snippet_Search( 
                snippet_id,
                search_text)
            VALUES(%s, %s);
            """
    insert_query(query, insert_string)


def collect_last_snippet_id():
    """Returns the snippet id of the most recent snippet"""
    query = """
            SELECT MAX(snippet_id) FROM Snippets;
            """
    return run_query(query, no_results=False)


def update_tags(tags):
    """Function updates the tags table if new tags have been provided
     Input:
        - tags: List of dictionaries. Each element in list has the tag_name and type
     """
    types = ["Language", "Library", "Topic"]
    # Insert each tag into the tag table
    for index, type_ in enumerate(types):
        for tag in tags[index]:
            insert_tag(tag, type_)


def collect_tag_id(tag_name, type_):
    """Function returns the tag_id of a particular tag"""
    query = """
            SELECT tag_id FROM Tags 
            WHERE tag_name = '{}' AND type = '{}';
            """.format(tag_name, type_)
    return run_query(query, False)


def update_tag_snippet(snippet_id, tag_ids):
    """Function updates tags_snippet table.
    Inputs:
        - snippet_id: the snippet updating for
        - tag_ids: list of tags to update"""
    for tag_id in tag_ids:
        tag_info = dict({'tag_id': tag_id, 'snippet_id': snippet_id})
        insert_tag_snippet(tag_info)


def collect_tag_ids(tags):
    """Function gets in input the tag info of a snippet and outputs a list of tag_ids"""
    tag_ids = []

    types = ["Language", "Library", "Topic"]
    # Insert each tag into the tag table
    for index, type_ in enumerate(types):
        for tag in tags[index]:
            try:
                tag_ids.append(collect_tag_id(tag, type_)[0][0])
            except IndexError:
                pass

    return tag_ids


def remove_stop_words(input_string):
    """Return input string but with stop words removed"""
    stop_words = set(stopwords.words('english'))

    word_tokens = word_tokenize(input_string)

    filtered_string = ' '.join([w for w in word_tokens if w not in stop_words])

    return filtered_string


def create_snippet_search_info(title, snippet, explanation, snippet_id, tags):
    """Function returns a string containing all info for insertion into the snippet search table
        Inputs:
        - snippet_info: Dictionary with parameters 'title', 'snippet', 'explanation'
        'user_id'
        - tags_info: List of dictionaries. Each element in list has the tag_name and type
        - snippet_id: the id of the snippet updating for
    """
    search_text = [title, snippet, explanation]
    tags = [item.strip() for sublist in tags for item in sublist]
    # tags = [tag for tag in tags_info]
    search_text.extend(tags)
    search_text = ' '.join(search_text)
    search_text = remove_stop_words(search_text.lower())
    snippet_search_info = dict({'snippet_id': snippet_id, 'search_text': search_text})

    return snippet_search_info


# def add_snippet(snippet_info, tags_info):
def add_snippet(title, snippet, explanation, user_id, tags_info):
    """Function updates the snippet, snippet_search, tags and tags_id table with the info from a
    new snippet.
    Inputs:
        - snippet_info: Dictionary with parameters 'title', 'snippet', 'explanation'
        'user_id'
        - tags_info: List of dictionaries. Each element in list has the tag_name and type
    """
    # Step 1 - Update snippet table and collect snippet id
    insert_snippet(title, snippet, explanation, user_id)
    snippet_id = collect_last_snippet_id()[0][0]

    # Step 2 - Update snippet search table
    snippet_search_info = create_snippet_search_info(title, snippet, explanation, snippet_id, tags_info)
    insert_snippet_search(snippet_search_info)

    # Step 3 - Update tags table (if new tags exist)
    update_tags(tags_info)

    # Step 4 - Update tags_snippet table
    tag_ids = collect_tag_ids(tags_info)
    update_tag_snippet(snippet_id, tag_ids)


# tests
# sql_create_db_if_doesnt_exist()
#
# insert_user('Gilad', '123456')
#
# tags = [['Python'], ['Flask'], ['Web development']]
# add_snippet('snippet 0',
#                'hello database',
#                'bla bla',
#             datetime.datetime.now(),
#                '1',
#             tags)


# snippet_info = {'title': 'snippet 0', 'snippet': 'hello database', 'explanation': 'bla bla',
#                 'date_added': datetime.datetime.now(), 'user_id': '1'}
# insert_snippet(snippet_info)
#
# tag_info = {'tag_name': 'Best', 'type': 'text'}
# insert_tag(tag_info)
#
# tag_snippet_info = {'tag_id': 1, 'snippet_id': 1}
# insert_tag_snippet(tag_snippet_info)
#
# vote_info = {'date_added': datetime.datetime.now(), 'vote': '1',
#              'snippet_id': 1, 'user_id': 1}
# insert_vote(vote_info)
#
# comment_info = {'date_added': datetime.datetime.now(), 'snippet_id': 1,
#                 'user_id': 1, 'comment': 'bla bla bla'}
# insert_comment(comment_info)
#
# snippet_search_info = {'snippet_id': 1, 'search_text': 'snippet 0 python hello database'}
# insert_snippet_search(snippet_search_info)
# download_info = {'date_added': datetime.datetime.now(), 'snippet_id': '4',
#                      'user_id': 2}
# insert_download(download_info)
