from bs4 import BeautifulSoup as bs
from flask import Flask,render_template,request
import requests
import pandas as pd
import pymongo
from urllib.request import urlopen as uReq


app=Flask(__name__)

@app.route('/',methods=['GET'])
def routetowebpage():
    return render_template('index.html')

@app.route('/weather',methods=['GET','POST'])
def mainlogic():

    if request.method=='POST':
        city=request.form['content'].replace(' ','')
        url = "https://www.timeanddate.com/weather/india/" + city

        uClient = uReq(url)
        page = uClient.read()
        uClient.close()
        soup= bs(page, "html.parser")

        now = soup.find('div', {'class': 'bk-focus__qlook'})



        current_temp = now.find('div', {'class': 'h2'}).text.replace('\xa0', '')



        descriptionbox = now.findAll('p')

        description = []
        for i in descriptionbox:
            description.append(i.text.replace('\xa0', ''))

        focus_info = soup.find('div', {'class': 'bk-focus__info'})

        table = focus_info.select('table', {'class': 'table table--left table--inner-borders-rows'})

        di = []
        for i in table[0].findAll('th'):
            di.append(i.text)


        inf = []
        for i in table[0].findAll('td'):
            inf.append(i.text.strip().replace('\xa0', ''))


        df = pd.DataFrame(columns=di)

        df.loc['Data'] = inf



        date = df['Current Time: '].apply(lambda x: x[0:2])

        forecastblock = soup.find('div', {'class': 'eight columns'})

        heading = forecastblock.h2.text

        tablebody = forecastblock.div.table.tbody

        tableheader = forecastblock.div.table.thead

        headerlist = tableheader.find_all('tr')


        mainheader = []
        for i in headerlist[0].find_all('th'):
            mainheader.append(i.text.replace('\xa0', ''))

        dayheader = []
        for i in headerlist[1].find_all('th'):
            dayheader.append(i.text.replace('\xa0', ''))




        rows = tablebody.find_all('tr')



        df2 = pd.DataFrame(columns=dayheader[1:])

        index=''
        for item in rows:
            li = []
            index = item.th.text
            dataitems = item.find_all('td')
            for item1 in dataitems:
                li.append(item1.text.replace('\xa0', ''))
            df2.loc[index] = li

        c_url = url + '/climate'

        tags = requests.get(c_url)
        soup1 = bs(tags.text, 'html.parser')

        tablebox = soup1.find('table', {'class': 'tb-minimal tb-vspace fw mgt15'})

        table_rows = tablebox.tbody.find_all('tr')


        column = []
        data = []
        for item in table_rows:
            column.append(item.th.text)
            data.append('/' + item.td.text.replace('\xa0', ''))
        df3 = pd.DataFrame(columns=column)
        df3.loc['climate'] = data

        df2.drop(index='Forecast',inplace=True)


        df2=df2.transpose()

        weather_dict=df.to_dict('records')
        weather_dict[0]['temp']=current_temp
        weather_dict[0]['description']=description

        forecast_dict=df2.to_dict('records')

        climate_dict = df3.to_dict('records')


        client = pymongo.MongoClient("mongodb+srv://manas:mongodb@cluster0.hgmxp9o.mongodb.net/?retryWrites=true&w=majority")
        banglore = client.test
        banglore = client['csv']
        collw = banglore['w1']
        collf = banglore['f1']
        collc = banglore['b1']


        collw.insert_one(weather_dict[0])

        collc.insert_one(climate_dict[0])

        collf.insert_many(forecast_dict)
        reviews=forecast_dict
        print(reviews)
        return render_template('result.html',reviews=reviews)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8002, debug=True)
    # app.run(debug=True)






