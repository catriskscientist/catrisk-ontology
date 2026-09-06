# -*- coding: utf-8 -*-
"""
utils.py -- date parsing helpers for the knowledge-graph build.

@author: Sashi Kanth Tadinada, PhD
"""

import pandas as pd
from datetime import datetime

MONTH_MAP = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
    "JUNE":6,
    "JULY":7
}

# Function to clean and parse dates
def clean_and_parse_date(date_str):
    # Normalize the date string by adding a space after the month if missing
    dt = date_str.strip().upper().replace(" ","")
    year = int(dt[-4:])
    monthday = dt[:-4]
    month = ''.join(char for char in monthday if char.isalpha())
    day = int(''.join(char for char in monthday if char.isdigit()))
    monthn = MONTH_MAP[month]
    
    return datetime(year, monthn, day)