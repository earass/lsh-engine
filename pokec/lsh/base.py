from collections import defaultdict


class SetFinder:

    def __init__(self):
        self.weights = {}
        self.parents = {}

    def __getitem__(self, object):
        if object not in self.parents:
            self.parents[object] = object
            self.weights[object] = 1
            return object

        path = [object]
        root = self.parents[object]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        for ancestor in path:
            self.parents[ancestor] = root
        return root

    def __iter__(self):
        return iter(self.parents)

    def union(self, *objects):
        """Find the sets containing the objects and merge them all."""
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest

    def sets(self):
        """Return a list of each disjoint set"""
        ret = defaultdict(list)
        for k, _ in self.parents.items():
            ret[self[k]].append(k)
        return ret.values()


class Signature:
    """Creates signatures for sets/tuples using minhash."""

    def __init__(self, dim):
        self.dim = dim
        self.hashes = self.hash_functions()

    def hash_functions(self):
        def hash_generator(n):
            return lambda x: hash("hashit" + str(n) + str(x) + "hashit")
        return [hash_generator(_) for _ in range(self.dim)]

    def signature(self, s):
        """Returns minhash signature for set s"""
        sig = [float("inf")] * self.dim
        for hash_ix, hash_fn in enumerate(self.hashes):
            sig[hash_ix] = min(hash_fn(value) for value in s)
        return sig


class Hashing(object):
    """Locality sensitive hashing.  Uses a banding approach to hash
    similar signatures to the same buckets."""
    def __init__(self, length, threshold):
        self.length = length
        self.threshold = threshold
        self.bandwidth = self.get_bandwidth(length, threshold)

    def hash(self, sig):
        """Generate hashvals for this signature"""
        for band in zip(*(iter(sig),) * self.bandwidth):
            yield hash("hashit" + str(band) + "tihsah")

    @staticmethod
    def get_bandwidth(n, t):
        best = n, 1
        minerr = float("inf")
        for r in range(1, n + 1):
            try:
                b = 1. / (t ** r)
            except Exception as e:
                return best
            err = abs(n - b * r)
            if err < minerr:
                best = r
                minerr = err
        return best

    def get_threshold(self):
        r = self.bandwidth
        b = self.length / r
        return (1. / b) ** (1. / r)

    def get_n_bands(self):
        return int(self.length / self.bandwidth)


class Grouping:
    def __init__(self, width=10, threshold=0.5):
        self.width = width
        self.finder = SetFinder()
        self.signer = Signature(width)
        self.hasher = Hashing(width, threshold)
        self.hashmaps = [defaultdict(list) for _ in range(self.hasher.get_n_bands())]

    def add_set(self, s, label):
        self.finder[label]

        sig = self.signer.signature(s)

        for band_idx, hshval in enumerate(self.hasher.hash(sig)):
            self.hashmaps[band_idx][hshval].append(label)
            self.finder.union(label, self.hashmaps[band_idx][hshval][0])

    def get_sets(self):
        return self.finder.sets()
