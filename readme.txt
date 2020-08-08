

--Linux Installation Instructions--
Create virtual environment, python3 -m venv env
Activate virtual environment, source env/bin/activate
If setuptools < 41.0.0 upgrade setuptools, pip install setuptools==41.0.0
NOTE: Tensorflow 2.3.0 not compatible with numpy > 1.19.0, run pip install numpy==1.18.0 to resolve
Install packages, pip install .
Grant permissions such that pepeiao.sh is executable

--Windows Installation Instructions--
Create virtual environment, py -m venv env
Activate virtual environment, .\env\Scripts\activate
If setuptools < 41.0.0 upgrade setuptools, pip install setuptools==41.0.0
Install packages, pip install .

--Linux Operation Instructions--
Activate virtual environment, source env/bin/activate
Run pepeiao bash script to start program, ./pepeiao.sh
