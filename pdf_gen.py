#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#installing a package
#!pip3 install <package name> 


# In[ ]:


# 2. remove jiwani hard coding apply any condition so that jiwani will be selected automatically...........done
# get islamic month and year from internet and put as an input
# 3. Make a method to process all files according to their Islamic Month name and Islamic date automatically
# 4. Calculate Parameters and recheck its accuracy with data 
# 5. Make GUI interface
# 6. Make it customizable code and reusable code apply OOP


# In[1]:


import pandas as pd
import math 
import os
from fpdf import FPDF
import webbrowser
from datetime import datetime
import requests


# In[3]:


class MoonCalc:
    def __init__(self, file_path, date, Month, year, dst):
        self.path = file_path.replace('"', '')
        self.date = date.replace('"', '')
        self.month = Month.replace('"', '')
        self.year = year.replace('"', '')
        self.dst = dst.replace('"', '') if dst else None

    def data(self, *args):
        def set_axis(df):
            columns = ["year", "h", "cd", "conj", "f", "wk", "mon", "day", "set", "Saz", "age",
                       "Alt", "Maz", "dz", "Mag", "El", "mset", "lag", "best", "cat"]
            df.columns = columns
            return df

        def illum(a):
            return round(50 * (1 - math.cos(math.radians(a))), 1)

        try:
            df = pd.read_fwf(os.path.join(args[0], args[1]))
        except Exception as e:
            print(f"Error loading file {args[1]}: {e}")
            return pd.DataFrame()

        df = set_axis(df)
        dfa = df.drop(['f', 'Mag', 'wk'], axis=1)
        dfs = dfa.loc[:, :'conj']
        dfd = dfa.loc[:, 'mon':'cat']

        dfd = dfd.bfill()
        dfs = dfs.ffill()

        dfg = dfs.combine_first(dfd)
        dfg.drop_duplicates(inplace=True)
        dfg.dropna(inplace=True)

        for x in ['conj', 'set', 'mset', 'best']:
            dfg[x] = dfg[x].replace(' ', ':', regex=True)

        for x in ['cd', 'day', 'year', 'lag', 'Alt', 'Saz', 'dz', 'Maz']:
            dfg[x] = dfg[x].astype(int).astype(str)

        dfg['mon'] = dfg['mon'].str[:3]
        dfg['h'] = dfg['h'].str[:3]
        dfg['date'] = pd.to_datetime(dfg['day'] + dfg['mon'] + dfg['year'], format='%d%b%Y')
        dfg.set_index('date', inplace=True)

        dfg['conj_time'] = pd.to_datetime(dfg['cd'] + dfg['h'] + dfg['year'] + ' ' + dfg['conj'])

        dfg['Station'] = args[1].split('.', 1)[0] if args else self.loc

        dfg['El'] = dfg['El'].astype(int)
        dfg['ilum'] = dfg['El'].apply(illum)

        return dfg

    def sort(self, *args):
        df = self.data(args[0], args[1])
        if df.empty:
            return pd.DataFrame()

        df = df[['Station', 'set', 'lag', 'Alt', 'Saz', 'dz', 'El', 'ilum', 'cat', 'age', 'conj_time']]
        df['Station'] = df['Station'].astype("category").cat.set_categories(sorted(df['Station'].unique()))
        return df

    def all_files(self):
        df = pd.DataFrame()
        if os.path.exists(self.path):
            for root, dirs, files in os.walk(self.path):
                for filename in files:
                    d = self.sort(root, filename)
                    if not d.empty:
                        df = pd.concat([df, d], ignore_index=False)
            return df
        else:
            print("Directory does not exist")
            return df

    def calculate(self):
        dfs = self.all_files()
        dfd = pd.DataFrame()
        if not dfs.empty:
            dfs['date'] = dfs.index
            dfs.set_index('date', inplace=True)
            dfs.index = pd.to_datetime(dfs.index)

            target_date = pd.to_datetime(self.date)
            if target_date in dfs.index:
                daily_df = dfs.loc[target_date]
                daily_df = daily_df.sort_values('Station')

                dfd = daily_df.loc[:, :'cat']
                dfd['Station'] = dfd['Station'].astype(str) + " (" + dfd['set'].astype(str) + ")"
                dfd.drop(columns="set", inplace=True)
                

                dfd.rename(columns={
                    'Station': 'STATION(Sunset)',
                    'lag': 'LAG TIME(Minutes)',
                    'Alt': 'MOON ALTITUDE(Degrees)',
                    'Saz': 'SUN_AZIMUTH(Degrees)',
                    'dz': 'DAZ(Degrees)',
                    'El': 'ELONGATION(Degrees)',
                    'ilum': 'ILLUMINATION(%)',
                    'cat': 'CRITERION'
                }, inplace=True)

        return dfd

    def Select_city(self):
        dfs = self.all_files()
        if dfs.empty:
            return {}

        dfs.index = pd.to_datetime(dfs.index)
        target_date = pd.to_datetime(self.date)

        if target_date not in dfs.index:
            print("Max df is not selected")
            return {}

        df_today = dfs.loc[target_date].sort_values("Station")
        df_today = df_today[df_today["set"] == df_today["set"].max()]

        return {
            "age": df_today.age.values[0].split(" "),
            "dt": df_today.conj_time.dt.strftime("%d-%m-%Y").values[0],
            "tm": df_today.conj_time.dt.strftime("%H:%M:%S").values[0],
            "city": df_today.Station.values[0]
        }
    
    def pdf(self):
        Format = "Arial"        
        data = {'Station':'  STATION    (Sunset)','lag':'LAG TIME  (Min)','Alt':'MOON ALTITUDE   (Deg)', 
                                      'Saz':'SUN_AZIMUTH (Deg)',
                                      'dz':'DAZ   (Deg)  ',
                                      'El':'ELONGATION  (Deg)','ilum':'ILLUMINATION  (%)',
                                      'cat':'CRITERION   '}
        df = pd.DataFrame()
        df = self.calculate()
        if df.empty == True: return print("Date not Found") 
        Date = datetime.strptime(self.date,"%Y-%m-%d")
        Date =Date.strftime("%d-%m-%Y")
        pdf = PDF(self.path, self.date, self.month, self.year , self.dst ,'L', 'mm', 'A4')
        pdf.add_page()
        pdf.set_font(Format,'B',11)
        li = []
        for x in data.values():li.append(x)
        width = [40,30,38,33,22,31,33,26,40,40]
        start = 25
        pdf.x = start
        offset = pdf.x + width[0]
        sx = pdf.x
        i = 0
        top = 40
        pdf.y = top
        for head in li:    
            pdf.multi_cell(width[i],7,head,border = 1,align = "C")
            # Reset y coordinate
            pdf.y = top
            # Move to computed offset    
            pdf.x = offset
            i += 1
            offset = offset+ width[i]
        h = pdf.font_size * 2.5
        pdf.y = 54
        pdf.set_font(Format,'',11)
        for index, row in df.iterrows():
            i = 0
            pdf.x = start
            for data in row.values:
                pdf.cell(width[i], h, str(data),border = 1,align='C') # write each data for the row in its cell
                i +=1  
            pdf.ln()      
        ls = ["(A)  Easily visible",
                         "(B) Visible under perfect conditions",
                         "(C)  May need optical aid to find the crescent Moon",
                        "(D)  Will need optical aid to find the crescent Moon",
                        "(E)  Not visible with a telescope",
                        "(F)  Not visible, below the Danjon limit"]
        
        pdf.ln()
        pdf.set_font(Format, 'BU', 12)
        h = 5
        pdf.ln()
        pdf.set_font(Format, '', 11)
        if self.dst:
            pdf.output(self.dst+"\\"+Date+".pdf",'F')
            webbrowser.open_new(self.dst+"\\"+Date+'.pdf')
        else:
            pdf.output(Date+'.pdf','F') # save pdf
            webbrowser.open_new(Date+'.pdf') # open pdf in browser  


