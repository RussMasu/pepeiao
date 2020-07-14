import argparse
import concurrent.futures
import itertools
import logging
import pkg_resources
import random

import numpy as np
import keras

from pepeiao.feature import Spectrogram
from pepeiao.parsers import make_train_parser as _make_parser
import pepeiao.util

# from matplotlib import pyplot as plt  # not in setup.py

_LOGGER = logging.getLogger(__name__)


# def _make_parser(parser=None):
#     if parser is None:
#         parser = argparse.ArgumentParser()
#     parser.add_argument('-w', '--width', type=float, default=0.5)
#     parser.add_argument('-o', '--offset', type=float, default=0.125)
#     parser.add_argument('-q', '--quiet', action='store_true')
#     parser.add_argument('-n', '--num-validation', type=float, default=0.25,
#                         help='An integer number of training files to use as a validation set, or if less than one, use as a proportion.')
#     parser.add_argument('-p', '--proportion-ones', type=float,
#                         help='Desired proportion of "one" labels in training/validation data')
#     parser.add_argument('-b', '--batch-size', default=64, type=int,
#                         help='Training batch size')
#     parser.add_argument('model', choices=pepeiao.util.get_models())
#     parser.add_argument('feature', nargs='+',
#                         help='Preprocessed feature files for training')
#     parser.add_argument('output', help='Filename for fitted model in (.h5)')
#     return parser

class DataGenerator(keras.utils.Sequence):
    def __init__(self, feature_list, width, offset, batch_size=128, desired_prop_ones=None):
        self.feature_list = feature_list
        self.width = width
        self.offset = offset
        self.batch_size = batch_size
        self.desired_prop_ones = desired_prop_ones

        self.count_total = 0
        self.count_ones = 0
        self.keep_prob = 1.0

        feature = pepeiao.feature.load_feature(feature_list[0])
        feature.set_windowing(width, offset)

        self.shape = feature._get_window(0).shape

    def __len__(self):
        return 100  # 100 batches per epoch

    def __getitem__(self, idx):
        '''Generate batch idx'''

        data = None
        labels = None

        data = np.empty((self.batch_size, *reversed(self.shape)), dtype=float)
        labels = np.empty(self.batch_size, dtype=float)

        feature_list = self.feature_list[:]
        feature_list = itertools.cycle(random.shuffle(feature_list))

        for filename in feature_list:
            feature = pepeiao.feature.load_feature(filename)
            feature.set_windowing(self.width, self.offset)
            for wind, lab in feature.shuffled_windows():
                if tuple(reversed(wind.shape)) != data.shape[1:]:
                    continue
                if lab > 0.5 or (self.desired_prop_ones is None):
                    keep = True
                    self.count_ones += 1
                else:
                    keep = random.random() < self.keep_prob
                if keep:
                    self.count_total += 1
                    index = (self.count_total - 1) % self.batch_size
                    data[index] = np.transpose(wind)
                    labels[index] = lab
                    if index + 1 == self.batch_size:
                        current_prop_ones = self.count_ones / self.count_total
                        if (current_prop_ones - self.desired_prop_ones) > 0.02:
                            self.keep_prob = min(self.keep_prob + 0.05, 1.0)
                        elif (current_prop_ones - self.desired_prop_ones) < 0.02:
                            self.keep_prob = max(self.keep_prob - 0.05, 0.01)
                        return data, labels

    def __del__(self):
        print('Generated {:d} windows, with {:.3%} true labels.'.format(self.count_total,
                                                                        self.count_ones / self.count_total))


def list_cycle(iterable):
    lst = list(iterable)
    while True:
        yield from lst
        _LOGGER.warn('\nExausted iterable. Restarting at beginning.\n')

def window_length():
    length = 418
    return length

