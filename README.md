# IED Runner

****************************************
POWERED on libIEC61850
****************************************


IED Runner - клиент для IED устройств со встроенным модулем проверки, позволяющий:

  - Проверить SCL/ICD/CID файл на синтаксис спецификации IEC-61850//
  - Проверить подключение к заданному IED
  - Проверить параметры IED устройства на основе исходного файла

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

Запуск в связке с shm-клиентом

```sh
$ python Flow.py --client='PATH_TO_CLIENT_APP' --connection='CONNECTION_NAME' --file='PATH_TO_TESTING_FLOW_FILE' --repeat=N_TIMES --timeout=N_MICROSECONDS
```

Запуск осуществляется со следующими ключами

iedRunner директория:
```sh
$ python run.py -f $file(имя_файла) -ip $ip(адрес_IED_устройства)
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

 - Создать кросс-платформенную генерацию iec61850 библиотеки
 - Добавить другие тесты 
 - Возможность выбора тестов