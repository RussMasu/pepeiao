from setuptools import setup

setup(
    name='pepeiao',
    author='Grady Weyenberg',
    author_email='grady.weyenberg@hawaii.edu',
    packages=['pepeiao'],
    license='MIT',
    install_requires=[
        'h5py',
        'keras',
        'librosa',
        'numpy',
        'pillow',
        'PyWavelets',
        'sounddevice',
        'numba==0.48.0',
        'scipy==1.4.1',
        'tensorflow',
		'setuptools==41.0.0',
        ],
    entry_points={
        'console_scripts':['pepeiao = pepeiao.__main__:_main'],
        'pepeiao_models': ['conv = pepeiao.models:conv_model',
                           'bulbul = pepeiao.models:bulbul',
                           'gru = pepeiao.models:gru_model',
                           'transfer = pepeiao.models:transfer']
        }
)
