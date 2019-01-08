from python.snippit_sql import run_query_to_json as run_query_to_json
from python.snippit_sql import run_query as run_query
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


SQL_SEARCH = """
    SELECT
        snip.snippet_id,
        title,
        snippet,
        explanation,
        date_added as date,
        u.user_id,
        username as user,
        IFNULL(votes, 0) as votes,
        IFNULL(downloads, 0) as downloads,
        IFNULL(comments, 0) as comments
    FROM Snippets snip
    JOIN (
        SELECT snippet_id, MATCH(search_text) AGAINST('%USER_SEARCH%') as relevancy
        FROM Snippet_Search
        WHERE MATCH(search_text) AGAINST('%USER_SEARCH%')
    ) srch
    ON snip.snippet_id = srch.snippet_id
    JOIN Users u
    ON snip.user_id = u.user_id
    LEFT JOIN (SELECT snippet_id, sum(vote) as votes 
            FROM Votes
            GROUP BY snippet_id) v
    ON v.snippet_id = snip.snippet_id
    LEFT JOIN (SELECT snippet_id, count(*) as downloads 
        FROM Downloads
        GROUP BY snippet_id) d
    ON d.snippet_id = snip.snippet_id
    LEFT JOIN (SELECT snippet_id, count(*) as comments
        FROM Comments
        GROUP BY snippet_id) c
    ON c.snippet_id = snip.snippet_id
    GROUP BY
        snip.snippet_id,
        title,
        snippet,
        explanation,
        date_added,
        u.user_id,
        username
    ORDER BY srch.relevancy DESC
"""

SQL_GET_TAGS = """
    SELECT tag_name
    FROM tags t
    JOIN Tags_Snippet ts
    ON t.tag_id = ts.tag_id
    WHERE ts.snippet_id = %SNIPPET_ID%
    AND t.type = '%TYPE%'
"""

# Get css
# print(HtmlFormatter(style='tango').get_style_defs('.highlight'))


def search_snippet(query):
    results = run_query_to_json(SQL_SEARCH.replace('%USER_SEARCH%', query))
    for result in results:
        result['languages'] = run_query(SQL_GET_TAGS.replace('%SNIPPET_ID%', str(result['snippet_id'])).replace('%TYPE%', 'Language'))[0]
        result['frameworks'] = run_query(SQL_GET_TAGS.replace('%SNIPPET_ID%', str(result['snippet_id'])).replace('%TYPE%', 'Library'))[0]
        result['topics'] = run_query(SQL_GET_TAGS.replace('%SNIPPET_ID%', str(result['snippet_id'])).replace('%TYPE%', 'Topic'))[0]
        result['snippet_html'] = highlight(result['snippet'], PythonLexer(), HtmlFormatter(style='tango'))

    return results
