import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import tokenlib as t  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]


def minimal():
    return {
        "tokens": {
            "text": {"kind": "color", "items": {"primary": "Main text"}},
            "surface": {"kind": "color", "items": {"window": "Window"}},
            "spacing": {"kind": "points", "items": {"m": "Medium gap"}},
            "type": {"kind": "font", "items": {"body": "Body text"}},
        },
        "contrast": [{"text": "text.primary", "on": "surface.window", "use": "body"}],
        "themes": [{
            "id": "classic-light", "appearance": "light",
            "values": {
                "text": {"primary": "#000000"},
                "surface": {"window": {"system": "windowBackgroundColor", "fallback": "#FFFFFF"}},
                "spacing": {"m": 12},
                "type": {"body": {"size": 13, "weight": "regular"}},
            },
        }],
    }


class Validation(unittest.TestCase):
    def problems(self, data):
        with self.assertRaises(t.TokenError) as ctx:
            t.validate(data)
        return ctx.exception.problems

    def test_minimal_file_is_valid(self):
        t.validate(minimal())

    def test_missing_token(self):
        d = minimal()
        del d["themes"][0]["values"]["spacing"]["m"]
        self.assertIn("theme classic-light lacks spacing.m", self.problems(d))

    def test_unknown_token(self):
        d = minimal()
        d["themes"][0]["values"]["spacing"]["huge"] = 99
        self.assertIn("theme classic-light defines unknown token spacing.huge", self.problems(d))

    def test_unknown_group(self):
        d = minimal()
        d["themes"][0]["values"]["glow"] = {"x": "#FFFFFF"}
        self.assertIn("theme classic-light defines unknown token glow.x", self.problems(d))

    def test_every_problem_is_reported_at_once(self):
        d = minimal()
        d["themes"][0]["values"]["text"]["primary"] = "red"
        d["themes"][0]["values"]["spacing"]["m"] = -1
        self.assertEqual(len(self.problems(d)), 2)

    def test_malformed_colours(self):
        for bad in ("#FFF", "FFFFFF", "#GGGGGG", 12, {"system": "windowBackgroundColor"},
                    {"system": "notAColor", "fallback": "#FFFFFF"},
                    {"system": "labelColor", "fallback": "white"}):
            with self.subTest(bad=bad):
                d = minimal()
                d["themes"][0]["values"]["text"]["primary"] = bad
                self.assertTrue(any("text.primary" in p for p in self.problems(d)))

    def test_alpha_colour_is_accepted(self):
        d = minimal()
        d["themes"][0]["values"]["text"]["primary"] = "#000000D9"
        t.validate(d)

    def test_points_must_be_non_negative_numbers(self):
        for bad in (-1, "12", True, None):
            with self.subTest(bad=bad):
                d = minimal()
                d["themes"][0]["values"]["spacing"]["m"] = bad
                self.assertTrue(any("spacing.m" in p for p in self.problems(d)))

    def test_font_needs_size_and_known_weight(self):
        for bad in ({"size": 13}, {"size": 0, "weight": "bold"}, {"size": 13, "weight": "fat"}):
            with self.subTest(bad=bad):
                d = minimal()
                d["themes"][0]["values"]["type"]["body"] = bad
                self.assertTrue(any("type.body" in p for p in self.problems(d)))

    def test_appearance_and_duplicate_ids(self):
        d = minimal()
        d["themes"].append(copy.deepcopy(d["themes"][0]))
        d["themes"][1]["appearance"] = "dim"
        problems = self.problems(d)
        self.assertIn("theme id 'classic-light' is used twice", problems)
        self.assertIn("theme classic-light: appearance must be light or dark", problems)

    def test_theme_id_must_be_neutral_kebab_case(self):
        d = minimal()
        d["themes"][0]["id"] = "Cubase_Dark"
        self.assertTrue(any("must be lower-case words" in p for p in self.problems(d)))

    def test_contrast_pair_must_name_colour_tokens(self):
        d = minimal()
        d["contrast"] = [{"text": "spacing.m", "on": "surface.nope", "use": "loud"}]
        problems = self.problems(d)
        self.assertEqual(len(problems), 3)

    def test_unknown_top_level_key(self):
        d = minimal()
        d["colours"] = {}
        self.assertIn("unknown top-level key 'colours'", self.problems(d))

    def test_token_needs_description(self):
        d = minimal()
        d["tokens"]["spacing"]["items"]["m"] = ""
        self.assertIn("token spacing.m: needs a one-line description", self.problems(d))

    def test_description_must_be_one_line(self):
        for bad in ("Medium\ngap", "Medium gap\n", "Medium\tgap", "Bell\x07", "Medium\x7fgap", "Line sep"):
            with self.subTest(bad=bad):
                d = minimal()
                d["tokens"]["spacing"]["items"]["m"] = bad
                self.assertIn("token spacing.m: needs a one-line description", self.problems(d))

    def test_theme_note_must_be_one_line_text(self):
        for bad in ("Starter\nvalues", "Starter values\r", 12):
            with self.subTest(bad=bad):
                d = minimal()
                d["themes"][0]["note"] = bad
                self.assertIn("theme classic-light: note must be one line of text", self.problems(d))
        d = minimal()
        d["themes"][0]["note"] = "Starter values; final palette later."
        t.validate(d)

    def test_trailing_newline_is_not_accepted_by_any_pattern(self):
        cases = [
            (lambda d: d["themes"][0]["values"]["text"].__setitem__("primary", "#000000\n"), "text.primary"),
            (lambda d: d["themes"][0]["values"]["surface"].__setitem__(
                "window", {"system": "windowBackgroundColor", "fallback": "#FFFFFF\n"}), "surface.window"),
            (lambda d: d["themes"][0].__setitem__("id", "classic-light\n"), "must be lower-case words"),
            (lambda d: d["tokens"]["spacing"]["items"].__setitem__("m\n", "Medium gap"), "lowerCamelCase"),
            (lambda d: d["tokens"].__setitem__("glow\n", {"kind": "points", "items": {"x": "X"}}),
             "lowerCamelCase"),
        ]
        for i, (mutate, needle) in enumerate(cases):
            with self.subTest(case=i):
                d = minimal()
                mutate(d)
                self.assertTrue(any(needle in p for p in self.problems(d)), needle)


    def test_unhashable_values_are_reported_not_crashed_on(self):
        cases = [
            (lambda d: d["contrast"][0].__setitem__("use", [1]), "contrast[0]: use must be body, large or icon"),
            (lambda d: d["contrast"][0].__setitem__("text", ["text.primary"]),
             "contrast[0]: ['text.primary'] is not a colour token"),
            (lambda d: d["themes"][0].__setitem__("id", ["x"]),
             "theme id ['x'] must be lower-case words joined by hyphens"),
            (lambda d: d["themes"][0].__setitem__("appearance", {"x": 1}),
             "theme classic-light: appearance must be light or dark"),
            (lambda d: d["tokens"]["spacing"].__setitem__("kind", ["points"]),
             "token group 'spacing': kind ['points'] not one of color, points, font"),
        ]
        for i, (mutate, message) in enumerate(cases):
            with self.subTest(case=i):
                d = minimal()
                mutate(d)
                self.assertIn(message, self.problems(d))


