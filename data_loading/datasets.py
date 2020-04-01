from torch.utils import data


class PairDataset(data.Dataset):
    """Combined source/target dataset for training using d-SNE.

    Attributes
    ----------
    src_X : PyTorch Tensor (N, H, W, C)
        Images corresponding to samples of source dataset.
    src_y : PyTorch Tensor (N, 1)
        Labels corresponding to samples of source dataset.
    tgt_X : PyTorch Tensor (M, H, W, C)
        Images corresponding to samples of target dataset.
    tgt_y : PyTorch Tensor (M, H, W, C)
        Labels corresponding to samples of target dataset.
    pair_idxs: List of pairs of ints
        Indexes for pairs of source and target samples.
    transforms : List of PyTorch transforms
        Pre-processing operations to apply to images when calling
        __getitem__.

    Methods
    -------
    __len__
        Reflects amount of available pairs of indices.
    __getitem__
        Gets pair of source and target images/labels.

    Notes
    -----
    d-SNE trains networks using two datasets simultaneously. Of note,
    with d-SNE's training procedure, the loss calculation differs for
    intraclass pairs (y_src == y_tgt) versus interclass pairs
    (y_src != y_tgt).

    By pre-determining pairs of images using a paired dataset, the ratio
    of intraclass and interclass pairs can be controlled. This would be
    more difficult to manage if images were sampled separately from each
    dataset.
    """

    def __init__(self, src_path, src_X_name, src_y_name,
                 tgt_path, tgt_X_name, tgt_y_name, sample_ratio=3,
                 src_num=-1, tgt_num=10, transforms=None):
        """Initialize dataset by sampling subsets of source/target.

        Parameters
        ----------
        src_path : str or Path object
            Path to HDF5 file for source dataset.
        src_X_name : str
            Name of image dataset, used as key into source HDF5 file.
        src_y_name : str
            Name of label dataset, used as key into source HDF5 file.
        src_num : int
            Number of samples to use per class for the source dataset.
        tgt_path : str or Path object
            Path to HDF5 file for target dataset.
        tgt_X_name : str
            Name of image dataset, used as key into target HDF5 file.
        tgt_y_name : str
            Name of label dataset, used as key into target HDF5 file.
        tgt_num : int
            Number of samples to use per class for the source dataset.
        sample_ratio : int
            Ratio between the number of intraclass pairs
            (y_src == y_tgt) to interclass pairs (y_src != y_tgt).
        transforms : list of PyTorch transforms
            Preprocessing operations to apply to images when sampling.
        """
        pass

    def _resample_data(self, X, y, N):
        """Limit sampling to N instances per class."""

        return X, y

    def _create_pairs(self, sample_ratio):
        """Enforce ratio of inter/intraclass pairs of samples."""
        pair_idxs = [None]

        return pair_idxs

    def __len__(self):
        pass

    def __getitem__(self, item):
        pass


class SingleDataset(data.Dataset):
    def __init__(self, data):
        pass
