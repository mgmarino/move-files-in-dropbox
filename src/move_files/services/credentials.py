import json

import s3fs


class Credentials:
    def __init__(self, credentials_location):
        fs = s3fs.S3FileSystem()
        with fs.open(credentials_location) as f:
            self.__credentials = json.load(f)

    @property
    def paths(self):
        return self.__credentials["paths"]

    @property
    def access_token(self):
        return self.__credentials["accessToken"]
