from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import sys
from winotify import Notification,audio
from settings import Setting
import time
import datetime
from main_ui import Ui_MainWindow
from sourceAdapter import UnsplashAdapter,WallhavenAdapter,QuoteAdapter

baseDir = os.path.dirname(__file__)
RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"

class RequestNewWallpaperUpdater(QThread):
    RequestNewWallpapeValue = pyqtSignal(bool)
    
    def __init__(self,myapp_obj):
        QThread.__init__(self)
        self.myapp_obj = myapp_obj

    def run(self):
        self.RequestNewWallpaper()
    
    def RequestNewWallpaper(self):
        if self.myapp_obj.setting.getSource().lower() == 'unsplash':
            res = self.myapp_obj.unsplash_adapter.requestRandomImage()
        else:
            res = self.myapp_obj.wallhaven_adapter.requestRandomImage()
            # print('wallhaven')
        if self.myapp_obj.ui.request_btn.text()=='Loading...':
            self.RequestNewWallpapeValue.emit(True)


class RequestQuoteUpdater(QThread):
    RequestQuoteValue = pyqtSignal(list)
    
    def __init__(self,myapp_obj):
        QThread.__init__(self)
        self.myapp_obj = myapp_obj

    def run(self):
        self.RequestQuote()
    
    def RequestQuote(self):
        if self.myapp_obj.setting.getQuoteAutoFetch():
            title,content = self.myapp_obj.quote_adapter.requestQuote()
            if title is not None and content is not None:
                self.RequestQuoteValue.emit([title,content])
            
        if self.myapp_obj.setting.getQuranAutoFetch():
            title,content = self.myapp_obj.quote_adapter.requestAyah()
            if title is not None and content is not None:
                self.RequestQuoteValue.emit([title,content])
        


