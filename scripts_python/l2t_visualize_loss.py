#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import os

import torch
from scilpy.io.utils import add_reference_arg

from dwi_ml.io_utils import add_arg_existing_experiment_path
from dwi_ml.models.projects.learn2track_model import Learn2TrackModel
from dwi_ml.testing.testers import TesterOneInput
from dwi_ml.testing.utils import add_args_testing_subj_hdf5
from dwi_ml.testing.visu_loss import run_all_visu_loss
from dwi_ml.testing.visu_loss_utils import prepare_args_visu_loss, visu_checks


def prepare_argparser():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawTextHelpFormatter)
    add_arg_existing_experiment_path(p)
    add_args_testing_subj_hdf5(p, ask_input_group=True)
    g = p.add_mutually_exclusive_group()
    g.add_argument('--streamlines_group',
                   help="Streamlines group in the hdf5 to use.")
    g.add_argument('--streamlines_file',
                   help="Optionally, instead of using streamlines in the "
                        "hdf5, you may \nprovide your own streamlines to use."
                        "\nUse with care: they must correspond with the "
                        "hdf5's input data. \nOffered for easier "
                        "visualisation of sub-divisions of your testing \n"
                        "tractogram.")
    prepare_args_visu_loss(p)
    add_reference_arg(p)
    return p


def main():
    p = prepare_argparser()
    args = p.parse_args()

    # Checks on experiment options
    if args.out_dir is None:
        args.out_dir = os.path.join(args.experiment_path, 'visu_loss')
    if not os.path.isdir(args.experiment_path):
        p.error("Experiment {} not found.".format(args.experiment_path))

    # Checks on visu options
    names = visu_checks(args, p)

    # Loggers
    sub_logger_level = args.logging.upper()
    if sub_logger_level == 'DEBUG':
        sub_logger_level = 'INFO'
    logging.getLogger().setLevel(level=args.logging)

    # Device
    device = (torch.device('cuda') if torch.cuda.is_available() and
              args.use_gpu else None)

    # 1. Load model
    logging.debug("Loading model.")
    if args.use_latest_epoch:
        model_dir = os.path.join(args.experiment_path, 'best_model')
    else:
        model_dir = os.path.join(args.experiment_path, 'checkpoint/model')
    model = Learn2TrackModel.load_model_from_params_and_state(
        model_dir, log_level=sub_logger_level)
    model.set_context('visu')

    # 2. Load data through the tester
    tester = TesterOneInput(
        model=model, batch_size=args.batch_size, device=device,
        subj_id=args.subj_id, hdf5_file=args.hdf5_file,
        subset_name=args.subset, volume_group=args.input_group)

    run_all_visu_loss(tester, model, args, names)


if __name__ == '__main__':
    main()
