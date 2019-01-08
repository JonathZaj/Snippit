from python.snippit_sql import add_snippet as add_snippet
from python.snippit_sql import insert_user as insert_user


def populate_db():
    # Add users
    insert_user('Gilad', '123456') # 1
    insert_user('Jeremey', '123456') # 2
    insert_user('Guy', '123456') # 3
    insert_user('Anzor', '123456') # 4
    insert_user('Jonathan', '123456') # 5

    # Add snippets - 2 per user
    tags = [['Python'], ['Flask'], ['Web development']]
    add_snippet('Flask Web Server',
                """
from flask import Flask
app = Flask(__name__)

@app.route('/')
def Index():
    return 'Index Page'
                """,
                'Code to get a flask server running with a simple index page',
                '1',
                tags)

    tags = [['Python'], ['Flask'], ['Web development']]
    add_snippet('Flask Get Parameters',
                """
from flask import request

@app.route('/my-route')
def my_route():
    page = request.args.get('page', default = 1, type = int)
    filter = request.args.get('filter', default = '*', type = str) 
                """,
                'Code to get a flask parameters',
                '1',
                tags)

    tags = [['Python'], ['Collections'], ['Python']]
    add_snippet('Count frequency of elements in a list',
                """
from collections import Counter
x = [1,1,1,1,2,2,2,2,3,3,4,5,5]

counter = Counter(x)
                """,
                'Code to get the frequency of elements in a list',
                '2',
                tags)

    tags = [['Python'], ['Collections'], ['Python']]
    add_snippet('Get most frequent elements in a list',
                """
from collections import Counter
x = [1,1,1,1,2,2,2,2,3,3,4,5,5]

counter = Counter(x)
print(counter.most_common(3))
# [(1, 4), (2, 4), (3, 2)]
                """,
                'Code to get the most frequent of elements in a list',
                '2',
                tags)

    tags = [['Python'], ['xgboost'], ['Data Science']]
    add_snippet('Implement an xgboost algorithm',
                """
import xgboost as xgb

xgb.XGBClassifier()

model = model.fit(X_train, y_train)
y_pred = model.predict(X_test)
                """,
                'Code to get predictions from an xgboost algorithms',
                '3',
                tags)

    tags = [['Python'], ['nltk'], ['NLP']]
    add_snippet('Remove stop words from a string',
                """
# Might need these top 2 lines if haven't installed stopwords before
# import nltk
# nltk.download('stopwords') 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('english')) 

word_tokens = word_tokenize(input_string)

filtered_string = ' '.join([w for w in word_tokens if w not in stop_words])
                """,
                'Code to generate a string without stop words',
                '3',
                tags)
