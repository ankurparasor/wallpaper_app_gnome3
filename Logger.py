from time import gmtime, strftime


class Logger(object):

    def __init__(self):
        def _gettimestamp():
            return strftime("%Y-%m-%d %H:%M:%S", gmtime())
        self._timestamp = _gettimestamp # here _timestamp is not a variable but a fuction

    def info(self, msg):
        print "INFO: %s : %s" %(self._timestamp(), msg)

    def error(self, msg):
        print "ERRO: %s : %s" %(self._timestamp(), msg)
