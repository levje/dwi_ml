"""
Parameters for the yaml file:

sampling:
    batch:
        chunk_size: int
             Number of streamlines to sample together while creating the
             batches. If the size of the streamlines is known in terms of
             number of points (resampling has been done, and no compressing is
             done in the batch sampler), we iteratively add chunk_size
             streamlines to the batch until the total number of sampled
             timepoint reaches the max_batch_size. Else, the total number of
             streamlines in the batch will be 1*chunk_size.
        max_batch_size: int
             Number of streamline points per batch.
             The total number your computer will accept depends on the type of
             input data. You will need to test this value. Suggestion: 20000.
        nb_subjects_per_batch: int
             Maximum number of different subjects from which to load data in
             each batch. This should help avoid loading too many inputs in
             memory, particularly for lazy data. If null, we will use true
             random sampling. Suggestion: 5.
             Hint: Will influence the cache size if memory:cache_manager is
             used.
        cycles: int
             Relevant only if training:batch:nb_subject_per_batch is not null.
             Number of cycles before changing to new subjects (and thus new
             volumes). null is equivalent to 1.
    streamlines:
        processing:
            step_size: float
                 Resample all streamlines to this step size (in mm). If null,
                 train on streamlines as they are. Cannot be used together
                 with compress. Note that you probably may have already
                 resampled or compressed your data creating your dataset, but
                 you can use a different choice in the batch sampler if you
                 wish.
            compress: bool
                 If true, compress streamlines. Cannot be used together with
                 step_size. Once again, the choice can be different in the
                 batch sampler than chosen when creating the hdf5.
            normalize_directions: bool
                 If true, directions will be normalized. If the step size is
                 fixed, it shouldn't make any difference. If streamlines are
                 compressed, in theory you should normalize, but you could
                 hope that not normalizing could give back to the algorithm a
                 sense of distance between points.
        data_augmentation:
            noise_size: bool
                 Add random Gaussian noise to streamline coordinates with
                 given variance. This corresponds to the std of the Gaussian.
                 If step_size is not given, make sure it is smaller than your
                 step size to avoid flipping direction. Ex, you could choose
                 0.1 * step-size. Noise is truncated to +/- 2*noise_sigma and
                 to +/- 0.5 * step-size (if given). null or 0 both lead to no
                 added noise.
            noise_variability: bool
                 If this is given, a variation is applied to the noise_size to
                 have very noisy streamlines and less noisy streamlines. This
                 means that the real gaussian_size will be a random number
                 between [size - variability, size + variability]. null is the
                 same as 0.
            split_ratio: float
                 Percentage of streamlines to randomly split into 2, in each
                 batch (keeping both segments as two independent streamlines).
                 The reason for cutting is to help the ML algorithm to track
                 from the middle of WM by having already seen half-
                 streamlines. If you are using interface seeding, this is not
                 necessary.
            reverse_ratio: float
                 Percentage of streamlines to randomly reverse in each batch.

training:
    learning_rate: int
         Learning rate. Default: 0.001 (torch's default)
    weight_decay: float
         Add a weight decay penalty on the parameters. Default: 0.01.
         (torch's default).

    epochs:
        max_epochs: int
             Maximum number of epochs. Suggestion: 100.
        patience: int
             Use early stopping. Defines the number of epochs after which the
             model should stop if the loss hasn't improved. Suggestion: 20. If
             null, the model will continue for max_epochs.
        max_batches_per_epoch: int
              Maximum number of batches per epoch. Exemple: 10000. This will
              help avoid long epochs, to ensure that we save checkpoints
              regularly.

model:
    previous_dirs:
        nb_previous_dirs: int
             Concatenate X previous streamline directions to the input vector.
             Null is equivalent to 0.
    neighborhood:
        sphere_radius: float
             If not null, a neighborhood will be added to the input
             information. This neighborhood definition lies on a sphere. It
             will be a list of 6 positions (up, down, left, right, behind, in
             front) at exactly given radius around each point of the
             streamlines, in voxel space. **Can't be used together with
             grid_radius.
        grid_radius: int
             If not null, a neighborhood will be added to the input
             information. This neighborhood definition uses a list of points
             similar to the original voxel grid around each point of the
             streamlines. Ex: with radius 1, that's 27 points. With radius 2,
             that's 125 points. Radius is in voxel space. **Can't be used
             together with sphere_radius.

memory:
    lazy: bool
         If set, do not load all the dataset in memory at once. Load only what
         is needed for a batch.
    cache_size: int
         Relevant only if memory:lazy is used. Size of the cache in terms of
         number of length of the queue (i.e. number of volumes).
         NOTE: Real cache size will actually be twice this value as the
         training and validation subsets each have their cache.
    use_gpu: bool
         If set, all computations that can be avoided in the batch sampler
         (which is computed on CPU) will be skipped and should be performed
         by the user later on GPU. Ex: computing directions from the
         streamline coordinates, computing input interpolation, etc.
    nb_cpu_workers: int
         Number of parallel CPU workers.
    worker_interpolation: bool
         If set, if using nb_cpu_workers > 0, interpolation will be done on
         CPU by the workers instead of on the main thread using the chosen
         device.
    taskman_managed: bool
         If set, instead of printing progression, print taskman-relevant data.

randomization:
    rng: int
         Random experiment seed.

"""