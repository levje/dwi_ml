#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

import h5py
import torch
import numpy as np
from dipy.io.stateful_tractogram import StatefulTractogram

from dwi_ml.data.dataset.multi_subject_containers import \
    MultiSubjectDataset, MultisubjectSubset
from dwi_ml.data.dataset.mri_data_containers import MRIData, LazyMRIData
from dwi_ml.data.dataset.single_subject_containers import \
    SubjectData, LazySubjectData
from dwi_ml.data.dataset.subjectdata_list_containers import \
    SubjectsDataList, LazySubjectsDataList
from dwi_ml.data.dataset.streamline_containers import \
    SFTData, LazySFTData
from dwi_ml.unit_tests.utils.expected_values import (
    TEST_EXPECTED_SUBJ_NAMES, TEST_EXPECTED_STREAMLINE_GROUPS,
    TEST_EXPECTED_VOLUME_GROUPS, TEST_EXPECTED_NB_STREAMLINES,
    TEST_EXPECTED_MRI_SHAPE, TEST_EXPECTED_NB_SUBJECTS,
    TEST_EXPECTED_NB_FEATURES)
from dwi_ml.unit_tests.utils.data_and_models_for_tests import \
    fetch_testing_data

dps_key_1 = 'mean_color_dps'
dps_key_2 = 'mock_2d_dps'


def test_multisubjectdataset(script_runner):
    data_dir = fetch_testing_data()

    hdf5_filename = os.path.join(data_dir, 'hdf5_file.hdf5')

    _non_lazy_version(hdf5_filename)
    logging.debug('\n\n')
    _lazy_version(hdf5_filename)


def _verify_multisubject_dataset(dataset):
    logging.debug("    Testing properties of the main MultiSubjectDataset.")
    assert isinstance(dataset, MultiSubjectDataset)
    assert dataset.volume_groups == TEST_EXPECTED_VOLUME_GROUPS
    assert dataset.streamline_groups == TEST_EXPECTED_STREAMLINE_GROUPS
    assert dataset.nb_features == TEST_EXPECTED_NB_FEATURES


def _verify_training_set(training_set):
    logging.debug("    Testing properties of the training set.")

    assert isinstance(training_set, MultisubjectSubset)
    assert training_set.nb_subjects == TEST_EXPECTED_NB_SUBJECTS
    assert training_set.volume_groups == TEST_EXPECTED_VOLUME_GROUPS
    assert training_set.streamline_groups == TEST_EXPECTED_STREAMLINE_GROUPS
    assert training_set.nb_features == TEST_EXPECTED_NB_FEATURES
    assert training_set.total_nb_streamlines == TEST_EXPECTED_NB_STREAMLINES
    # logging.debug("  - Lengths: {}".format(training_set.streamline_lengths))
    # logging.debug("  - Lengths_mm: {}"
    #               .format(training_set.streamline_lengths_mm))
    # logging.debug("  - Streamline ids per subj: {}"
    #               .format(training_set.streamline_ids_per_subj))


def _verify_data_list(subj_data_list):
    assert len(subj_data_list) == TEST_EXPECTED_NB_SUBJECTS


def _verify_subj_data(subj, subj_number):
    assert subj.subject_id == TEST_EXPECTED_SUBJ_NAMES[subj_number]
    assert subj.volume_groups == TEST_EXPECTED_VOLUME_GROUPS
    assert subj.streamline_groups == TEST_EXPECTED_STREAMLINE_GROUPS
    assert subj.nb_features == TEST_EXPECTED_NB_FEATURES


def _verify_mri(mri_data, training_set, group_number):
    expected_shape = TEST_EXPECTED_MRI_SHAPE[group_number]
    device = torch.device('cpu')

    # Non-lazy: getting data as tensor directly.
    # Lazy: it should load it.
    assert isinstance(mri_data.get_data_as_tensor(device), torch.Tensor)
    assert list(mri_data.get_data_as_tensor(device).shape) == expected_shape

    # This should also get it.
    volume0 = training_set.get_volume_verify_cache(0, 0)
    assert isinstance(volume0, torch.Tensor)


