import requests, time, os, urllib, csv
from shutil import copyfile
from bs4 import BeautifulSoup as bs
import cv2

'''
觀測時間(hour),ObsTime
測站氣壓(hPa),StnPres
海平面氣壓(hPa),SeaPres
氣溫(℃),Temperature
露點溫度(℃),Td dew point
相對溼度(%),RH
風速(m/s),WS
風向(360degree),WD
最大陣風(m/s),WSGust
最大陣風風向(360degree),WDGust
降水量(mm),Precp
降水時數(hr),PrecpHour
日照時數(hr),SunShine
全天空日射量(MJ/㎡),GloblRad
能見度(km),Visb
紫外線指數,UVI
總雲量(0~10),Cloud Amount

體感溫度(°C)=溫度(°C)-2√風速(公尺/每秒)
AT = Temperature-2*WS**0.5
'''

posNoNameDict = {'富貴角': '084', '基隆': '001', '士林': '011', '大直': '012', '臺北': '014', '松山': '015', '竹子湖': '064', '萬華': '013', '環保署大樓': '303', '三重': '067', '土城': '005', '永和': '070', '汐止': '002', '板橋': '006', '林口': '009', '菜寮': '008', '屈尺': '004', '大坪': '003', '大園': '018', '中壢': '068', '平鎮': '020', '桃園': '017', '龍潭': '021', '觀音': '019', '新竹': '024', '湖口': '022', '三義': '027', '苗栗': '026', '大里': '030', '西屯': '032', '沙鹿': '029', '忠明': '031', '豐原': '028', '竹山': '069', '南投': '036', '埔里': '072', '二林': '035', '彰化': '033', '線西': '034', '斗六': '037', '崙背': '038', '麥寮': '083', '臺西': '041', '雲林旭光': '404', '嘉義': '042', '朴子': '040', '新港': '039', '鹿林山': '082', '安南': '045', '善化': '044', '新營': '043', '臺南': '046', '大寮': '051', '小港': '058', '仁武': '049', '左營': '054', '林園': '052', '前金': '056', '前鎮': '057', '美濃': '047', '楠梓': '053', '鳳山': '050', '橋頭': '048', '高雄': '413', '屏東': '059', '恆春': '061', '潮州': '060', '冬山': '066', '宜蘭': '065', '花蓮': '063', '臺東': '062', '關山': '080', '臺東仁愛': '401', '馬公': '078', '金門': '077', '馬祖': '075', '馬祖東引': '408', '彰化（員林）': '201', '彰化（大城）': '202', '臺南': '203', '屏東（琉球）': '204'}

posnoList = ['001', '002', '003', '004', '005', '006', '008', '009', '011', '012', '013', '014', '015', '017', '018', '019', '020', '021', '022', '024', '026', '027', '028', '029', '030', '031', '032', '033', '034', '035', '036', '037', '038', '039', '040', '041', '042', '043', '044', '045', '046', '047', '048', '049', '050', '051', '052', '053', '054', '056', '057', '058', '059', '060', '061', '062', '063', '064', '065', '066', '067', '068', '069', '070', '072', '075', '077', '078', '080', '082', '083', '084', '201', '202', '203', '204', '303', '401', '404', '408', '413']

# timeList = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']

timeList = ['0000', '0100', '0200', '0300', '0400', '0500', '0600', '0700', '0800', '0900', '1000', '1100', '1200', '1300', '1400', '1500', '1600', '1700', '1800', '1900', '2000', '2100', '2200', '2300']

dateList = ['0101', '0102', '0103', '0104', '0105']
dateList = ['20210103','20210104','20210105','20210106','20210107']

site= "https://airtw.epa.gov.tw/AirSitePic"

def getPics():
    for d in dateList:
        for t in timeList:
            for p in posnoList:
                picname = "{}-{}{}.jpg".format(p,d,t)
                picurl = "{}/{}/{}".format(site,d,picname)
                print(picurl)
                # break
                img = requests.get(picurl).content
                with open(os.path.join('pics',picname),'wb') as f:
                    f.write(img)

