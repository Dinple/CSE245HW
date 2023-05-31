import numpy as np

class GMM:
    """Gaussian Mixture Model in High Dimensional Space.
    Takes one input, and use it as the mean of a Gaussian distribution.
    Takes another input, and use it as the standard deviation of the same Gaussian distribution (for all dimensions).
    """

    def __init__(self, init_sample, init_std):
        """Initialize the GMM.
        Args:
            init_sample: A 1D numpy array, the initial sample.
            init_std: A 1D numpy array, standard_deviation along each dimension.
        """
        self.mean = init_sample
        self.std = init_std

    def sample(self, n):
        """Sample from the GMM.
        Args:
            n: An integer, the number of samples.
        Returns:
            A 2D numpy array, the samples.
        """
        return np.random.normal(self.mean, self.std, (n, len(self.mean)))
    
def main():
    gmm = GMM(np.array([1, 1, 1, 1]), np.array([1, 2, 3]))
    print(gmm.sample(10))

if __name__ == '__main__':
    main()