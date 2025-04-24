#!/usr/bin/env python
# coding: utf-8

# In[9]:


import requests
from datetime import datetime

def get_hijri_date(date):
    """
    Convert a Gregorian date (YYYY-MM-DD) to an Islamic (Hijri) date and get the next Islamic month.

    :param georgian_date: str, Gregorian date in 'YYYY-MM-DD' format
    :return: dict, Hijri date details including next Islamic month
    """
    try:
        # Convert date from YYYY-MM-DD to DD-MM-YYYY for API
        converted_date =date

        # API URL with formatted date
        url = f"https://api.aladhan.com/v1/gToH/{converted_date}?calendarMethod=UAQ"

        # Send GET request
        response = requests.get(url)
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()  # Convert response to JSON

            # Extract Hijri date details
            hijri_date = data["data"]["hijri"]["date"]  # Example: "28-08-1446"
            hijri_month = data["data"]["hijri"]["month"]["en"].upper()  # Convert to uppercase
            hijri_day = data["data"]["hijri"]["day"]  # Example: "28"
            hijri_year = hijri_date.split('-')[2]  # Convert year to integer

            # Get current Hijri month number
            hijri_month_number = data["data"]["hijri"]["month"]["number"] # Example: 8 for Sha'ban

            # List of Islamic months in uppercase
            ISLAMIC_MONTHS = [
                "MUHARRAM", "SAFAR", "RABI UL AWWAL", "RABI US SANI",
                "JUMADI UL-AWWAL", "JUMADI US SANI", "RAJAB", "SHABAN",
                "RAMADAN", "SHAWWAL", "ZUL-QADDAH", "ZUL-HIJJAH"
            ]

            # Calculate next Islamic month
            next_hijri_month = ISLAMIC_MONTHS[hijri_month_number % 11]  # Modulo to cycle months  
            imonth = ISLAMIC_MONTHS[hijri_month_number-1]

#                 If next month is MUHARRAM, increment the Hijri year
            if next_hijri_month == "MUHARRAM":
                hijri_year += 1

            return {
                "hijri_year": hijri_year,
                "month_num" : hijri_month_number-1
            }
        else:
            return {"error": "Failed to fetch Hijri date"}

    except Exception as e:
        return {"error": str(e)}


# In[10]:


def downloader(date):
    
    # Parse the date
    date_obj = datetime.strptime(date, "%d-%m-%Y")

    # Format as "M-dd-YYYY" with dashes
    formatted_date = date_obj.strftime("%#m-%d-%Y")  # Use %#m on Windows

    names = ["muh","sfr","rba","rbt","jmo","jmt","rjb","shb","rmd","shw","zqd","zhj"]
    num =  get_hijri_date(date)["month_num"]    
    year = get_hijri_date(date)["hijri_year"]
    code = names[num]
    url = f"https://moonsighting.com/visibilitycurves/{year}{code}_{formatted_date}.gif"

    # Set the filename to save the image
    filename = f"{formatted_date}.gif"

    # Download the image
    response = requests.get(url)

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Image successfully downloaded as {filename}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

