#libraries
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sys
from IPython.display import clear_output
import time
from fake_useragent import UserAgent
import random as rd
import time

#idk, an open source progressbar. Cuz why not?
def progressBar(count_value, total, suffix=''):
    bar_length = 100
    filled_up_Length = int(round(bar_length* count_value / float(total)))
    percentage = round(100.0 * count_value/float(total),1)
    bar = '=' * filled_up_Length + '-' * (bar_length - filled_up_Length)
    sys.stdout.write('[%s] %s%s ...%s\r' %(bar, percentage, '%', suffix))
    sys.stdout.flush()


class GSMArenaScraper():
    '''Your normal GSM Sscraper mate!'''
    
    def __init__(self, hidden=True, timer=4):
        '''Your normal init thing?'''
        self.web="https://www.gsmarena.com/"
        self.hidden= hidden                                                                                                     #if set false, not need to run either getidentity or getidentityfile
        self.timer=timer
        self.useragentlist=[UserAgent().random for i in range(100)]                                                            #get UserAgentList
        #empty list for what imma scrap next.
        self.data=pd.DataFrame(columns=["Manufacturer", "Phone Name", "Release Date", "OS", "Battery Size", "Battery Type", "Screen Size", "Screen Type", "Network Technology", "Chipset", "CPU", "GPU", "Internal Memory", "Main Camera Specifications", "Main Camera Video", "Selfie Camera Specificications", "Selfie Camera Video", "Price"])
    
    def getidentity(self, proxies=20, debug=False):
        self.debug=1 if debug else 0
        '''Get a random users and proxies. Why should i be respectful? Cuh.'''
        
        proxydata=pd.DataFrame(columns=["IP", "Port", "Country", "Anonymity", "Last Checked"])
        header= {'User-Agent': str(rd.sample(self.useragentlist, 1)), "Accept-Language": "en-US, en;q=0.5"}
        SSLPROXIES=requests.get("https://www.sslproxies.org/", headers= header)
        soup=BeautifulSoup(SSLPROXIES.content, "html5lib")
        table=soup.find("table", attrs={"class" : "table table-striped table-bordered"}).find("tbody")
        counter=0
        for i in table.find_all("tr"):
                if counter==proxies:
                        break
                values=[j.text for j in i.find_all("td")]
                proxydata.loc[len(proxydata)]=[values[0], values[1], values[3], values[4], values[7]]
                counter+=1
        self.proxydata=proxydata
        self.brute()
        
    def getidentityfromfile(self, debug=False):
        self.debug=1 if debug else 0
        self.proxydata=pd.read_table("File/Free_Proxy_List.txt", header=0, delimiter=",")
        self.proxydata=self.proxydata.iloc[:,[0,7,3]]
        self.brute()
        
    def brute(self):
        '''BruteChecker'''
        usableproxyindex=[]                                                              #index
        for i in range(len(self.proxydata)):
            rowproxydata=self.proxydata.iloc[i,:].values
            proxy= {
            'http': f'http://{rowproxydata[0]}:{rowproxydata[1]}',
            'https': f'http://{rowproxydata[0]}:{rowproxydata[1]}',
            }
            if self.debug:
                print(f'Trying to connect {rowproxydata[0]}:{rowproxydata[1]} |{rowproxydata[2]}|', end="status: ")
            try:
                r=requests.get(self.web, proxies=proxy, timeout=15)
                if  BeautifulSoup(r.content, 'html5lib').find("title").text != "Too Many Requests":
                    usableproxyindex.append(i)
                    print("Success")
                else:
                    print("failed")
            except:
                print("failed")
                pass
        self.proxydata=self.proxydata.iloc[usableproxyindex,:]
    
    def requestget(self, link):
        if not self.hidden:
            return requests.get(link)           #idk why i write this cuh
        while True:
            try:
                rduseragent=str(rd.sample(self.useragentlist, 1))
                header= {'User-Agent': rduseragent, "Accept-Language": "en-US, en;q=0.5"}
                rdrproxydata=self.proxydata.iloc[rd.randint(0,len(self.proxydata)-1),:].values
                if self.debug:
                    print(f'Connected to {rdrproxydata[0]}:{rdrproxydata[1]} | {rdrproxydata[2]}    | {rduseragent}')
                proxy= {
                    'http': f'http://{rdrproxydata[0]}:{rdrproxydata[1]}',
                    'https': f'http://{rdrproxydata[0]}:{rdrproxydata[1]}',
                    }
                time.sleep(self.timer)
                asu=requests.get(link, headers=header, proxies=proxy)
                return asu
            except:
                if self.debug:
                    print("retrying")
                pass

    def getphonespec(self, link):
        try:
            self.manufacturer
        except:
            self.manufacturer="Na"
            pass
        r=self.requestget(link)
        phonespecsoup=BeautifulSoup(r.content, "html5lib")
        try:
            phonename=phonespecsoup.find("h1", attrs={"class" : "specs-phone-name-title"}).text                                                                    #phone name
        except:
            phonename="Na"
            pass
        try:
            releasedate=phonespecsoup.find("span", attrs={"data-spec" :"released-hl"}).text.removeprefix("Released ")                                                #Released date
        except:
            releasedate="Na"
            pass
        try:
            os=phonespecsoup.find("span", attrs={"data-spec" :"os-hl"}).text                                                                                #OS
        except:
            os="Na"
            pass

        #battery
        try:
            batsize=phonespecsoup.find("span", attrs={"data-spec":"batsize-hl"}).text                                                                            #size
        except:
            batsize="Na"
            pass
        try:
            battype=phonespecsoup.find("div", attrs={"data-spec":"battype-hl"}).text                                                                            #type
        except:
            battype="Na"
            pass

        #screen
        try:
            scrsize=phonespecsoup.find("div", attrs={"data-spec":"displayres-hl"}).text.strip(" pixels")                                                     #resolution
        except:
            scrsize="Na"
            pass
        try:
            scrtype=phonespecsoup.find("td", attrs={"data-spec":"displaytype"}).text.strip(" pixels")                                                        #type
        except:
            scrtype="Na"
            pass
        try:
            nettech=phonespecsoup.find("a", attrs={"data-spec":"nettech"}).text                                                                              #network technology
        except:
            nettech="Na"
            pass

        #platform
        try:
            chipset=phonespecsoup.find("td", attrs={"data-spec":"chipset"}).text
        except:
            chipset="Na"
            pass
        try:
            cpu=phonespecsoup.find("td", attrs={"data-spec":"cpu"}).text
        except:
            cpu="Na"
            pass
        try:
            gpu=phonespecsoup.find("td", attrs={"data-spec":"gpu"}).text
        except:
            gpu="Na"
            pass
        try:
            internal=phonespecsoup.find("td", attrs={"data-spec":"internalmemory"}).text                                                                      #internal
        except:
            internal="Na"
            pass

        #main camera
        try:
            maincammodule= phonespecsoup.find("td", attrs={"data-spec":"cam1modules"}).text
        except:
            maincammodule="Na"
            pass
        try:
            maincamvid=phonespecsoup.find("td", attrs={"data-spec":"cam1video"}).text 
        except:
            maincamvid="Na"
            pass

        #selfie camera
        try:
            selfcammodule=phonespecsoup.find("td", attrs={"data-spec":"cam2modules"}).text
        except:
            selfcammodule="Na"
            pass
        try:
            selfcamvid= phonespecsoup.find("td", attrs={"data-spec":"cam2video"}).text 
        except:
            selfcamvid="Na"
            pass

        #price
        try:
            price=phonespecsoup.find("td", attrs={"data-spec":"price"}).text.strip("About ")
        except:
            price="Na"
            pass
        self.data.loc[len(self.data)]=[self.manufacturer, phonename, releasedate, os, batsize, battype, scrsize, scrtype, nettech, chipset, cpu, gpu, internal, maincammodule, maincamvid, selfcammodule, selfcamvid, price]
        
    def showbrandphone(self, pages):
        if type(pages)==list:
            for page in pages:
                r=self.requestget(page)
                soup=BeautifulSoup(r.content, "html5lib")
                thetable=soup.find("div", attrs={"class" : "makers"})
                self.manufacturer=soup.find("h1", attrs={"class" : "article-info-name"}).text.strip(" phones")
                for phone in thetable.find_all("a"):
                    speclink= self.web + phone["href"]
                    self.getphonespec(speclink)
        else:
            r=self.requestget(pages)
            soup=BeautifulSoup(r.content, "html5lib")
            thetable=soup.find("div", attrs={"class" : "makers"})
            self.manufacturer=soup.find("h1", attrs={"class" : "article-info-name"}).text.strip(" phones")
            for phone in thetable.find_all("a"):
                speclink= self.web + phone["href"]
                self.getphonespec(speclink)
    
    def scrapall(self):
        '''Start the scrap!'''
        
        r = self.requestget(self.web+"makers.php3")
        soup = BeautifulSoup(r.content, 'html5lib')
        table = soup.find('div', attrs = {'class':'st-text'})

        for manufacturer in table.find_all("a"):
            temp=manufacturer.span.extract()
            manufacturername=manufacturer.text                                                                             #get manufacturer name
            
            #Show phones made by manufacturer
            URL=self.web+manufacturer["href"]
            r=self.requestget(URL)
            soup=BeautifulSoup(r.content, "html5lib")
            
            #if there's only single page
            if soup.find("div", attrs={"class": "nav-pages"})==None:
                self.showbrandphone(URL)
            else:
                pages=[]
                getpages=soup.find("div", attrs={"class": "nav-pages"})
                #making proper pages list cuh
                count=1
                for page in getpages.find_all("a"):
                    URL=self.web+page["href"]
                    pages.append(URL)
                    count+=1
                pages.insert(0, URL.replace("p"+str(count), "p1"))
                self.showbrandphone(pages)