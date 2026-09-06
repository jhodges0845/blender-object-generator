# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import FrozenInstanceError, replace
import unittest

from humanoid_core import Bone, Skeleton, BodyType, HumanoidSpec
from humanoid_core import generate_mesh, generate_proportions, generate_skeleton


class SkeletonTests(unittest.TestCase):
    def test_bones_bind_all_parts_and_match_mesh_joints_across_supported_range(self):
        for height in (120, 180, 240):
            for weight in (30, 95, 300):
                for kind in BodyType:
                    with self.subTest(height=height, weight=weight, kind=kind):
                        p = generate_proportions(HumanoidSpec(height, weight, kind))
                        rig = generate_skeleton(p)
                        mesh = generate_mesh(p)
                        self.assertEqual(len(rig.bones), 16)
                        self.assertEqual({b.part_name for b in rig.bones if b.part_name},
                                         {part.name for part in mesh.parts})
                        parts = {part.name: part for part in mesh.parts}
                        bones = {b.name: b for b in rig.bones}
                        for bone in rig.bones:
                            if bone.name.startswith(("upper_arm.", "forearm.", "hand.", "upper_leg.", "lower_leg.")):
                                vertices = parts[bone.part_name].vertices
                                centers = [tuple(sum(v[a] for v in ring) / len(ring) for a in range(3))
                                           for ring in (vertices[:8], vertices[8:])]
                                if "leg." in bone.name:
                                    centers.reverse()
                                for point, center in zip((bone.head, bone.tail), centers):
                                    for a, b in zip(point, center):
                                        self.assertAlmostEqual(a, b)
                            if bone.name.endswith('.left'):
                                other = bones[bone.name.replace('.left', '.right')]
                                for point, mirror in zip((bone.head, bone.tail), (other.head, other.tail)):
                                    self.assertAlmostEqual(point[0], -mirror[0])
                                    self.assertAlmostEqual(point[1], mirror[1])
                                    self.assertAlmostEqual(point[2], mirror[2])
                        self.assertEqual(bones['forearm.left'].parent, 'upper_arm.left')
                        self.assertEqual(bones['foot.right'].parent, 'lower_leg.right')

    def test_scaling_and_determinism(self):
        p = generate_proportions(HumanoidSpec(160, 60, BodyType.AVERAGE))
        a = generate_skeleton(p)
        b = generate_skeleton(generate_proportions(HumanoidSpec(200, 60 * 1.25**3, BodyType.AVERAGE)))
        self.assertEqual(a, generate_skeleton(p))
        for small, large in zip(a.bones, b.bones):
            for x, y in zip(small.head + small.tail, large.head + large.tail):
                self.assertAlmostEqual(y, x * 1.25)

    def test_contract_rejects_invalid_bones_and_hierarchies(self):
        bone = Bone('root', (0, 0, 0), (0, 0, 1))
        for point in ((0, 0, float('nan')), (0, 0, float('inf')), (0, 0), (0, 0, 10**1000)):
            with self.assertRaises(ValueError):
                replace(bone, head=point)
        with self.assertRaises(TypeError):
            replace(bone, head=(True, 0, 0))
        with self.assertRaises(ValueError):
            replace(bone, tail=bone.head)
        invalid = ((), (bone, bone), (bone, replace(bone, name='second')),
                   (replace(bone, parent='root'),), (replace(bone, parent='missing'),),
                   (replace(bone, part_name='torso'), Bone('child', (0, 0, 1), (0, 0, 2), 'root', 'torso')))
        for bones in invalid:
            with self.assertRaises(ValueError):
                Skeleton(bones)
        with self.assertRaises(TypeError):
            Skeleton((None,))
        with self.assertRaises(TypeError):
            generate_skeleton(None)

    def test_contract_copies_input_and_is_immutable(self):
        head = [0, 0, 0]
        bone = Bone('root', head, (0, 0, 1))
        bones = [bone]
        skeleton = Skeleton(bones)
        head[0] = 10
        bones.clear()
        self.assertEqual(skeleton.bones[0].head, (0, 0, 0))
        with self.assertRaises(FrozenInstanceError):
            bone.name = 'changed'
