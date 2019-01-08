from python.snippit_sql import remove_stop_words as remove_stop_words
import pickle
model = pickle.load(open('python/w2v_model.sav', 'rb'))


def get_similar_words(model, word):
    return model.wv.most_similar(positive=word)


def select_top_words(similar_words, search_words, threshold):
    for element in similar_words:
        if element[1] > threshold:
            search_words.append(element[0])
        else:
            break
    return search_words


def suggested_search(search_text):
    """Uses trained NLP model to suggest similar searches based on given search text"""
    threshold = 0.6
    global model

    search_text = remove_stop_words(search_text)
    tmp_search = search_text.split()

    new_search = []
    for word in tmp_search:
        similar_words = get_similar_words(model, word)
        new_search = select_top_words(similar_words, new_search, threshold)

    new_search = list(set(new_search))
    new_search = ' '.join(new_search)

    return new_search + ' ' + search_text
