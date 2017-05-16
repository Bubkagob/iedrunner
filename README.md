# IED Runner

****************************************
POWERED on libIEC61850
****************************************


IED Runner - клиент для IED устройств со встроенным модулем проверки, позволяющий:

  - Проверить SCL/ICD/CID файл на синтаксис спецификации IEC-61850//
  - Проверить подключение к заданному IED
  - Проверить параметры IED устройства на основе исходного файла
  - Записать, прочитать данные по всем переменным(тест)

### Installation
IED runner требует следующие пакеты для работы: 
     -  [Python](https://python.org/) v3+
     -  [SWIG](http://www.swig.org//) (Реализация py-обертки iec61850 библиотеки)
     -  [lxml](http://lxml.de/)  (Python XML модуль)

Установка lxml возможна с помощью pip:
```sh
$ pip install lxml
```
Установка SWIG (cygwin, Linux ...)
[SWIG](http://www.swig.org/download.html)


### Запуск


RUN.PY - Запуск тестов (Необходим работающий сервер + SCD/ICD/ файл)
*для запуска теста с shm-client необходимо вручную отредактировать констанкты в def sasClient функции (строка 1000 iec/sclparser.py)
```sh
$ python run.py --file=$FILENAME --ip=$IP --ied=$FULLIEDNAME
```

FLOW.PY - Запуск тестов через shared memory клиента (Необходим работающий сервер + файл с заготовленным потоком VarName, type, Value)
```sh
$ python flow.py --client=$PATH_TO_SHMCLIENT --connection=$SHMFILENAME --file=$PATH_TO_FLOW_FILE  --repeat=$N_TIMES --timeout=$N_MICROSECONDS
```

OBSERVER.PY - Пробежаться по серверу, чтобы посмотреть структурку, пока на локалхосте, если хотите поменять - там внутри
```sh
$ python observer.py
```

#### Отчет
консоль:
```sh
$ ИМЯ_ТЕСТА_1
$ OK/FAILED/ERROR
$ ИМЯ_ТЕСТА_2
$ OK/FAILED/ERROR
$ =========================
$ Сводка
```


### ToDo list

 - Возможность выбора тестов