import argparse
import csv
import sys
import logging
import librosa
import os
import re

from pepeiao.constants import _RAVEN_HEADER, _SELECTION_KEY, _BEGIN_KEY, _END_KEY, _FILE_KEY
from pepeiao.train import window_length
import pepeiao.feature
import pepeiao.models
import pepeiao.util
from pepeiao.parsers import make_predict_parser as _make_parser
from pathlib import Path
import keras.layers

_LOGGER = logging.getLogger(__name__)

def predict(feature, model, channel, window_size, arr, out_stream=sys.stdout):
    """Write predicted times to console and to pred list"""
    feature.predict(model, channel, window_size)
    writer = csv.DictWriter(out_stream, fieldnames=[
        _SELECTION_KEY, _BEGIN_KEY, _END_KEY, _FILE_KEY],
    delimiter='\t')
    writer.writeheader()
    for idx, (start, end) in enumerate(feature.time_intervals, start=1):
        writer.writerow({_SELECTION_KEY: idx, _BEGIN_KEY: '{:.3f}'.format(start), _END_KEY: '{:.3f}'.format(end), _FILE_KEY: feature.file_name})
        arr.append((idx, '{:.3f}'.format(start), '{:.3f}'.format(end), feature.file_name))

def compare(selpath, filename, arr, epsilon):
    """Compares selection table to prediction list, returns list with (start_time, end_time, result)"""
    output = []
    selections = pepeiao.util.load_selections(selpath)
    # search for true positives and false negatives
    for selection in selections:
        if selection.get('view') == 'Spectrogram 1':
            start_t = float(selection.get('begin time (s)', default=None))
            end_t = float(selection.get('end time (s)', default=None))
            result = "FN"
            for item in arr:
                (arrID, start_p, end_p, file) = item
                if abs(float(start_p) - start_t) + abs(float(end_p) - end_t) < epsilon:
                    result = 'TP'
            output.append((float(start_t), float(end_t), result, filename))
    # search for false positives
    for item in arr:
        (arrID, start_p, end_p, file) = item
        result = 'FP'
        for selection in selections:
            if selection.get('view') == 'Spectrogram 1':
                start_t2 = float(selection.get('begin time (s)', default=None))
                end_t2 = float(selection.get('end time (s)', default=None))
                if abs(float(start_p) - start_t2) + abs(float(end_p) - end_t2) < epsilon:
                    result = 'TP'
        if result is 'FP':
            output.append((float(start_p), float(end_p), result, filename))
    # sort output by starting time
    output.sort(key=lambda x: x[0])
    return output

def compareToCSV(compareList, filename):
    "writes compare list to CSV file"
    # generate name for .csv file
    filepath = Path(filename)
    csvpath = filepath.with_suffix('.csv')
    # write data to csv file
    with open(csvpath, 'w', newline='') as csv_file:
        fileWriter = csv.writer(csv_file)
        header = list(['Begin Time (s)', 'End Times (s)', 'Result', 'Begin file'])
        fileWriter.writerow(header)
        for item in compareList:
            fileWriter.writerow(item)

def main(args):
    predictList = []  # list holding predictions
    channel = 1
    import keras.models
    try:
        model = keras.models.load_model(args.model, custom_objects={'_prob_bird': pepeiao.models._prob_bird})
        if model.name == "transfer":
            channel = 3
    except OSError as err:
        print("Failed to open model file: {}".format(args.model))
        return -1
    for filename in args.wav:
        feature = pepeiao.feature.Spectrogram(filename, args.selections)
        predict(feature, model, channel, window_length(), predictList)

        if args.selections is not None:
            # write results to csv file
            compareToCSV(compare(args.selections, filename, predictList, 2), filename)
            _LOGGER.info('Writing roc table')
            with open(os.path.basename(filename) + '.roc', 'w') as rocfile:
                print('true, pred', file=rocfile)
                for true, pred in feature.roc():
                    print(true, pred, sep=', ', file=rocfile)
                

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = _make_parser().parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print('Exiting on user interrupt.')