def getData():
    print("getData")
    # response = requests.get("https://e-service.cwb.gov.tw/HistoryDataQuery/")
    # print(response)
    url = "https://e-service.cwb.gov.tw/wdps/obs/state.htm"
    # url = "https://google.com"
    # postdata = {'station_no': 467490, 'MIME': 'application/x-www-form-urlencoded; charset=UTF-8'}
    # response = requests.post(url, data = postdata)
    # response = requests.get(url)
    # print(response)
    # return
    data = ''
    with open('data.html','r') as f:
        data = f.read()
    # print(data)
    soup = bs(data, "html.parser")
    # print(soup.prettify())
    # soup = soup.find_all("li")
    soup = soup.find("div",id="existing_station").find_all("tr")
    with open('station_no.csv','w') as f:
        for tr in soup:
            tds = tr.find_all("td")
            if tds:
                print(tds[1].text, tds[0].text)
                f.write("{},{}\n".format(tds[1].text, tds[0].text))
        # print(tds[0], tds[1])
    # print(soup.prettify())

def matchAirAndStation():
    query_site = "https://e-service.cwb.gov.tw/HistoryDataQuery/DayDataController.do?command=viewMain&station={}&stname={}&datepicker={}"
    stationDict = {}
    csvfile= open('station_no.csv','r')
    csvdata = csv.DictReader(csvfile,['name','no'])
    for item in csvdata:
        stationDict[item['name']] = item['no']
    errorcount = 0
    for pos in posNoNameDict:
        try:
            if stationDict[pos]:
                query_stname = urllib.parse.quote(urllib.parse.quote(pos))
                query_stno = stationDict[pos]
                posno = posNoNameDict[pos]
                print(pos, posNoNameDict[pos],stationDict[pos], urllib.parse.quote(urllib.parse.quote(pos)))
                continue
                # print(query_stname, query_stno)
                headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
                url = query_site.format(query_stno, query_stname, '2021-01-01')
                print(url)
                response = requests.get(url, headers=headers, stream=True)
                print(response)
                with open('posdata/{}-2021-01-01.html'.format(), 'w') as f:
                    f.write(response.text)
                '''
                with urllib.request.urlopen(url) as response:
                    html = str(response.read(),'utf-8')
                    # print(type(str(html)))
                    # print(html)
                    # print(html)
                    # print(response.status)
                    with open('station_data.html', 'w') as f:
                        f.write(html)
                    soup = bs(html,'html.parser')
                    soup = soup.find_all("table")
                    print(len(soup))
                    print(soup)
                    # print(soup.prettify())
                    '''
        except Exception as e:
            errorcount += 1
            print("error!",e)
        # break
    # print("errors:", errorcount)
    # print(stationDict)
    # print(stationDict['銅門'])
    # for line in csvdata:
    #     print(line[0], line[1])


def decodeUrl():
    code = "%25E5%25AF%258C%25E8%25B2%25B4%25E8%25A7%2592"
    newcode = urllib.parse.unquote(code) 
    newcode = urllib.parse.unquote(newcode) 
    print(newcode)

def requestAirPicture():
    response = requests.get("https://airtw.epa.gov.tw/ajax.aspx?Target=SitePhoto")
    soup = bs(response.text, "html.parser")
    soup = soup.find_all("li")
    noList = {}
    for li in soup:
        picname =li.img.get("data-original").split('/')[-1] 
        if picname == "pic_error.png":
            # print(li)
            continue
        posname = li.a.get("name")
        posno = picname[0:3]
        # print(posname, posno)
        noList[posname] = posno
    # print(noList)

def parseStationDataHtml():
    csv_header = ['ObsTime','StnPres','SeaPres','Temperature','Td_dew_point','RH','WS','WD','WSGust','WDGust','Precp','PrecpHour','SunShine','GloblRad','Visb','UVI','Cloud_Amount', 'Apparent_Temp']
    path = 'posdata'
    files = os.listdir('posdata/')
    for htmlfile in files:
        htmlfilename = os.path.join(path,htmlfile)
        csvfilename = htmlfilename.split('.')[0].split('/')[1]+'.csv'
        # csvfilename = "{}-{}{}{}".format(csvfilenameUnit[0],csvfilenameUnit[1],csvfilenameUnit[2], csvfilenameUnit[3])
        print(csvfilename)
        with open(htmlfilename, 'r') as f:
            # print(f.read())
            soup = bs(f.read(), 'html.parser')
            soup = soup.find_all("table")[1].find_all("tr")
            with open(os.path.join('posdataCsv',csvfilename), 'w') as f:
                for i, h in enumerate(csv_header):
                    f.write(h)
                    if i < len(csv_header)-1:
                        f.write(',')
                f.write('\n')
                for index,tr in enumerate(soup):
                    if index < 3:
                        continue
                    # if index < 5:
                    if True:
                        tds = tr.find_all("td")
                        # print("\n")
                        for i, td in enumerate(tds):
                            if td.text.startswith("..."):
                                # print("start with ...")
                                f.write("")
                            else:
                                f.write("{}".format(td.text).strip())

                            if i < len(tds)-1:
                                f.write(",")
                        f.write('\n')
        # break

