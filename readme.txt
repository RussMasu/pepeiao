

--Linux Installtion Instructions--
Create virtual enviroment, python3 -m venv env
Activate virtual enviroment, source env/bin/activate
If setuptools < 41.0.0 upgrade setuptools, pip install setuptools==41.0.0
Install packages, pip install .

--Windows Installtion Instructions--
Create virtual enviroment, py -m venv env
Activate virtual enviroment, .\env\Scripts\activate
If setuptools < 41.0.0 upgrade setuptools, pip install setuptools==41.0.0
Install packages, pip install .

NOTES: As of 7/28/20 Tensorflow 2.3.0 not compatible with numpy > 1.19.0, run pip install numpy==1.18.0 to resolve
