#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import os.path

import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
from dipy.io.streamline import save_tractogram
from dipy.io.utils import is_header_compatible

from scilpy.io.utils import assert_inputs_exist, assert_outputs_exist, \
    load_tractogram_with_reference, add_verbose_arg, add_overwrite_arg

from dwi_ml.data.hdf5.utils import add_nb_blocs_connectivity_arg, \
    format_nb_blocs_connectivity
from dwi_ml.data.processing.streamlines.post_processing import \
    compute_triu_connectivity_from_blocs, find_streamlines_with_chosen_connectivity


def _build_arg_parser():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('in_volume',
                   help='Input nifti volume. Only used to get the shape of the '
                        'volume.')
    p.add_argument('streamlines',
                   help='Tractogram (trk or tck).')
    add_nb_blocs_connectivity_arg(p)
    p.add_argument('out_file',
                   help="Out .npy file.")
    p.add_argument('--binary', action='store_true',
                   help="If set, saves the result as binary. Else, the "
                        "streamline count is saved.")
    p.add_argument('--show_now', action='store_true',
                   help="If set, shows the matrix with matplotlib.")

    g = p.add_argument_group("Investigation of the matrix:")
    g.add_argument('--save_biggest', metavar='filename',
                   help="If set, saves the biggest bundle (as tck or trk).")
    g.add_argument('--save_smallest', metavar='filename',
                   help="If set, saves the smallest (non-zero) bundle "
                        "(as tck or trk).")

    add_verbose_arg(p)
    add_overwrite_arg(p)

    return p


def main():
    p = _build_arg_parser()
    args = p.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    args.connectivity_nb_blocs = format_nb_blocs_connectivity(
        args.connectivity_nb_blocs)

    assert_inputs_exist(p, [args.in_volume, args.streamlines])
    assert_outputs_exist(p, args, [args.out_file],
                         [args.save_biggest, args.save_smallest])

    ext = os.path.splitext(args.streamlines)[1]
    if ext == '.trk':
        args.reference = None
        if not is_header_compatible(args.streamlines, args.in_volume):
            p.error("Streamlines not compatible with chosen volume.")
    else:
        args.reference = args.in_volume
    in_sft = load_tractogram_with_reference(p, args, args.streamlines)
    in_sft.to_vox()
    in_sft.to_corner()
    in_img = nib.load(args.in_volume)

    tmp_binary = args.binary
    if args.binary and (args.save_biggest or args.save_smallest):
        tmp_binary = False

    matrix, start_blocs, end_blocs = compute_triu_connectivity_from_blocs(
        in_sft.streamlines, in_img.shape, args.connectivity_nb_blocs,
        binary=tmp_binary)

    # Options to try to investigate the connectivity matrix:
    if args.save_biggest is not None:
        i, j = np.unravel_index(np.argmax(matrix, axis=None), matrix.shape)
        print("Saving biggest bundle: {} streamlines.".format(matrix[i, j]))
        biggest = find_streamlines_with_chosen_connectivity(
            in_sft.streamlines, i, j, start_blocs, end_blocs)
        sft = in_sft.from_sft(biggest, in_sft)
        save_tractogram(sft, args.save_biggest)

    if args.save_smallest is not None:
        tmp_matrix = np.ma.masked_equal(matrix, 0)
        i, j = np.unravel_index(tmp_matrix.argmin(axis=None), matrix.shape)
        print("Saving smallest bundle: {} streamlines.".format(matrix[i, j]))
        biggest = find_streamlines_with_chosen_connectivity(
            in_sft.streamlines, i, j, start_blocs, end_blocs)
        sft = in_sft.from_sft(biggest, in_sft)
        save_tractogram(sft, args.save_smallest)

    if tmp_binary is False and args.binary:
        matrix = matrix > 0

    # Save results.
    np.save(args.out_file, matrix)

    if args.show_now:
        plt.imshow(matrix)
        plt.colorbar()

        if not args.binary:
            plt.figure()
            plt.imshow(matrix > 0)
            plt.title('Binary')
        plt.show()


if __name__ == '__main__':
    main()