def labelPosPic(toLabelPath):
    toLabelPath = os.path.join('data', toLabelPath)
    path = 'posdataCsv'
    writePath = 'posdataCsv2'
    csv_header = ['ObsTime','StnPres','SeaPres','Temperature','Td_dew_point','RH','WS','WD','WSGust','WDGust','Precp','PrecpHour','SunShine','GloblRad','Visb','UVI','Cloud_Amount', 'Apparent_Temp']
    copied_files = 0
    csvs = os.listdir(path)
    print("csv file number is",len(csvs))
    for csvfile in csvs:
        # print(csvfile)
        label_posno = csvfile.split(".")[0][0:3]
        label_date = csvfile.split(".")[0][3:].replace('-', '')
        print(label_date, label_posno)
        with open(os.path.join(path,csvfile), 'r') as f:
            csvdata = csv.DictReader(f, csv_header)
            # print(csvdata.fieldnames)
            '''
                體感溫度(°C)=溫度(°C)-2√風速(公尺/每秒)
                AT = Temperature-2*WS**0.5
            '''
            for index, line in enumerate(csvdata):
                if index == 0:
                    continue
                try:
                    # AT = "{:.1f}".format(float(line['Temperature'])-2*float(line['WS'])**0.5)
                    AT = round(float(line['Temperature'])-2*float(line['WS'])**0.5)
                    # print(AT, line['Temperature'], line['WS'])
                    label_time = '0000' if line['ObsTime']=='24' else line['ObsTime']+'00'
                    label_image = "{}-{}{}.jpg".format(label_posno,label_date, label_time)
                    # images = os.listdir(os.path.join(toLabelPath,'images'))
                    label_image_path = os.path.join(toLabelPath,'images',label_image)
                    # print(label_image_path)
                    if os.path.exists(label_image_path):
                        print("exist")
                        copied_files += 1
                        # label_AT = str(int(float(AT)*10))
                        label_AT = str(AT)
                        print(label_image_path)
                        print(label_AT)
                        copyfile(label_image_path, os.path.join(toLabelPath,'classes','c{}'.format(label_AT), label_image))
                    else:
                        pass
                        # copied_files += 1
                        # print("non exist")
                except Exception as e:
                    pass
                    # print("error!", e, csvfile, line)
                # break
    print(copied_files, 'files copied')

def mapColChEn():
    csvfile = 'posdata/001-2021-01-01.html'
    with open(csvfile, 'r') as f:
        # print(f.read())
        soup = bs(f.read(),'html.parser')
        soup = soup.find_all("table")[1].find_all("tr")
        colCh = soup[1].find_all("th")
        colEn = soup[2].find_all("th")
        for index in range(len(colCh)):
            print(index)

def DlPrepare(datapath):
    '''
        generate folders of classes(-10.0 to 50.0) from img and posdata
    '''
    path = os.path.join('data', datapath)
    if not os.path.exists(path):
        os.makedirs(path)
    # at_classes = ["c{}".format(x) for x in range(-100,500)]
    at_classes = ["c{}".format(x) for x in range(-10,50)]
    print(at_classes)
    for c in at_classes:
        cpath = os.path.join(path,'classes',c)
        print(cpath)
        if not os.path.exists(cpath):
            os.makedirs(cpath)

def resizePics():
    for dir,dirnames,files in os.walk('data/valid/classes'):
        for f in files:
            imgpath = os.path.join(dir,f)
            img = cv2.imread(imgpath)
            img = cv2.resize(img,(1280,720))
            print(imgpath)
            print(img.shape)
            cv2.imwrite(imgpath,img)

resizePics()
# DlPrepare('valid')
# labelPosPic('valid')
# matchAirAndStation()