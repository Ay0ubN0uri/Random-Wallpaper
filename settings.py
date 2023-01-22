from PyQt5.QtCore import QSettings



class Setting():
    REQUEST_BTN_STYLE = ".QPushButton {    \n    background-color: rgba(39,119,255,255);\n    color: white;\n    padding: 20px;\n    border:none;\n    border-radius:10px;\n    font-size:20px;\n}\n.QPushButton:hover {\n    background-color: #3d85ff;\n}\n.QPushButton:pressed {    \n    background-color: #204a91;\n    color:#878a91;\n}"
    REQUEST_BTN_STYLE_LOADING = ".QPushButton {\nbackground-color: #204a91;\ncolor: #878a91;\npadding: 20px;\nborder:none;\nborder-radius:10px;\nfont-size:20px;\n}\n.QPushButton:hover {\nbackground-color: #3d85ff;\n}\n.QPushButton:pressed {\nbackground-color: #204a91;\ncolor:#878a91;\n}"
    
    def __init__(self):
        self.getSettingValues()
    
    
    def getSettingValues(self):
        self.wallpaper_setting = QSettings('RandomWallpaper','settings')
        self.setDefaultValues()
    
    def setDefaultValues(self):
        if not self.wallpaper_setting.contains('AutoFetch'):
            self.wallpaper_setting.setValue('AutoFetch',False)
        if not self.wallpaper_setting.contains('quote-auto-fetch'):
            self.wallpaper_setting.setValue('quote-auto-fetch',False)
        if not self.wallpaper_setting.contains('quran-auto-fetch'):
            self.wallpaper_setting.setValue('quran-auto-fetch',False)
        if not self.wallpaper_setting.contains('FetchInterval'):
            self.wallpaper_setting.setValue('FetchInterval',900) # in seconds (15 min)
        if not self.wallpaper_setting.contains('WallpaperSource'):
            self.wallpaper_setting.setValue('WallpaperSource','unsplash')
        if not self.wallpaper_setting.contains('unsplash-featured'):
            self.wallpaper_setting.setValue('unsplash-featured','false')
        if not self.wallpaper_setting.contains('unsplash-keyword'):
            self.wallpaper_setting.setValue('unsplash-keyword','')
        if not self.wallpaper_setting.contains('wallhaven-keyword'):
            self.wallpaper_setting.setValue('wallhaven-keyword','')
        
            
    def getQuoteAutoFetch(self):
        if self.wallpaper_setting.value('quote-auto-fetch').lower()=='true':
            return True
        else:
            return False

    def setQuoteAutoFetch(self,value):
        return self.wallpaper_setting.setValue('quote-auto-fetch',value)

    def getQuranAutoFetch(self):
        if self.wallpaper_setting.value('quran-auto-fetch').lower()=='true':
            return True
        else:
            return False

    def setQuranAutoFetch(self,value):
        return self.wallpaper_setting.setValue('quran-auto-fetch',value)
    
    def getFetchInterval(self):
        return int(self.wallpaper_setting.value('FetchInterval'))
    
    def isAutoFetch(self):
        if self.wallpaper_setting.value('AutoFetch').lower()=='true':
            return True
        else:
            return False
    
    def setAutoFetch(self,value):
        self.wallpaper_setting.setValue('AutoFetch',value)
    
    def setFetchInterval(self,value):
        self.wallpaper_setting.setValue('FetchInterval',value)
    
    def getSource(self):
        return self.wallpaper_setting.value('WallpaperSource')
    
    def setSource(self,value):
        self.wallpaper_setting.setValue('WallpaperSource',value)
    
    def getUnsplashKeywords(self):
        return self.wallpaper_setting.value('unsplash-keyword')
    
    def setUnsplashKeywords(self,value):
        self.wallpaper_setting.setValue('unsplash-keyword',value)
    
    def getWallhavenKeywords(self):
        return self.wallpaper_setting.value('wallhaven-keyword')
    
    def setWallhavenKeywords(self,value):
        self.wallpaper_setting.setValue('wallhaven-keyword',value)

    def getUnsplashFeatured(self):
        if self.wallpaper_setting.value('unsplash-featured').lower()=='true':
            return True
        else:
            return False
    
    def setUnsplashFeatured(self,value):
        self.wallpaper_setting.setValue('unsplash-featured',value)
        



