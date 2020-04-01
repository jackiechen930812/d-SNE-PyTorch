import h5py
import numpy as np
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
        Reflect amount of available pairs of indices.
    __getitem__
        Get pair of source and target images/labels.

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
        super().__init__()
        self.transforms = transforms

        with h5py.File(src_path, "r") as f_s, h5py.File(tgt_path, "r") as f_t:
            # Read datasets from HDF5 file pointers
            src_X, src_y = f_s[src_X_name][()], f_s[src_y_name][()]
            tgt_X, tgt_y = f_t[tgt_X_name][()], f_t[tgt_y_name][()]

            # Sample datasets using configuration parameters
            self.src_X, self.src_y = self._resample_data(src_X, src_y, src_num)
            self.tgt_X, self.tgt_y = self._resample_data(tgt_X, tgt_y, tgt_num)
            self.intra_idxs, self.inter_idxs = self._create_pairs(sample_ratio)
            self.full_idxs = np.concatenate((self.intra_idxs, self.inter_idxs))

            # Sort as to allow shuffling to be performed by the DataLoader
            self.full_idxs = self.full_idxs[np.lexsort((self.full_idxs[:, 1],
                                                        self.full_idxs[:, 0]))]

    def _resample_data(self, X, y, N):
        """Limit sampling to N instances per class."""
        if N > 0:
            # Split labels into set of indexes for each class
            class_idxs = [np.where(y == c)[0] for c in np.unique(y)]

            # Shuffle each of sets of indexes
            [np.random.shuffle(i) for i in class_idxs]

            # Take N indexes, or fewer if total is less than N
            subset_idx = [i[:N] if len(i) >= N else i for i in class_idxs]

            # Use advanced indexing to get subsets of X and y
            idxs = np.array(subset_idx).ravel()
            np.random.shuffle(idxs)
            X, y = X[idxs], y[idxs]

        return X, y

    def _create_pairs(self, sample_ratio):
        """Enforce ratio of inter/intraclass pairs of samples."""

        # Broadcast target/source labels into mesh grid
        # `source` -> (N, 1) broadcast to (N, M)
        # `target` -> (1, M) broadcast to (N, M)
        target, source = np.meshgrid(self.tgt_y, self.src_y)

        # Find index pairs (i_S, i_T) for where src_y == tgt_y
        intra_pair_idxs = np.argwhere(source == target)

        # Find index pairs (i_S, i_T) for where src_y != tgt_y
        inter_pair_idxs = np.argwhere(source != target)

        # Randomly sample the interclass pairs to meet desired ratio
        if sample_ratio > 0:
            n_interclass = sample_ratio * len(intra_pair_idxs)
            np.random.shuffle(inter_pair_idxs)
            inter_pair_idxs = inter_pair_idxs[:n_interclass]

            # Sort as to allow shuffling to be performed by the DataLoader
            inter_pair_idxs = inter_pair_idxs[
                np.lexsort((inter_pair_idxs[:, 1], inter_pair_idxs[:, 0]))
            ]

        return intra_pair_idxs, inter_pair_idxs

    def __len__(self):
        """Reflect amount of available pairs of indices."""
        return len(self.full_idxs)

    def __getitem__(self, idx):
        """Get pair of source and target images/labels."""
        src_idx, tgt_idx = self.full_idxs[idx]

        X_src, y_src = self.src_X[src_idx], self.src_y[src_idx]
        X_tgt, y_tgt = self.tgt_X[tgt_idx], self.tgt_y[tgt_idx]

        for transform in self.transforms:
            X_src, X_tgt = transform(X_src), transform(X_tgt)

        return X_src, y_src, X_tgt, y_tgt


class SingleDataset(data.Dataset):
    def __init__(self, data):
        pass
