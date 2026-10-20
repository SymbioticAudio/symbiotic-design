import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import rolelib as r  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
GLYPHS = [
    {"id": "glyph-05", "suggestedRole": "envelope", "confidence": "confirmed by owner"},
    {"id": "glyph-06", "suggestedRole": "antenna", "confidence": "medium"},
    {"id": "glyph-39", "suggestedRole": "brand logo", "confidence": "confirmed by owner"},
]


def catalogue(*extra):
    return {"roles": [
        {"id": "transport.play", "standard": "play", "label": "Play"},
        {"id": "editor.envelope", "standard": "envelope", "brand": "glyph-05", "label": "Envelope"},
        {"id": "brand.logo", "brand": "glyph-39", "label": "SymbioticAudio"},
        *extra,
    ]}


class Validation(unittest.TestCase):
    def problems(self, data):
        with self.assertRaises(r.RoleError) as ctx:
            r.validate(data, GLYPHS)
        return ctx.exception.problems

    def test_valid_catalogue(self):
        self.assertEqual(len(r.validate(catalogue(), GLYPHS)), 3)

    def test_standard_is_required(self):
        p = self.problems(catalogue({"id": "edit.undo", "label": "Undo"}))
        self.assertIn("edit.undo: needs a standard icon", p)

    def test_logo_must_not_have_a_standard_icon(self):
        data = catalogue()
        data["roles"][2]["standard"] = "play"
        self.assertTrue(any("wordmark" in p for p in self.problems(data)))

    def test_logo_is_required(self):
        data = catalogue()
        del data["roles"][2]
        self.assertIn("brand.logo is missing", self.problems(data))

    def test_unconfirmed_glyph_cannot_be_mapped(self):
        p = self.problems(catalogue({"id": "net.wireless", "standard": "play", "brand": "glyph-06", "label": "W"}))
        self.assertIn("net.wireless: brand glyph glyph-06 is not confirmed by the owner", p)

    def test_unknown_glyph(self):
        p = self.problems(catalogue({"id": "x.y", "standard": "play", "brand": "glyph-99", "label": "X"}))
        self.assertIn("x.y: brand glyph 'glyph-99' does not exist", p)

    def test_duplicate_and_bad_ids(self):
        p = self.problems(catalogue({"id": "transport.play", "standard": "play", "label": "Play"},
                                    {"id": "Transport", "standard": "play", "label": "T"}))
        self.assertIn("transport.play: listed twice", p)
        self.assertTrue(any("dotted lower-case" in x for x in p))

    def test_swift_name_clash(self):
        p = self.problems(catalogue({"id": "transport.pla-y", "standard": "play", "label": "A"},
                                    {"id": "transport.pla.y", "standard": "play", "label": "B"}))
        self.assertTrue(any("clashes" in x for x in p))

    def test_label_and_unknown_keys(self):
        p = self.problems(catalogue({"id": "a.b", "standard": "play", "label": " ", "colour": "red"}))
        self.assertIn("a.b: needs a label", p)
        self.assertIn("a.b: unknown key 'colour'", p)


class Hardening(unittest.TestCase):
    def problems(self, data, glyphs=GLYPHS):
        with self.assertRaises(r.RoleError) as ctx:
            r.validate(data, glyphs)
        return ctx.exception.problems

    def test_id_with_trailing_newline(self):
        p = self.problems(catalogue({"id": "transport.play\n", "standard": "play", "label": "P"}))
        self.assertTrue(any("dotted lower-case" in x for x in p))

    def test_label_must_be_one_line(self):
        p = self.problems(catalogue({"id": "a.b", "standard": "play", "label": "Two\nlines"}))
        self.assertIn("a.b: label must be one line without control characters", p)
        p = self.problems(catalogue({"id": "a.c", "standard": "play", "label": "Tab\there"}))
        self.assertIn("a.c: label must be one line without control characters", p)

    def test_designer_name_is_an_optional_string(self):
        glyphs = [dict(g) for g in GLYPHS]
        glyphs[0]["designerName"] = "envelope"
        self.assertEqual(len(r.validate(catalogue(), glyphs)), 3)
        glyphs[1]["designerName"] = 7
        self.assertIn("glyphs.json: glyph-06: designerName must be a one-line string", self.problems(catalogue(), glyphs))
        glyphs[1]["designerName"] = "a\nb"
        self.assertIn("glyphs.json: glyph-06: designerName must be a one-line string", self.problems(catalogue(), glyphs))