def data_generator(model, feature_list, width, offset, channels, batch_size=100, desired_prop_ones=None):
    count_total = 0
    count_ones = 0
    keep_prob = 1.0
    result_idx = 0

    keep = True
    windows = None
    labels = None
    if desired_prop_ones and (desired_prop_ones < 0 or desired_prop_ones > 1):
        raise ValueError('desired proportion of ones is not a valid proportion.')

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

        # train_list = itertools.cycle(feature_list)
        train_list = list_cycle(feature_list)
        current_future = executor.submit(pepeiao.feature.load_feature, next(train_list))
        # for feat_file in train_list:
        for feat_file in train_list:
            next_future = executor.submit(pepeiao.feature.load_feature, feat_file)
            current_feature = current_future.result()
            current_feature.set_windowing(width, offset, model)
            _LOGGER.info('Loaded feature %s.', current_feature.file_name)
            current_future = next_future

            if windows is None:  # initilize result arrays on first iteration
                shape = list(current_feature._get_window(0).shape)
                shape[0] = window_length()
                windows = np.empty((batch_size, *shape, channels), dtype=float)
                labels = np.empty(batch_size, dtype=float)

            ## take items from the feature and put them into the arrays until full then yield arrays
            if desired_prop_ones is None:
                for wind, lab in current_feature.shuffled_windows():
                    if wind.shape[1] != windows.shape[2]:
                        continue
                    s_win = wind[47:47 + window_length(), ]
                    # find min value
                    s_win = s_win - np.amin(s_win)
                    # log10 transform values in window
                    #s_win = s_win+1
                    #s_win = np.log10(s_win)
                    # clone data into separate channels
                    sample_window = np.repeat(s_win[..., np.newaxis], channels, -1)
                    # write image to window array
                    windows[result_idx] = sample_window
                    labels[result_idx] = lab
                    result_idx += 1
                    if (result_idx % batch_size) == 0:
                        result_idx = 0
                        yield windows, labels
            else:  # keep track of proportion of ones
                for wind, lab in current_feature.shuffled_windows():
                    if wind.shape[1] != windows.shape[2]:
                        continue
                    if lab >= 0.5:
                        keep = True
                        count_ones += 1
                    else:
                        keep = random.random() < keep_prob
                    if keep:
                        count_total += 1
                        windows[result_idx] = wind[47:47 + window_length(), ]
                        labels[result_idx] = lab
                        result_idx += 1
                        if (result_idx % batch_size)== 0:
                            result_idx = 0
                            yield windows, labels

                    current_prop_ones = count_ones / count_total
                    if (current_prop_ones - desired_prop_ones) > 0.05:
                        keep_prob = min(keep_prob + 0.05, 1.0)
                    elif (current_prop_ones - desired_prop_ones) < 0.05:
                        keep_prob = max(keep_prob - 0.05, 0.0)


# def grouper(iterable, n, fillvalue=None):
#     'Collect data into fixed-length chunks or blocks (from itertools recipes)'
#     # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
#     args = [iter(iterable)] * n
#     return itertools.zip_longest(*args, fillvalue=fillvalue)

def main(args):
    # level = logging.WARNING if args.quiet else logging.INFO

    # _LOGGER.setLevel(level)
    # _LOGGER.debug(args)
    channel = 1
    if str(args.model) == "transfer":
        channel = 3

    if args.num_validation >= 1.0:
        if args.num_validation > len(args.feature):
            raise ValueError('--num-validation argument is greater than the number of available files')
        n_valid = int(args.num_validation)
    elif args.num_validation >= 0.0:
        n_valid = int(args.num_validation * len(args.feature))
    else:
        raise ValueError('--num-validation argument is not positive')

    if n_valid > 0.3 * len(args.feature):
        _LOGGER.warning('Using more than 30% of files as validation data.')

    matching_models = list(pkg_resources.iter_entry_points('pepeiao_models', args.model))

    training_set = data_generator(matching_models[0], args.feature[:-n_valid], args.width, args.offset, channel,
                                  args.batch_size, args.proportion_ones)

    validation_set = data_generator(matching_models[0], args.feature[-n_valid:], args.width, args.offset, channel,
                                    args.batch_size, args.proportion_ones)

    if len(matching_models) > 1:
        _LOGGER.warn('Multiple model objects match name %s', args.model)
    # unpack training_set into images and labels
    (trainImages, trainLabels) = next(training_set)
    (validationImages, validationLabels) = next(validation_set)
    """
    #TODO
    plt.imshow(trainImages[0], interpolation='nearest')
    plt.gray()
    plt.show()
    """
    # remove batch size from input tensor
    input_shape = trainImages.shape[1:]
    # calls arg.model in model.py
    model = matching_models[0].load()(input_shape)  # expecting tensorshape array
    try:
        history = model.fit_generator(  # may want to use model.fit instead
            training_set,
            steps_per_epoch=150,
            shuffle=False,
            epochs=100,
            verbose=1,  # 0-silent, 1-progessbar, 2-1line
            validation_data=validation_set,
            validation_steps=100,
            callbacks=[keras.callbacks.EarlyStopping(patience=6)],
        )
    except KeyboardInterrupt:
        print('\nExiting on user request.')
    model.save(args.output)
    print('Wrote model to', args.output)


if __name__ == '__main__':
    logging.basicConfig()
    parser = _make_parser()
    args = parser.parse_args()
    main(args)