class MyApplicationGui(QMainWindow):
    isShowingValue = pyqtSignal(bool)
    timeValue = pyqtSignal(object)
    
    def __init__(self,app):
        QMainWindow.__init__(self)
        self.app = app
        self.setWindowIcon(QIcon(os.path.join(baseDir,'assets','logo.svg')))
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        
        self.setFonts()
        
        self.setEvents()
        
        self.initSetting()
        self.setSourceAdapter()
    
    
    def animateWindow(self,rect_trayicon):
        animation = QPropertyAnimation(self, b"geometry")
        animation.setStartValue(self.geometry())
        rect_window = self.geometry()
        animation.setEndValue(QRect(rect_trayicon.x()-(rect_window.width()//2),rect_trayicon.y()-rect_window.height(), rect_window.width(), rect_window.height()))
        # animation.setEndValue(QRect(100,100, rect_window.width(), rect_window.height()))
        animation.setDuration(500)
        self.group = QParallelAnimationGroup()
        self.group.addAnimation(animation)
        self.group.start()
        
    def closeEvent(self, event):
        event.ignore()  # ignore the close event
        self.hide()  # hide the window instead of closing it
    
    def event(self, event):
        if event.type() == QEvent.WindowDeactivate:
            # print('hello',event.type(),datetime.datetime.now())
            # self.app.isShowing = False
            self.isShowingValue.emit(False)
            self.timeValue.emit(datetime.datetime.now())
            self.hide()
        return super().event(event)
        

    def setSourceAdapter(self):
        self.unsplash_adapter = UnsplashAdapter(self.setting)
        self.wallhaven_adapter = WallhavenAdapter(self.setting)
        self.quote_adapter = QuoteAdapter()
        self.RequestNewWallpaperThread = RequestNewWallpaperUpdater(self)
        self.RequestNewWallpaperThread.RequestNewWallpapeValue.connect(self.update_request_button)
        self.RequestQuoteThread = RequestQuoteUpdater(self)
        self.RequestQuoteThread.RequestQuoteValue.connect(self.update_quote)
        
    def setFonts(self):
        self.font_id = QFontDatabase.addApplicationFont(os.path.join(baseDir,'assets','Roboto.ttf'))
        font_family = QFontDatabase.applicationFontFamilies(self.font_id)[0]
        self.setStyleSheet(f"\nfont-family: '{font_family}';\n" + self.styleSheet())
        font = QFont(font_family)
        font.setPointSize(12)
        self.ui.comboBox.setFont(font)
        
    def update_quote(self,value):
        self.SendNotification(value[0],value[1])
        
    def SendNotification(self,title,content,duration='long',app_id='Random Wallpaper'):
        noti = Notification(app_id,title,content,duration=duration)
        noti.set_audio(audio.SMS,loop=False)
        noti.show()
        
    def setEvents(self):
        self.ui.exit_btn.clicked.connect(self.exit_btn_clicked)
        self.ui.request_btn.clicked.connect(self.request_btn_clicked)
        self.ui.checkBox_auto_fetch.stateChanged.connect(self.checkBox_auto_fetch_changed)
        self.ui.hours_slider.valueChanged['int'].connect(self.hours_slider_changed)
        self.ui.minutes_slider.valueChanged['int'].connect(self.minutes_slider_changed)
        self.ui.comboBox.currentIndexChanged['int'].connect(self.combobox_changed)
        self.ui.checkBox_featured_unsplash.stateChanged.connect(self.checkBox_featured_unsplash_changed)
        self.ui.unsplash_keyword_lineedit.focusOutEvent = lambda event: self.unsplash_keyword_lineedit_focusOutEvent(event)
        self.ui.wallhaven_keyword_lineedit.focusOutEvent = lambda event: self.wallhaven_keyword_lineedit_focusOutEvent(event)
        self.ui.checkBox_quote_auto_fetch.stateChanged.connect(self.checkBox_quote_auto_fetch_changed)
        self.ui.checkBox_quran_auto_fetch.stateChanged.connect(self.checkBox_quran_auto_fetch_changed)
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._countdown_and_show)
        self.timer.setInterval(1000)
    
    def checkBox_quote_auto_fetch_changed(self):
        self.setting.setQuoteAutoFetch(self.ui.checkBox_quote_auto_fetch.isChecked())
    
    def checkBox_quran_auto_fetch_changed(self):
        self.setting.setQuranAutoFetch(self.ui.checkBox_quran_auto_fetch.isChecked())
        
    def combobox_changed(self,index):
        if index == 0:
            self.setting.setSource('unsplash')
            self.ui.stackedWidget.setCurrentWidget(self.ui.unsplash_page)
        elif index == 1:
            self.setting.setSource('wallhaven')
            self.ui.stackedWidget.setCurrentWidget(self.ui.wallhaven_page)
    
    def checkBox_featured_unsplash_changed(self):
        self.setting.setUnsplashFeatured(self.ui.checkBox_featured_unsplash.isChecked())

    def unsplash_keyword_lineedit_focusOutEvent(self,event):
        self.setting.setUnsplashKeywords(self.ui.unsplash_keyword_lineedit.text())
    
    def wallhaven_keyword_lineedit_focusOutEvent(self,event):
        self.setting.setWallhavenKeywords(self.ui.wallhaven_keyword_lineedit.text())
        
    
    def hours_slider_changed(self,value):
        self.ui.hours_value_label.setNum(value)
        self.updateInterval()
    
    def minutes_slider_changed(self,value):
        self.ui.minutes_value_label.setNum(value)
        self.updateInterval()
        
    def updateInterval(self):
        value = int((int(self.ui.hours_value_label.text()) * 60 + int(self.ui.minutes_value_label.text())) * 60)
        self._left_seconds = value
        self.setting.setFetchInterval(value)
        
    def checkBox_auto_fetch_changed(self):
        self.setting.setAutoFetch(self.ui.checkBox_auto_fetch.isChecked())
        # print(self.setting.isAutoFetch(),'===============================================')
        self.changeComponentStatus(self.setting.isAutoFetch())
        
    def changeComponentStatus(self,status):
        if status:
            self._left_seconds = self.setting.getFetchInterval()
            # print(self._left_seconds)
            self.ShowTime()
            self.timer.start()
            self.ui.rest_time.setVisible(True)
            self.ui.rest_time.setMaximumHeight(100)
            self.ui.hours_slider.setEnabled(True)
            self.ui.hours_value_label.setEnabled(True)
            self.ui.minutes_value_label.setEnabled(True)
            self.ui.minutes_slider.setEnabled(True)
        else:
            if self.timer.isActive():
                self.timer.stop()
            self.ui.rest_time.setVisible(False)
            self.ui.rest_time.setMaximumHeight(0)
            self.ui.hours_slider.setEnabled(False)
            self.ui.hours_value_label.setEnabled(False)
            self.ui.minutes_value_label.setEnabled(False)
            self.ui.minutes_slider.setEnabled(False)
        
    def convert_seconds_to_hours_minutes(self,seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return hours, minutes

    def request_btn_clicked(self):
        self.update_request_button(False)
        
        # fetch the image and change the background
        self.RequestNewWallpaperThread.start()
        self.RequestQuoteThread.start()
        
    
    def update_request_button(self,value):
        if value:
            self.ui.request_btn.setEnabled(True)
            self.ui.request_btn.setText('Request New Wallpaper')
            self.ui.request_btn.setStyleSheet(Setting.REQUEST_BTN_STYLE)
        else:
            self.ui.request_btn.setEnabled(False)
            self.ui.request_btn.setText('Loading...')
            self.ui.request_btn.setStyleSheet(Setting.REQUEST_BTN_STYLE_LOADING)
    
    def RequestNewWallpaper(self):
        if self.setting.getSource().lower() == 'unsplash':
            self.unsplash_adapter.requestRandomImage()
        else:
            self.wallhaven_adapter.requestRandomImage()
            # print('wallhaven')
        
    def initSetting(self):
        self.setting = Setting()
        self.ui.checkBox_auto_fetch.setChecked(self.setting.isAutoFetch())
        self.changeComponentStatus(self.setting.isAutoFetch())
        hours, minutes = self.convert_seconds_to_hours_minutes(self.setting.getFetchInterval())
        self.ui.hours_value_label.setText(str(hours))
        self.ui.hours_slider.setValue(hours)
        self.ui.minutes_value_label.setText(str(minutes))
        self.ui.minutes_slider.setValue(minutes)
        
        self.ui.checkBox_featured_unsplash.setChecked(self.setting.getUnsplashFeatured())
        self.ui.unsplash_keyword_lineedit.setText(self.setting.getUnsplashKeywords())
        self.ui.wallhaven_keyword_lineedit.setText(self.setting.getWallhavenKeywords())
        self.ui.comboBox.setCurrentIndex(0 if self.setting.getSource().lower()=='unsplash' else 1)
        self.ui.checkBox_quote_auto_fetch.setChecked(self.setting.getQuoteAutoFetch())
        self.ui.checkBox_quran_auto_fetch.setChecked(self.setting.getQuranAutoFetch())
        
    
    def _countdown_and_show(self):
        if self._left_seconds > 0:
            self._left_seconds -= 1
            self.ShowTime()
        else:
            # print("change wallpaper")
            self._left_seconds = self.setting.getFetchInterval()
            self.RequestNewWallpaperThread.start()
            self.RequestQuoteThread.start()
            # self.RequestNewWallpaper()
            self.ShowTime()
    
    def exit_btn_clicked(self):
        self.app.quit()
        
    def ShowTime(self):
        total_seconds = min(self._left_seconds, 359940)  # Max time: 99:59:00
        hours = total_seconds // 3600
        total_seconds = total_seconds - (hours * 3600)
        minutes = total_seconds // 60
        seconds = total_seconds - (minutes * 60)
        self.ui.rest_time.display('-'+"{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds)))










class MyApplication(QApplication):
    def __init__(self,argv):
        QApplication.__init__(self,argv)

        self.trayicon = QSystemTrayIcon(QIcon(os.path.join(os.path.dirname(__file__),'assets','logo.png')),parent=self)
        self.trayicon.setToolTip("Random Wallpaper")
        self.trayicon.show()
        self._isShowing = False
        self._triggerTime = None
        
        self.trayicon.activated.connect(self.on_tray_icon_activated)
        
        
        self.settings = QSettings(RUN_PATH, QSettings.NativeFormat)
        self.settings.setValue("RandomWallpaper",os.path.join(baseDir,'main.exe'))
    
    @property
    def isShowing(self):
        return self._isShowing

    @isShowing.setter
    def isShowing(self, value):
        self._isShowing = value
    
    @property
    def triggerTime(self):
        return self._triggerTime

    @triggerTime.setter
    def triggerTime(self, value):
        self._triggerTime = value

    def on_tray_icon_activated(self,reason):
        if reason == QSystemTrayIcon.Trigger:
            # self.trayicon.showMessage("Title", "Content of the message", QSystemTrayIcon.Information, 5000)
            if not (self.isShowing==False and self.triggerTime is not None and (datetime.datetime.now() - self.triggerTime)<datetime.timedelta(seconds=1)):
                self.isShowing = not self.isShowing
                self.ToggleWallpaperGui()

    def ToggleWallpaperGui(self):
        if not hasattr(self,'WallpaperGui'):
            self.WallpaperGui = MyApplicationGui(self)
            self.WallpaperGui.isShowingValue.connect(self.change_showing_value)
            self.WallpaperGui.timeValue.connect(self.change_time_value)
        if self.isShowing:
            self.WallpaperGui.show()
            self.WallpaperGui.activateWindow()
            self.changePosition()
        else:
            self.WallpaperGui.hide()
        
    def change_showing_value(self,value):
        self.isShowing = False
    
    def change_time_value(self,value):
        self._triggerTime = value
    
    def changePosition(self):
        if hasattr(self,'WallpaperGui'):
            rect_trayicon = self.trayicon.geometry()
            rect_window = self.WallpaperGui.geometry()
            # self.WallpaperGui.move(rect_trayicon.x()-(rect_window.width()//2),rect_trayicon.y()-rect_window.height())
            self.WallpaperGui.move(rect_trayicon.x()-(rect_window.width()//2),rect_trayicon.y())
            self.WallpaperGui.animateWindow(rect_trayicon)
            # self.animateWindow()
    
    def animateWindow(self):
        animation = QPropertyAnimation(self.WallpaperGui, b"geometry")
        animation.setStartValue(self.WallpaperGui.geometry())
        rect_trayicon = self.trayicon.geometry()
        rect_window = self.WallpaperGui.geometry()
        animation.setEndValue(QRect(100,rect_trayicon.y()-rect_window.height(), self.WallpaperGui.width(), self.WallpaperGui.height()))
        # animation.setEndValue(QRect(rect_trayicon.x()-(rect_window.width()//2),rect_trayicon.y()-rect_window.height(), self.WallpaperGui.width(), self.WallpaperGui.height()))
        animation.setDuration(1000)
        # print('---------------------------------------------------------------------------------start animation ')
        animation.start()
        



















    


def main():
    app = MyApplication(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()