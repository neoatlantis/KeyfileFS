#!/usr/bin/env python3

class KeyfileFSConfig:

    def __init__(self):
        pass

    def readdir(self):
        yield "option-1"

    def getattr(self, basename):
        return {}
