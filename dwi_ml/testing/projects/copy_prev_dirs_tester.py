# -*- coding: utf-8 -*-
import logging

import torch

from dwi_ml.data.processing.streamlines.data_augmentation import \
    resample_or_compress
from dwi_ml.models.projects.copy_previous_dirs import CopyPrevDirModel
from dwi_ml.testing.testers import Tester
from dwi_ml.testing.utils import prepare_dataset_one_subj


class TesterCopyPrevDir(Tester):
    def __init__(self, model: CopyPrevDirModel,
                 streamline_group, batch_size: int = None,
                 device: torch.device = None):
        super().__init__('no_experiment', model, batch_size, device)
        self.streamline_group = streamline_group

    @property
    def _volume_groups(self):
        return []

    @property
    def streamlines_group(self):
        return self.streamline_group

    def _prepare_inputs_at_pos(self, streamlines):
        return None
