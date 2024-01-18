from config import create_app
from celery import shared_task
import requests
import os
import bs4

flask_app = create_app()
celery_app = flask_app.extensions["celery"]

positive_words_path = "./assets/positive_words.txt"
negative_words_path = "./assets/negative_words.txt"
script_dir = os.path.dirname(__file__)
abs_positive_file_path = os.path.join(script_dir, positive_words_path)
abs_negative_file_path = os.path.join(script_dir, negative_words_path)

class Utils:
    positive_words_path = "./assets/positive_words.txt"
    negative_words_path = "./assets/negative_words.txt"
    script_dir = os.path.dirname(__file__)
    abs_positive_file_path = os.path.join(script_dir, positive_words_path)
    abs_negative_file_path = os.path.join(script_dir, negative_words_path)

    cashed_urls = []
    cashed_urls_num = 10

    @staticmethod
    def article_scraper(url):
        textual_data = ""
        response = requests.get(url)
        if response is not None:
            html = bs4.BeautifulSoup(response.text, 'html.parser')
            paragraphs = html.select("p")
            textual_data = " ".join([para.text for para in paragraphs[0:5]])
        return textual_data.split(" ")

    @staticmethod
    def article_sentiment_analysis(url, path_pos, path_neg):
        file_pos = open(path_pos, "r")
        file_pos_content = file_pos.read()
        found_positive_words = file_pos_content.split('\n')
        file_neg = open(path_neg, "r")
        file_neg_content = file_neg.read()
        found_negative_words = file_neg_content.split('\n')

        article_words = Utils.article_scraper(url)
        set_pos_words, set_neg_words, set_article_words = set(found_negative_words), set(found_positive_words), set(article_words)
        num_pos_words = len(set_pos_words.intersection(set_article_words))
        num_neg_words = len(set_neg_words.intersection(set_article_words))

        if num_pos_words == num_neg_words or num_pos_words + 1 == num_neg_words or num_pos_words == num_neg_words + 1:
            return url.split("/")[-1], "neutral"
        if num_pos_words > num_neg_words:
            return url.split("/")[-1], "positive"

        return url.split("/")[-1], "negative"

    @staticmethod
    def cashing_urls():
        for i in range(Utils.cashed_urls_num):
            Utils.cashed_urls.append(requests.get("https://en.wikipedia.org/wiki/Special:Random").url)

        print(Utils.cashed_urls_num, 'urls cashed')

@shared_task(ignore_result=False)
def long_running_task(iterations, urls, path1, path2) -> list:
    result = []

    for i in range(iterations):
        result.append(Utils.article_sentiment_analysis(urls[i], path1, path2))

    return result
