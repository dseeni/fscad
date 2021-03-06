# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fscad import *

import adsk.fusion
import unittest
import test_utils
import importlib
importlib.reload(test_utils)
import test_utils


class FaceTest(test_utils.FscadTestCase):
    def validate_test(self):
        pass

    def test_adjacent_coincident_faces(self):
        box1 = Box(1, 1, 1, "box1")
        box2 = Box(1, 1, 1, "box2")
        box2.place(-box2 == +box1,
                   ~box2 == ~box1,
                   ~box2 == ~box1)

        faces = box1.find_faces(box2.left)
        self.assertEqual(len(faces), 1)
        self.assertTrue(faces[0].brep.geometry.normal.isParallelTo(Vector3D.create(1, 0, 0)))
        self.assertEqual(faces[0].brep.pointOnFace.x, 1)

    def test_diff_coincident_face(self):
        box = Box(1, 1, 1)
        hole = Box(.5, .5, .5, "hole")
        hole.place(+hole == +box,
                   ~hole == ~box,
                   ~hole == ~box)
        diff = Difference(box, hole)

        faces = diff.find_faces(hole.left)
        self.assertEqual(len(faces), 1)
        self.assertTrue(faces[0].brep.geometry.normal.isParallelTo(Vector3D.create(1, 0, 0)))
        self.assertEqual(faces[0].brep.pointOnFace.x, .5)

        faces = diff.find_faces(hole)
        self.assertEqual(len(faces), 5)
        for face in faces:
            self.assertEqual(face.brep.area, .5*.5)

        faces = diff.find_faces([hole])
        self.assertEqual(len(faces), 5)
        for face in faces:
            self.assertEqual(face.brep.area, .5*.5)

        faces = diff.find_faces([list(hole.bodies[0].faces)])
        self.assertEqual(len(faces), 5)
        for face in faces:
            self.assertEqual(face.brep.area, .5*.5)

        faces = diff.find_faces(hole.bodies[0])
        self.assertEqual(len(faces), 5)
        for face in faces:
            self.assertEqual(face.brep.area, .5*.5)

    def test_spherical_coincident_face(self):
        box = Box(1, 1, 1)
        sphere = Sphere(.25)
        sphere.place(~sphere == +box,
                     ~sphere == ~box,
                     ~sphere == ~box)
        diff = Difference(box, sphere)

        faces = diff.find_faces(sphere.surface)
        self.assertEqual(len(faces), 1)
        self.assertTrue(isinstance(faces[0].brep.geometry, adsk.core.Sphere))

    def test_connected_faces(self):
        box = Box(1, 1, 1)

        self.assertSetEqual({face.brep.tempId for face in box.bottom.connected_faces},
                            {face.brep.tempId for face in [box.left, box.right, box.front, box.back]})
        self.assertSetEqual({face.brep.tempId for face in box.top.connected_faces},
                            {face.brep.tempId for face in [box.left, box.right, box.front, box.back]})
        self.assertSetEqual({face.brep.tempId for face in box.left.connected_faces},
                            {face.brep.tempId for face in [box.top, box.bottom, box.front, box.back]})
        self.assertSetEqual({face.brep.tempId for face in box.right.connected_faces},
                            {face.brep.tempId for face in [box.top, box.bottom, box.front, box.back]})
        self.assertSetEqual({face.brep.tempId for face in box.front.connected_faces},
                            {face.brep.tempId for face in [box.top, box.bottom, box.left, box.right]})
        self.assertSetEqual({face.brep.tempId for face in box.back.connected_faces},
                            {face.brep.tempId for face in [box.top, box.bottom, box.left, box.right]})

    def test_component_faces(self):
        box1 = Box(1, 1, 1, name="box1")
        box2 = Box(1, 1, 1, name="box2")
        box2.place(
            (-box2 == +box1) + 5,
            ~box2 == ~box1,
            ~box2 == ~box1)

        self.assertEquals(len(Group([box1, box2]).faces), 12)


from test_utils import load_tests
def run(context):
    import sys
    test_suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(failfast=True).run(test_suite)
