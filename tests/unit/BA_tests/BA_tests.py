"""
Boolean Algen
 Covers: fetchSpecies wrapper, homolog retrieval, grouping,
  clustering, intersect, and bool_except.
"""

import unittest
from unittest.mock import patch
from collections import defaultdict

from plugins.BooleanAlgebra import service

_FAKE_SPECIES = [(1, "Mus musculus"), (2, "Homo sapiens")]


_FAKE_GENESETS = {
    "1256": {
        "object": {
            "geneset": {"species_id": 1},
            "geneset_values": [
                {"ode_gene_id": gid, "ode_ref_id": f"R{gid}"}
                for gid in (11, 12, 13, 101)           
            ],
        }
    },
    "239581": {
        "object": {
            "geneset": {"species_id": 2},
            "geneset_values": [
                {"ode_gene_id": gid, "ode_ref_id": f"R{gid}"}
                for gid in (21, 22, 101, 102)          
            ],
        }
    },
    "137861": {
        "object": {
            "geneset": {"species_id": 2},
            "geneset_values": [
                {"ode_gene_id": gid, "ode_ref_id": f"R{gid}"}
                for gid in (23, 24, 102)                
            ],
        }
    },
}


class ServiceHelperTests(unittest.TestCase):
    """Unit‑tests for functions in service.py."""

    def setUp(self):
        # Patch fetchSpecies & get_geneset_data so helpers work offline
        self.patches = [
            patch.object(service, "fetchSpecies", lambda: _FAKE_SPECIES),
            patch.object(service, "get_geneset_data",
                         lambda gs_id: _FAKE_GENESETS[str(gs_id)]),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()


    def test_get_all_geneweaver_species_for_boolean(self):
        short, full = service.get_all_geneweaver_species_for_boolean()
        self.assertEqual(short, {1: "Mm", 2: "Hs"})
        self.assertEqual(full[1], "Mus musculus")


    def test_homolog_and_grouping(self):
        genes = service.get_homologs_for_geneset(["1256", "239581", "137861"])
        # Expect 4 + 4 + 3 = 11 tuples
        self.assertEqual(len(genes), 11)

        grouped = service.group_homologs(genes, [1, 2])
        # Unique IDs = 9 (101 appears twice, 102 twice)
        self.assertEqual(len(grouped), 9)
        # Gene 101 should have 2 tuples, gene 102 should have 2 tuples
        self.assertEqual(len(grouped[101]), 2)
        self.assertEqual(len(grouped[102]), 2)


    def test_intersect_and_except(self):
        genes = service.get_homologs_for_geneset(["1256", "239581", "137861"])
        grouped = service.group_homologs(genes, [1, 2])

        inter = service.intersect(grouped, at_least=2)
        # Only genes 101 & 102 appear in >=2 genesets → 2 total
        total_shared = sum(len(bucket) for bucket in inter.values())
        self.assertEqual(total_shared, 2)

        ex = service.bool_except(grouped)
        # bool_except should NOT contain 101 or 102
        flat_except = {gid for bucket in ex.values() for gid in bucket}
        self.assertNotIn(101, flat_except)
        self.assertNotIn(102, flat_except)

    def test_cluster_genes(self):
        genes = service.get_homologs_for_geneset(["1256", "239581", "137861"])
        cluster = service.cluster_genes(genes, [1, 2])

        self.assertIn(11, cluster[1]["unique"])
        self.assertEqual(len(cluster[1]["unique"]), 3)

        self.assertEqual(len(cluster[2]["unique"]), 4)

        self.assertIn(101, cluster[1]["intersection"] + cluster[2]["intersection"])
        self.assertIn(102, cluster[1]["intersection"] + cluster[2]["intersection"])


if __name__ == "__main__":
    unittest.main(verbosity=2)