import random
import json
import os
import requests
import shutil
import tempfile
from pyWallpaper import PyWallpaper

class UnsplashAdapter():
    def __init__(self,setting):
        self.sourceName = 'Unsplash'
        self.setting = setting
        self.sourceUrl = 'https://source.unsplash.com'

        self.options = {
			'query': '',
			'w': 3840,
			'h': 2160,
			'featured': False,
		}
        self._readOptionsFromSettings()
    
    def requestRandomImage(self):
        self._readOptionsFromSettings()
        optionString = self._generateOptionsString()
        url = self.sourceUrl+optionString
        # print(url,'===============================================================================')
        filename = os.path.join(tempfile.gettempdir(),'image.jpg')
        # filename = os.path.join(os.path.dirname(__file__),'image.jpg')
        self.SaveImage(url,filename)
        return PyWallpaper().set_wallpaper(filename)
    
    def SaveImage(self,url,filename):
        try:
            r = requests.get(url=url,stream=True)
            if r.status_code == 200:
                # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                r.raw.decode_content = True
                
                # Open a local file with wb ( write binary ) permission.
                with open(filename,'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                    
                print('Image sucessfully Downloaded: ',filename)
                return True
            else:
                print('Image Couldn\'t be retreived')
                return False
        except :
            print('check your connection')
            return False

        
    def _generateOptionsString(self):
        options = self.options
        if options['featured']:
            optionString='/featured/'
        else:
            optionString = '/random/'
        optionString +=f'{options["w"]}x{options["h"]}'
        if options['query']:
            q = ' '.join(options['query'].split()).replace(' ',',')
            optionString += f'?{q}'
        return optionString

    
    def _readOptionsFromSettings(self):
        keywords = self.setting.getUnsplashKeywords().split(',')
        if len(keywords)>0:
            randomkeyword = random.choice(keywords)
            self.options['query']=randomkeyword.strip()
        self.options['featured'] = self.setting.getUnsplashFeatured()
    
    


class WallhavenAdapter():
    def __init__(self,setting):
        self.sourceName = 'wallhaven'
        self.setting = setting
        self.sourceUrl = 'https://wallhaven.cc/api/v1/search?'

        self.options = {
			'q': '',
			# 'apikey': '',
			'purity': '110', # SFW, sketchy
			'sorting': 'random',
			'categories': '111', # General, Anime, People
			'resolutions': '1920x1200,2560x1440'
		}
        self._readOptionsFromSettings()
    
    def requestRandomImage(self):
        self._readOptionsFromSettings()
        optionString = self._generateOptionsString()
        url = self.sourceUrl+optionString
        # print(url,'===============================================================================')
        # filename = os.path.join(os.path.dirname(__file__),'image.jpg')
        filename = os.path.join(tempfile.gettempdir(),'image.jpg')
        self.SaveImage(url,filename)
        return PyWallpaper().set_wallpaper(filename)
    
    def SaveImage(self,url,filename):
        try:
            r = requests.get(url=url)
            if r.status_code == 200:
                url = random.choice(json.loads(r.text)['data'])['path']
                r = requests.get(url=url,stream=True)
                if r.status_code == 200:
                    # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                    r.raw.decode_content = True
                    # Open a local file with wb ( write binary ) permission.
                    with open(filename,'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                    
                    print('Image sucessfully Downloaded: ',filename)
                    return True
                else:
                    print('Image Couldn\'t be retreived')
                    return False
            else:
                print('Image Couldn\'t be retreived')
                return False
        except :
            print('check your connection')
            return False

    def _generateOptionsString(self):
        optionString = ''
        for key in self.options:
            optionString+=f'{key}={self.options[key]}&'
                
        return optionString[:-1]
        
    def _readOptionsFromSettings(self):
        keywords = self.setting.getWallhavenKeywords().split(',')
        if len(keywords)>0:
            randomkeyword = random.choice(keywords)
            self.options['q']=randomkeyword.strip()


class QuoteAdapter():
    def __init__(self):
        self.sourceUrl = 'https://api.quotable.io/random'
    
    def requestQuote(self):
        try:
            resp = requests.get(self.sourceUrl)
            if resp.status_code==200:
                res = json.loads(resp.text)
                return '— '+res['author'],res['content']
            else:
                return None,None
        except:
            print('check your connection')
            return None,None
    
    def requestAyah(self):
        try:
            surah = random.randint(1,114)
            url = f'http://api.alquran.cloud/v1/surah/{surah}'
            resp = requests.get(url)
            if resp.status_code==200:
                data = json.loads(resp.text)['data']
                name = data['name']
                ayah = random.choice(data['ayahs'][1:])['text']
                return name,ayah
            else:
                return None,None
        except:
            print('check your connection')
            return None,None
    