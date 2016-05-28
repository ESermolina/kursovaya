import sys
import argparse
import process
import logging
import datetime

 
def createParser ():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--symbol", help="Биржевой символ акций")
    parser.add_argument("-f","--file", help="Файл для обработки")
    parser.add_argument ("-y", "--year", help="Год", default=datetime.datetime.now().year, type=int)
    parser.add_argument ("-fo", "--file_out", help="Файл для записи результата", default="rezult.txt")
    parser.add_argument ("-fl", "--file_log", help="Файл для логирования", default="app.log")
    parser.add_argument ("-l", "--level_log", help="Уровень логирования", default="INFO")
    parser.add_argument ("-i", "--indicator", help="Индикатор (MACD-Индикатор MACD)")
    parser.add_argument ("-ws", "--window_s", help="Интервал короткого периода", type=int, default=12)
    parser.add_argument ("-wl", "--window_l", help="Интервал длинного периода", type=int, default=26)
  
    return parser

if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    if namespace.file:
        logging.basicConfig(filename=namespace.file_log, level=namespace.level_log, filemode='w')
        logging.info('Программа запущена с параметрами ' + str(namespace) + " в режиме файл")
        try:
            process.process_file(namespace.file, namespace.file_out, namespace.indicator, namespace.window_s, namespace.window_l) 
        except Exception as e:
            logging.error(str(e))
    elif namespace.symbol:
        logging.basicConfig(filename=namespace.file_log, level=namespace.level_log)
        logging.info('Программа запущена с параметрами ' + str(namespace) + " в режиме сеть")
        try:
            process.process_network(namespace.symbol, namespace.year,  namespace.file_out, namespace.indicator, namespace.window_s, namespace.window_l)
        except Exception as e:
            logging.error(str(e))
