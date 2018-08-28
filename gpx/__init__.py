from .parser import GPXParser


def parse(xml):
    return GPXParser(xml)