def two_themes_with_brand():
    d = minimal()
    d["tokens"]["brand"] = {"kind": "color", "constant": True, "items": {"gold": "Brand gold"}}
    d["themes"][0]["values"]["brand"] = {"gold": "#EFC031"}
    second = copy.deepcopy(d["themes"][0])
    second["id"] = "studio-dark"
    second["appearance"] = "dark"
    d["themes"].append(second)
    return d


class ConstantGroups(unittest.TestCase):
    def problems(self, data):
        with self.assertRaises(t.TokenError) as ctx:
            t.validate(data)
        return ctx.exception.problems

    def test_constant_group_with_equal_values_is_valid(self):
        t.validate(two_themes_with_brand())

    def test_constant_group_must_match_in_every_theme(self):
        d = two_themes_with_brand()
        d["themes"][1]["values"]["brand"]["gold"] = "#EFC032"
        self.assertIn("theme studio-dark, brand.gold: brand is constant, so it must equal theme classic-light's "
                      "value '#EFC031'", self.problems(d))

    def test_other_groups_may_differ(self):
        d = two_themes_with_brand()
        d["themes"][1]["values"]["text"]["primary"] = "#FFFFFF"
        t.validate(d)

    def test_constant_must_be_a_boolean(self):
        d = two_themes_with_brand()
        d["tokens"]["brand"]["constant"] = "yes"
        self.assertIn("token group 'brand': constant must be true or false", self.problems(d))

    def test_group_keys_are_still_checked(self):
        d = two_themes_with_brand()
        d["tokens"]["brand"]["fixed"] = True
        self.assertIn("token group 'brand' needs 'kind' and 'items' (and optionally 'constant')", self.problems(d))


