from pytube import YouTube
class Downloader:
    def __init__(self, url, location,name):
        self.url = url
        self.location = location
        self.name = name

    def download(self):
       self.name = YouTube(self.url).streams.first().download(self.location,filename=self.name)