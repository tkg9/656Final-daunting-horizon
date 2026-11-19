from django.test import SimpleTestCase

from productions import script

SAMPLE = """SCENE 1. A kitchen.
ANNA: Morning.
BEN: Is it?

SCENE 2. A street.
ANNA: Wait for me.
"""


class SplitScenesTests(SimpleTestCase):
    def test_splits_on_scene_headings(self):
        scenes = script.split_scenes(SAMPLE)
        self.assertEqual([s["number"] for s in scenes], [1, 2])
        self.assertEqual(scenes[0]["heading"], "SCENE 1. A kitchen.")
        self.assertIn("BEN: Is it?", scenes[0]["text"])
        self.assertNotIn("Wait for me", scenes[0]["text"])

    def test_text_before_first_heading_becomes_scene_one(self):
        scenes = script.split_scenes("Prologue words.\nACT I\nANNA: Hi.")
        self.assertEqual(len(scenes), 2)
        self.assertEqual(scenes[0]["heading"], "Scene 1")
        self.assertEqual(scenes[1]["heading"], "ACT I")

    def test_no_headings_is_one_scene(self):
        self.assertEqual(len(script.split_scenes("ANNA: Hi.\nBEN: Bye.")), 1)

    def test_empty_script(self):
        self.assertEqual(script.split_scenes("   "), [])


class CharactersTests(SimpleTestCase):
    def test_finds_speakers_in_order_without_duplicates(self):
        self.assertEqual(script.characters(SAMPLE), ["ANNA", "BEN"])

    def test_ignores_headings_and_lowercase_lines(self):
        self.assertEqual(script.characters("SCENE 3\nnot a name: hi\nMRS. GRAY: Hello."), ["MRS. GRAY"])