class Contrast(unittest.TestCase):
    def test_black_on_white_is_21(self):
        self.assertAlmostEqual(t.contrast_ratio(t.rgba("#000000"), t.rgba("#FFFFFF")), 21.0, places=6)

    def test_same_colour_is_1(self):
        self.assertAlmostEqual(t.contrast_ratio(t.rgba("#777777"), t.rgba("#777777")), 1.0)

    def test_known_grey(self):
        # #767676 on white is the classic 4.54:1 AA grey.
        self.assertAlmostEqual(t.contrast_ratio(t.rgba("#767676"), t.rgba("#FFFFFF")), 4.54, places=2)

    def test_alpha_is_composited_over_the_background(self):
        r, g, b, a = t.over(t.rgba("#00000080"), (1.0, 1.0, 1.0, 1.0))
        self.assertAlmostEqual(r, 1 - 128 / 255)
        self.assertEqual((r, a), (b, 1.0))

    def test_ratio_is_rounded_down(self):
        self.assertEqual(t.format_ratio(4.4988), "4.49:1")
        self.assertEqual(t.format_ratio(21.0), "21.00:1")

    def test_system_colour_uses_fallback(self):
        self.assertEqual(t.rgba({"system": "labelColor", "fallback": "#FF0000"}), (1.0, 0.0, 0.0, 1.0))

    def test_rows_flag_failures_without_raising(self):
        d = minimal()
        d["themes"][0]["values"]["text"]["primary"] = "#EEEEEE"
        (row,) = t.contrast_rows(d)
        self.assertEqual(row[:4], ("classic-light", "text.primary", "surface.window", "body"))
        self.assertFalse(row[6])
        self.assertIn("| WARN |", t.contrast_markdown([row]))


BRAND = {"gold": "#EFC031", "cyan": "#00ACEC", "cyanInk": "#0077A8",
         "ink": "#222222", "paper": "#FFFFFF", "rule": "#000000"}


class RepositoryTokens(unittest.TestCase):
    def setUp(self):
        self.data = t.load(ROOT / "tokens" / "tokens.json")
        self.themes = {th["id"]: th for th in self.data["themes"]}

    def test_tokens_json_is_valid_and_has_the_five_themes(self):
        data = self.data
        self.assertEqual([th["id"] for th in data["themes"]],
                         ["classic-light", "studio-dark", "flat", "console", "symbiotic"])
        self.assertEqual([th["appearance"] for th in data["themes"]], ["light", "dark", "light", "dark", "light"])
        self.assertEqual([th.get("placeholder") for th in data["themes"]], [False, False, True, True, False])

    def test_spec_groups_are_present(self):
        with open(ROOT / "tokens" / "tokens.json", encoding="utf-8") as f:
            groups = json.load(f)["tokens"]
        self.assertEqual(sorted(groups), sorted(["surface", "text", "accent", "state", "meter", "graph", "control",
                                                 "strip", "brand", "spacing", "radius", "iconStroke", "type"]))
        self.assertEqual(list(groups["iconStroke"]["items"]), ["s16", "s24", "s32"])
        self.assertEqual(list(groups["control"]["items"]),
                         ["gain", "eqLow", "eqLowMid", "eqHighMid", "eqHigh", "send", "pan", "dynamics", "filter"])
        self.assertEqual(list(groups["brand"]["items"]), list(BRAND))
        self.assertIs(groups["brand"].get("constant"), True)

    def test_brand_group_holds_the_site_palette_in_every_theme(self):
        for tid, theme in self.themes.items():
            with self.subTest(theme=tid):
                self.assertEqual(theme["values"]["brand"], BRAND)

    def test_symbiotic_theme_is_the_site_look(self):
        v = t.flat_values(self.themes["symbiotic"])
        self.assertEqual(v["surface.window"], BRAND["cyan"])
        self.assertEqual(v["surface.panel"], BRAND["paper"])
        self.assertEqual(v["surface.raised"], BRAND["gold"])
        self.assertEqual(v["surface.selection"], BRAND["gold"])
        self.assertEqual(v["surface.separator"], BRAND["rule"])
        self.assertEqual(v["text.primary"], BRAND["ink"])
        self.assertEqual(v["accent.accent"], BRAND["cyanInk"])
        self.assertIn("symbioticaudio.org", self.themes["symbiotic"]["note"])

    def test_classic_light_is_not_seeded_from_the_brand_palette(self):
        v = t.flat_values(self.themes["classic-light"])
        site = {BRAND["cyan"], BRAND["cyanInk"], BRAND["gold"], BRAND["ink"]}
        colour_groups = {g for g, spec in self.data["tokens"].items() if spec["kind"] == "color"} - {"brand"}
        for token, value in v.items():
            if token.split(".")[0] not in colour_groups:
                continue
            colour = value["fallback"] if isinstance(value, dict) else value
            with self.subTest(token=token):
                self.assertNotIn(colour.upper(), site)

    def test_accent_text_is_checked_on_panels_only(self):
        pairs = [(p["text"], p["on"], p["use"]) for p in self.data["contrast"]]
        self.assertIn(("accent.accent", "surface.panel", "body"), pairs)
        self.assertNotIn("surface.window", [on for text, on, _ in pairs if text == "accent.accent"])
        self.assertIn("not on the window", self.data["description"])

    def test_symbiotic_is_not_the_default_light_theme(self):
        lights = [th["id"] for th in self.data["themes"] if th["appearance"] == "light"]
        self.assertEqual(lights[0], "classic-light")


if __name__ == "__main__":
    unittest.main()
