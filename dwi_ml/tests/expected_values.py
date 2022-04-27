#!/usr/bin/env python

# Values corresponding to the testing data, as of Apr 27, 2022.

TEST_EXPECTED_VOLUME_GROUPS = ['input', 'wm_mask']
TEST_EXPECTED_STREAMLINE_GROUPS = ['streamlines']
TEST_EXPECTED_NB_FEATURES = [2, 1]  # input = t1 + fa. wm_mask = wm.
TEST_EXPECTED_NB_STREAMLINES = [3827]  # from the Fornix.trk file
TEST_EXPECTED_NB_SUBJECTS = 1
TEST_EXPECTED_SUBJ_NAMES = ['subjX']
TEST_EXPECTED_MRI_SHAPE = [[138, 168, 134, 2], [138, 168, 134, 1]]
