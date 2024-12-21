import unittest
import numpy as np
from try_clustering import FaceClustering

class TestFaceClustering(unittest.TestCase):
    def setUp(self):
        self.faces = np.random.rand(20, 512)
        self.faces /= np.linalg.norm(self.faces, axis=1)[:, None]
        self.clustering = FaceClustering(self.faces)

        # Add explicit test embeddings
        self.simple_faces = np.array([
            [1, 0, 0],  # Cluster 1
            [0.99, 0.01, 0],
            [0.98, 0.02, 0],
            [0, 1, 0],  # Cluster 2
            [0.01, 0.99, 0],
            [0, 0, 1],  # Cluster 3
        ])
        # Normalize vectors
        self.simple_faces /= np.linalg.norm(self.simple_faces, axis=1)[:, None]

    def test_merge_clusters_below_threshold(self):
        self.clustering.cluster_sizes = {0: 5, 1: 5}
        self.clustering.assignments = {i: i % 2 for i in range(10)}
        self.clustering.merge_clusters(0, 1)
        self.assertNotIn((0, 1), self.clustering.suspicious_cluster_pairs)
        self.assertEqual(self.clustering.cluster_sizes[0], 10)
        self.assertNotIn(1, self.clustering.cluster_sizes)

    def test_merge_clusters_above_threshold(self):
        self.clustering.cluster_sizes = {0: 15, 1: 12}
        self.clustering.merge_clusters(0, 1)
        self.assertIn((0, 1), self.clustering.suspicious_cluster_pairs)
        self.assertEqual(self.clustering.cluster_sizes[0], 15)
        self.assertEqual(self.clustering.cluster_sizes[1], 12)

    def test_cluster_faces(self):
        self.clustering.cluster_faces()
        total_assignments = len(self.clustering.assignments)
        self.assertEqual(total_assignments, len(self.faces))
        total_cluster_size = sum(self.clustering.cluster_sizes.values())
        self.assertEqual(total_cluster_size, len(self.faces))

    def test_three_distinct_clusters(self):
        """Test formation of three distinct clusters with clear separation"""
        clustering = FaceClustering(self.simple_faces)
        clustering.cluster_faces()

        # Get unique clusters
        unique_clusters = set(clustering.assignments.values())
        self.assertEqual(len(unique_clusters), 3)

        # First three vectors should be in same cluster
        c1 = clustering.assignments[0]
        self.assertEqual(clustering.assignments[1], c1)
        self.assertEqual(clustering.assignments[2], c1)

        # Next two vectors should be in same cluster
        c2 = clustering.assignments[3]
        self.assertEqual(clustering.assignments[4], c2)

    def test_cluster_sizes(self):
        """Test correct cluster size tracking"""
        clustering = FaceClustering(self.simple_faces)
        clustering.cluster_faces()

        # Verify sizes match assignments
        for cluster_id in clustering.cluster_sizes:
            expected_size = sum(1 for x in clustering.assignments.values() if x == cluster_id)
            self.assertEqual(clustering.cluster_sizes[cluster_id], expected_size)

    def test_cosine_threshold(self):
        """Test that vectors beyond cosine threshold (0.4) don't merge"""
        # Create two vectors with cosine distance > 0.4
        test_faces = np.array([
            [1, 0, 0],
            [0.5, 0.87, 0]  # ~60 degree angle
        ])
        test_faces /= np.linalg.norm(test_faces, axis=1)[:, None]

        clustering = FaceClustering(test_faces)
        clustering.cluster_faces()

        # Should form separate clusters
        self.assertNotEqual(
            clustering.assignments[0],
            clustering.assignments[1]
        )



if __name__ == '__main__':
    unittest.main()