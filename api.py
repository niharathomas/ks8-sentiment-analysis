import falcon
import logging
import json

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "<<ADD_KEY_FILE_HERE>>"

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class RequestLogger(object):
    def process_request(self, req, resp):
        logger.info("{} request received... {}".format(req.method, req.uri))


class RequireJSON(object):
    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                "This API only supports responses encoded as JSON.",
                href="http://docs.examples.com/api/json")

        if req.method in ("POST", "PUT"):
            if "application/json" not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    "This API only supports requests encoded as JSON.",
                    href="http://docs.examples.com/api/json")


class Status(object):
    def on_get(self, req, resp):
        """Status check"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = ("Hello World!!")


class SentimentAnalysis(object):
    def on_post(self, req, resp):
        """Return sentiment scores for input sentences"""
        client = language.LanguageServiceClient()

        document = types.Document(
            content=req.media.get("data"),
            type=enums.Document.Type.PLAIN_TEXT)
        annotations = client.analyze_sentiment(document=document)

        # Process results
        response = {}
        score = annotations.document_sentiment.score
        magnitude = annotations.document_sentiment.magnitude
        document_response = {
            "document": {
                "score": score,
                "magnitude": magnitude
            }
        }

        logger.info("Document sentiment analysis: Score: {}, Magnitude: {}".format(
            score, magnitude))
        sentence_response_list =[]
        sentences_response = {
            "sentences" : sentence_response_list
        }
        for index, sentence in enumerate(annotations.sentences):
            sentence_sentiment = round(sentence.sentiment.score, 2)
            sentence_emotional_magnitude = round(
                sentence.sentiment.magnitude, 2)
            pos_or_neg = "positive" if sentence_sentiment >= 0.5 else "negative"

            sentence_response = {
                "sentence": sentence.text.content,
                "score": sentence_sentiment,
                "magnitude": sentence_emotional_magnitude,
                "pos_or_neg": pos_or_neg
            }
            sentence_response_list.append(sentence_response)

            logger.info("Input sentence: {} - has a sentiment score of {} and is {} with an emotional magnitude of {}".format(
                sentence.text.content, sentence_sentiment, pos_or_neg, sentence_emotional_magnitude))

        resp.media = {**document_response, **sentences_response}


# Configure app middleware
app = falcon.API(
    middleware=[
        RequestLogger(),
        RequireJSON(),
    ]
)
logger.info("API is up!!!!")

# Setup resources
status = Status()
sentiment_analysis = SentimentAnalysis()

# Add routes
app.add_route("/status", status)
app.add_route("/analyze", sentiment_analysis)
