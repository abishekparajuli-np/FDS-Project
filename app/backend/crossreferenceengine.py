import requests
import feedparser
import numpy as np
import re
import time
from urllib.parse import urlparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
from sentence_transformers import SentenceTransformer