def _verify_sft_data(sft_data, group_number):
    expected_nb = TEST_EXPECTED_NB_STREAMLINES[group_number]
    assert len(sft_data.as_sft()) == expected_nb
    expected_mock_2d_dps = np.random.RandomState(42).rand(expected_nb, 42)

    # First streamline's first coordinate:
    # Also verifying accessing by index
    list_one = sft_data.as_sft([0])
    assert type(list_one) == StatefulTractogram
    assert len(list_one) == 1
    assert len(list_one.streamlines[0][0, :]) == 3  # a x, y, z coordinate

    # Both dps should be in the data_per_streamline
    # of the sft. Also making sure that the data is
    # the same as expected.
    assert dps_key_1 in list_one.data_per_streamline.keys()
    assert dps_key_2 in list_one.data_per_streamline.keys()
    assert np.allclose(
        list_one.data_per_streamline[dps_key_2][0],
        expected_mock_2d_dps[0])

    # Assessing by slice
    list_4 = sft_data.as_sft(slice(0, 4))
    assert len(list_4) == 4

    # Same as above, but with slices. Both dps
    # should be in the data_per_streamline and
    # the data should be the same as expected.
    assert dps_key_1 in list_4.data_per_streamline.keys()
    assert dps_key_2 in list_4.data_per_streamline.keys()
    assert np.allclose(
        list_4.data_per_streamline[dps_key_2][0:4],
        expected_mock_2d_dps[0:4])


def _non_lazy_version(hdf5_filename):
    logging.debug("-------------- NON-LAZY version -----------------")
    logging.debug("   Initializing dataset")
    dataset = MultiSubjectDataset(hdf5_filename, lazy=False,
                                  log_level=logging.DEBUG)
    dataset.load_data()
    _verify_multisubject_dataset(dataset)

    training_set = dataset.training_set
    assert training_set.cache_size == 0
    _verify_training_set(training_set)

    logging.debug("    Testing properties of the SubjectDataList.")
    subj_data_list = training_set.subjs_data_list
    assert isinstance(subj_data_list, SubjectsDataList)
    _verify_data_list(subj_data_list)

    logging.debug("    Testing properties of a SingleSubjectDataset.")
    subj0 = training_set.subjs_data_list[0]
    assert isinstance(subj0, SubjectData)
    _verify_subj_data(subj0, subj_number=0)

    logging.debug("    Testing properties of his first MRIData.")
    mri_data = subj0.mri_data_list[0]
    assert isinstance(mri_data, MRIData)
    # Non-lazy: the _data should already be loaded.
    assert isinstance(mri_data._data, torch.Tensor)
    _verify_mri(mri_data, training_set, group_number=0)

    logging.debug("    Testing properties of his first SFTData.")
    sft_data = subj0.sft_data_list[0]
    assert isinstance(sft_data, SFTData)
    _verify_sft_data(sft_data, group_number=0)


def _lazy_version(hdf5_filename):
    logging.debug("-------------- LAZY version -----------------")
    dataset = MultiSubjectDataset(hdf5_filename,
                                  lazy=True, cache_size=1,
                                  log_level=logging.DEBUG)
    dataset.load_data()
    _verify_multisubject_dataset(dataset)

    training_set = dataset.training_set
    assert training_set.cache_size == 1
    _verify_training_set(training_set)

    print("    Testing properties of the LAZY SubjectDataList.")
    subj_data_list = training_set.subjs_data_list
    assert isinstance(subj_data_list, LazySubjectsDataList)
    _verify_data_list(subj_data_list)

    logging.debug("    Testing properties of a LAZY SingleSubjectDataset.")

    # Getting subject and adding handle to allow loading.
    subj0 = training_set.subjs_data_list.get_subj_with_handle(0)
    assert isinstance(subj0, LazySubjectData)
    _verify_subj_data(subj0, subj_number=0)

    logging.debug("    Testing properties of his first LAZY MRIData.")
    mri_data = subj0.mri_data_list[0]
    assert isinstance(mri_data, LazyMRIData)
    # Lazy: data should be a hdf5 group)
    assert isinstance(mri_data._data, h5py.Dataset)
    _verify_mri(mri_data, training_set, group_number=0)

    logging.debug("    Testing properties of his first Lazy SFTData.")
    sft_data = subj0.sft_data_list[0]
    assert isinstance(sft_data, LazySFTData)
    _verify_sft_data(sft_data, group_number=0)


if __name__ == '__main__':
    logging.getLogger().setLevel(level='DEBUG')
    test_multisubjectdataset()
