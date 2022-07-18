# Written by Beau Daoust (2021)
from scrapy.pipelines.files import FilesPipeline

class EzproxyPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        file_name: str = request.url.split("/")[-1]
        return file_name