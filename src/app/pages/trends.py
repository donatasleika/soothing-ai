import numpy as np
import pandas as pd
from PIL import Image
from word_cloud.wordcloud import WordCloud, STOPWORDS

from nicegui import ui
from ..database.mongodb_db import Read


ROUTE_PATIENT_PAGE = f'/{normalized_name}/trends/{{patient_name}}'

def register_trends_ui():
    @ui.page(ROUTE_PATIENT_PAGE)
    def word_cloud(patient_name: str):
        pass


    def trend_chart(patient_name: str):
        pass