# In[4]:


class PDF(FPDF, MoonCalc):
    def __init__(self, file_path, date, Month, year, dst, *args, **kwargs):
        # Initialize FPDF
        FPDF.__init__(self, *args, **kwargs)  
        
        # Initialize MoonCalc with required parameters
        MoonCalc.__init__(self, file_path, date, Month, year, dst)

    
    def footer(self):
        self.set_y(-27)
        Format = "Arial"
        
        # Visibility Criterion
        ls = [
            "(A)  Easily visible",
            "(B)  Visible under perfect conditions",
            "(C)  May need optical aid to find the crescent Moon",
            "(D)  Will need optical aid to find the crescent Moon",
            "(E)  Not visible with a telescope",
            "(F)  Not visible, below the Danjon limit"
        ]

        self.set_font(Format, 'BU', 12)
        self.cell(297, 5, "Visibility Criterion:", ln=1, align='L')
        self.ln(2)

        self.set_font(Format, '', 11)
        sp = "  "
        self.multi_cell(280, 5, txt=sp.join(ls), align='L')
        
        self.set_font(Format, 'I', 8)
        self.cell(270, 10, 'Computer Generated', 0, 0, 'R')

        self.ln(5)

    def header(self):
        data = self.Select_city()
        age = data["age"]
        dt = data["dt"]
        tm = data["tm"]
        city = data["city"]

        Format = "Arial"        

        Date = datetime.strptime(self.date, "%Y-%m-%d")
        Date = Date.strftime("%d-%m-%Y")

        self.set_font(Format, 'B', 16)
        h = 7
        w = 297
        self.cell(w, h, txt="PARAMETERS OF THE NEW MOON " + self.month + " " + self.year, ln=1, align='C')
        self.cell(w, h, txt="AT THE TIME OF SUNSET ON " + Date, ln=1, align='C')
        self.cell(w, h, txt=f"(Conjunction on {dt} {tm} PST) ", ln=1, align='C')
        self.cell(w, h, txt = f"Moon Age at the time of Sunset on {Date} ({city}): {age[0]} hrs {age[1]} mins",ln = 1, align = 'C')
        self.ln()



