#!/usr/bin/env python
import logging
import os
import tempfile

from dwi_ml.data.dataset.multi_subject_containers import MultiSubjectDataset
from dwi_ml.training.trainers import DWIMLTrainerOneInput
from dwi_ml.tests.utils import (ModelForTest, create_test_batch_sampler,
                                create_batch_loader, fetch_testing_data,
                                TrackingModelForTestWithPD)

SAVE_RESULT_SFT_NII = False
ref = None
batch_size = 50
batch_size_units = 'nb_streamlines'


def test_trainer_and_models():
    data_dir = fetch_testing_data()

    hdf5_filename = os.path.join(data_dir, 'hdf5_file.hdf5')

    # Initializing dataset
    dataset = MultiSubjectDataset(hdf5_filename, lazy=False)
    dataset.load_data()

    # Initializing model 1 + associated batch sampler.
    logging.info("\n\n---------------TESTING MODEL # 1 -------------")
    model = ModelForTest()
    batch_sampler, batch_loader = _create_sampler_and_loader(dataset, model)

    # Start tests
    trainer = _create_trainer(batch_sampler, batch_loader, model)
    trainer.train_and_validate()

    # Initializing model 2
    logging.info("\n\n---------------TESTING MODEL # 2 -------------")
    model2 = TrackingModelForTestWithPD()
    batch_sampler, batch_loader = _create_sampler_and_loader(dataset, model)

    # Start tests
    trainer2 = _create_trainer(batch_sampler, batch_loader, model2)
    trainer2.train_and_validate()


def _create_sampler_and_loader(dataset, model):

    # Initialize batch sampler
    logging.debug('\nInitializing sampler...')
    batch_sampler = create_test_batch_sampler(
        dataset, batch_size=batch_size,
        batch_size_units='nb_streamlines', log_level=logging.WARNING)

    batch_loader = create_batch_loader(dataset, model,
                                       log_level=logging.WARNING,
                                       wait_for_gpu=False)

    return batch_sampler, batch_loader


def _create_trainer(batch_sampler, batch_loader, model):
    tmp_dir = tempfile.TemporaryDirectory()

    trainer = DWIMLTrainerOneInput(
        batch_sampler=batch_sampler,
        batch_loader=batch_loader,
        model=model, experiments_path=tmp_dir.name, experiment_name='test',
        log_level='DEBUG',
        max_batches_per_epoch_training=2,
        max_batches_per_epoch_validation=None, max_epochs=2, patience=None,
        use_gpu=False)
    # Note. toDo Test fails with nb_cpu_processes=1. Why??

    return trainer


if __name__ == '__main__':
    logging.getLogger().setLevel(level='INFO')
    test_trainer_and_models()