class FixRound1(unittest.TestCase):
    def problems(self, data):
        with self.assertRaises(r.RoleError) as ctx:
            r.validate(data, GLYPHS)
        return ctx.exception.problems

    def test_stray_hyphens_in_ids(self):
        for bad in ["a-.b", "a--b.c", "-a.b", "a.b-", "a.-b", "a.b--c", "1a.b"]:
            p = self.problems(catalogue({"id": bad, "standard": "play", "label": "Z"}))
            self.assertTrue(any("dotted lower-case" in x for x in p), bad)

    def test_labels_must_be_unique(self):
        p = self.problems(catalogue({"id": "a.b", "standard": "play", "label": "Play"}))
        self.assertIn("a.b: label 'Play' is already used by transport.play", p)

    def test_standard_name_grammar(self):
        for bad in ["../x", "has space", "Play", "a--b", "-a", "a/b", "x\n"]:
            p = self.problems(catalogue({"id": "a.b", "standard": bad, "label": "Z"}))
            self.assertIn(f"a.b: standard icon name {bad!r} is not a lower-case hyphenated name", p)

    def test_repository_has_part_single_and_distinct_mono(self):
        roles = {x["id"]: x for x in r.load_json(ROOT / "icons" / "roles.json")["roles"]}
        self.assertEqual(roles["part.single"]["label"], "Single")
        self.assertNotEqual(roles["audio.mono"]["label"], roles["voice.mono"]["label"])


class Coverage(unittest.TestCase):
    def test_sections(self):
        roles = r.validate(catalogue({"id": "notation.fermata", "standard": "fermata", "label": "Fermata"}), GLYPHS)
        md = r.coverage_markdown(roles, ["play", "envelope"], GLYPHS)
        brief = md.split("## To draw")[0]
        self.assertIn("| `transport.play` | Play | `play` |", brief)
        self.assertNotIn("editor.envelope", brief)
        self.assertNotIn("brand.logo", brief)
        self.assertIn("| `notation.fermata` | `fermata` |", md)
        unassigned = md.split("## Glyphs not assigned")[1]
        self.assertIn("`glyph-06`", unassigned)
        self.assertNotIn("`glyph-05`", unassigned)

    def test_unassigned_glyph_shows_designer_name(self):
        glyphs = [dict(g) for g in GLYPHS]
        glyphs[1]["designerName"] = "antenna-2009"
        roles = r.validate(catalogue(), glyphs)
        md = r.coverage_markdown(roles, ["play", "envelope"], glyphs)
        self.assertIn("| `glyph-06` | antenna | medium | antenna-2009 |", md)

    def test_nothing_missing(self):
        roles = r.validate(catalogue(), GLYPHS)
        self.assertEqual(r.missing_standard(roles, ["play", "envelope"]), [])
        self.assertIn("None: every role's standard icon exists", r.coverage_markdown(roles, ["play", "envelope"], GLYPHS))


class RepositoryRoles(unittest.TestCase):
    def setUp(self):
        self.glyphs = r.load_json(ROOT / "icons" / "glyphs.json")
        self.roles = r.validate(r.load_json(ROOT / "icons" / "roles.json"), self.glyphs)
        self.by_id = {x["id"]: x for x in self.roles}

    def test_every_confirmed_glyph_is_mapped(self):
        confirmed = {g["id"] for g in self.glyphs if g["confidence"] == "confirmed by owner"}
        self.assertEqual(len(confirmed), 12)
        self.assertEqual({x["brand"] for x in self.roles if "brand" in x}, confirmed)

    def test_designer_names(self):
        names = {g["id"]: g["designerName"] for g in self.glyphs if "designerName" in g}
        self.assertEqual(names, {"glyph-02": "virus", "glyph-03": "joystick", "glyph-07": "echo", "glyph-08": "ps",
                                 "glyph-17": "stafflines", "glyph-23": "controller", "glyph-24": "controller",
                                 "glyph-25": "bassclef", "glyph-35": "natural", "glyph-41": "gclef"})

    def test_owner_assignments(self):
        expect = {"editor.envelope": "glyph-05", "editor.notation-alternate": "glyph-12", "editor.notation": "glyph-13",
                  "notation.fermata": "glyph-15", "monitor.phones-left": "glyph-23", "monitor.phones-right": "glyph-24",
                  "routing.send": "glyph-29", "notation.repeat": "glyph-34", "notation.natural": "glyph-35",
                  "editor.piano-roll": "glyph-38", "brand.logo": "glyph-39", "mode.loop": "glyph-40"}
        self.assertEqual({k: self.by_id[k]["brand"] for k in expect}, expect)

    def test_vizdaw_and_eg13_needs_are_covered(self):
        for rid in ["transport.play", "transport.record", "edit.add", "edit.close", "view.zoom-in", "view.zoom-out",
                    "status.warning", "status.problem", "status.fault", "status.audio-muted", "status.disk-slow",
                    "media.offline", "edit.remove-item", "view.taller-rows", "view.shorter-rows",
                    "record.arm", "monitor.input", "transport.punch-in", "transport.punch-out", "record.takes",
                    "media.pool", "audio.normalize", "audio.fade-in", "audio.fade-out",
                    "part.a", "part.b", "part.layer", "part.split", "part.multi", "voice.poly", "voice.mono",
                    "voice.legato", "audio.mono", "audio.stereo", "slot.source", "slot.filter", "slot.shaper",
                    "slot.fx", "slot.modulation", "control.tempo-sync", "control.midi-learn", "edit.random",
                    "routing.add-route", "routing.remove-route", "routing.via", "mixer.bypass", "mixer.power",
                    "preset.save", "preset.browse", "preset.previous", "preset.next", "preset.init",
                    "app.settings", "app.about"]:
            self.assertIn(rid, self.by_id)


if __name__ == "__main__":
    unittest.main()
