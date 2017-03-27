# IED Runner

****************************************
POWERED on libIEC61850
****************************************


IED Runner - ������ ��� IED ��������� �� ���������� ������� ��������, �����������:

  - ��������� SCL/ICD/CID ���� �� ��������� ������������ IEC-61850//
  - ��������� ����������� � ��������� IED
  - ��������� ��������� IED ���������� �� ������ ��������� �����

### Installation
IED runner ������� ��������� ������ ��� ������: 
     -  [Python](https://python.org/) v3+
     -  [SWIG](http://www.swig.org//) (���������� py-������� iec61850 ����������)
     -  [lxml](http://lxml.de/)  (Python XML ������)

��������� lxml �������� � ������� pip:
```sh
$ pip install lxml
```
��������� SWIG (cygwin, Linux ...)
[SWIG](http://www.swig.org/download.html)


### ������

������ �������������� �� ���������� �������

iedRunner ����������:
```sh
$ python run.py -f $file(���_�����) -ip $ip(�����_IED_����������)
```

#### �����
�������:
```sh
$ ���_�����_1
$ OK/FAILED/ERROR
$ ���_�����_2
$ OK/FAILED/ERROR
$ =========================
$ ������
```


### ToDo list

 - ������� �����-������������� ��������� iec61850 ����������
 - �������� ������ ����� 
 - ����������� ������ ������