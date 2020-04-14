import logging

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s [%(levelname)s] %(module)s:%(funcName)s:%(lineno)d: %(message)s',
    filename='/tmp/smartcar.log',
    stream=
)
logging.info('\n'*4)
logging.info('\n='*30)
