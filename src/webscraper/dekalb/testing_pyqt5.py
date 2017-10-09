# import sys  
# from PyQt5.QtGui import *  
# from PyQt5.QtCore import *  
# # from PyQt5.QtWebKit import *  
# from PyQt5.QtWebEngineWidgets import *
# from lxml import html 

# #Take this class for granted.Just use result of rendering.
# class Render(QWebEngineView):  
#   def __init__(self, url):  
#     self.app = QApplication(sys.argv)  
#     QWebEngineView.__init__(self)  
#     self.loadFinished.connect(self._loadFinished)  
#     self.mainFrame().load(QUrl(url))  
#     self.app.exec_()  
  
#   def _loadFinished(self, result):  
#     self.frame = self.mainFrame()  
#     self.app.quit()  

# url = 'http://pycoders.com/archive/'  
# r = Render(url)  
# result = r.frame.toHtml()
# #This step is important.Converting QString to Ascii for lxml to process
# archive_links = html.fromstring(str(result.toAscii()))
# print(archive_links)

import sys
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QApplication

class Render(QWebEnginePage):
  def __init__(self, html):
    # self.html = None
    self.app = QApplication(sys.argv)
    QWebEnginePage.__init__(self)
    self.loadFinished.connect(self._loadFinished)
    self.load(QUrl(url))
    self.app.exec_()
    # self.setHtml(html)
    # while self.html is None:
    #   self.app.processEvents(
    #     QEventLoop.ExcludeUserInputEvents |
    #     QEventLoop.ExcludeSocketNotifiers |
    #     QEventLoop.WaitForMoreEvents)
    #   self.app.quit()

  def _loadFinished(self, result):
      self.frame = self.load
      self.app.quit()

url = 'http://pycoders.com/archive/'  
r = Render(url)  
result = r.frame.toHtml()
#This step is important.Converting QString to Ascii for lxml to process
archive_links = html.fromstring(str(result.toAscii()))
print(archive_links)
print('hello')