import logging
import logging.handlers

LOG_FILE = 'tst.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5)
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)  # 为handler添加formatter

logger = logging.getLogger('tst')  # 获取名为tst的logger
logger.addHandler(handler)  # 为logger添加handler
logger.setLevel(logging.DEBUG)


LOG_FILE2 = 'error.log'
handler2 = logging.handlers.RotatingFileHandler(LOG_FILE2, maxBytes = 1024*1024, backupCount = 5)
fmt2 = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter2 = logging.Formatter(fmt2)  # 实例化formatter
handler2.setFormatter(formatter2)  # 为handler添加formatter
logger2 = logging.getLogger('error')  # 获取名为tst的logger
logger2.addHandler(handler)  # 为logger添加handler
logger2.setLevel(logging.DEBUG)

def info(v):
    logger.info(v)

def error(v):
    logger2.error(v)