# In[5]:


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
            hijri_year = int(hijri_date.split('-')[2])  # Convert year to integer
            
            # Get current Hijri month number
            hijri_month_number = data["data"]["hijri"]["month"]["number"]  # Example: 8 for Sha'ban
            
            # List of Islamic months in uppercase
            ISLAMIC_MONTHS = [
                "MUHARRAM", "SAFAR", "RABI UL AWWAL", "RABI US SANI",
                "JUMADI UL-AWWAL", "JUMADI US SANI", "RAJAB", "SHABAN",
                "RAMADAN", "SHAWWAL", "ZUL-QADDAH", "ZUL-HIJJAH"
            ]
            
        # Calculate next Islamic month
            if hijri_month_number == 12:
                imonth = ISLAMIC_MONTHS[0] # Modulo to cycle months 
                hijri_year += 1
            else:
                imonth = ISLAMIC_MONTHS[hijri_month_number-1]

            
            return {
                "hijri_day": hijri_day,
                "hijri_month": imonth,
                "hijri_year": str(hijri_year)
            }
        else:
            return {"error": "Failed to fetch Hijri date"}
    
    except Exception as e:
        return {"error": str(e)}


# In[11]:


def generate_pdf(date,path="D:/code/Data_2035", dst='D:/Output'):
#     date = "28-02-2025"
    hijri_data = get_hijri_date(date)
    month = hijri_data['hijri_month']
    year = hijri_data['hijri_year']
    date_obj = datetime.strptime(date, "%d-%m-%Y")    
    # Convert to YYYY-MM-DD format
    converted_date = date_obj.strftime("%Y-%m-%d")
    Moon = MoonCalc(path,converted_date,month,year +" AH",dst)
    Moon.pdf()
    
generate_pdf("28-04-2025")

