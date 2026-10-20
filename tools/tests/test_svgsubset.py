import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import svgsubset as s  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="butt" stroke-linejoin="miter">')


def svg(body):
    return HEAD + body + "</svg>"


def close(test, got, want, places=6):
    test.assertEqual(len(got), len(want))
    for g, w in zip(got, want):
        test.assertAlmostEqual(g, w, places=places)


class Primitives(unittest.TestCase):
    def test_line_is_stroked_move_line(self):
        (shape,) = s.parse_svg_text(svg('<line x1="1" y1="2" x2="3" y2="4"/>'))
        self.assertEqual(shape.ops, [("M", 1, 2), ("L", 3, 4)])
        self.assertTrue(shape.stroke)
        self.assertFalse(shape.fill)
        self.assertAlmostEqual(shape.weight, 1.0)
        self.assertEqual((shape.cap, shape.join), ("butt", "miter"))

    def test_polygon_closes_and_polyline_does_not(self):
        poly, line = s.parse_svg_text(svg('<polygon points="1 1 5 1 5 5"/><polyline points="1,1 5,1"/>'))
        self.assertEqual(poly.ops[-1], ("Z",))
        self.assertEqual(line.ops, [("M", 1, 1), ("L", 5, 1)])

    def test_circle_is_four_cubics_through_the_extremes(self):
        (c,) = s.parse_svg_text(svg('<circle cx="12" cy="12" r="6" fill="currentColor" stroke="none"/>'))
        self.assertTrue(c.fill)
        self.assertFalse(c.stroke)
        self.assertEqual([op[0] for op in c.ops], ["M", "C", "C", "C", "C", "Z"])
        self.assertEqual(c.ops[0], ("M", 18, 12))
        close(self, c.ops[2][5:], (6, 12))

    def test_rect_with_rx_has_rounded_corners(self):
        (r,) = s.parse_svg_text(svg('<rect x="4" y="4" width="16" height="10" rx="2"/>'))
        self.assertEqual(r.ops[0], ("M", 6, 4))
        self.assertEqual(sum(1 for op in r.ops if op[0] == "C"), 4)

    def test_ellipse(self):
        (e,) = s.parse_svg_text(svg('<ellipse cx="12" cy="12" rx="6" ry="3"/>'))
        self.assertEqual(e.ops[0], ("M", 18, 12))
        close(self, e.ops[1][5:], (12, 15))

    def test_child_paint_overrides_root(self):
        (shape,) = s.parse_svg_text(svg('<line x1="0" y1="0" x2="1" y2="1" stroke-width="2.4" '
                                        'stroke-linecap="round" stroke-linejoin="bevel"/>'))
        self.assertAlmostEqual(shape.weight, 2.0)
        self.assertEqual((shape.cap, shape.join), ("round", "bevel"))

    def test_xml_comments_are_ignored(self):
        self.assertEqual(len(s.parse_svg_text(svg('<!-- note --><line x1="0" y1="0" x2="1" y2="1"/>'))), 1)


class Paths(unittest.TestCase):
    def ops(self, d):
        return s.parse_path(d)

    def test_absolute_and_relative_lines(self):
        self.assertEqual(self.ops("M1 1 L3 1 l0 2 H5 h1 V7 v-1 Z"),
                         [("M", 1, 1), ("L", 3, 1), ("L", 3, 3), ("L", 5, 3), ("L", 6, 3),
                          ("L", 6, 7), ("L", 6, 6), ("Z",)])

    def test_implicit_lineto_after_move(self):
        self.assertEqual(self.ops("m1 1 2 0 0 2"), [("M", 1, 1), ("L", 3, 1), ("L", 3, 3)])

    def test_compact_numbers(self):
        self.assertEqual(self.ops("M.5.5L-1-1"), [("M", 0.5, 0.5), ("L", -1, -1)])
        self.assertEqual(self.ops("M1e1,2E-1"), [("M", 10, 0.2)])

    def test_smooth_cubic_reflects_previous_control(self):
        ops = self.ops("M0 0 C0 1 1 2 2 2 S4 1 4 0")
        self.assertEqual(ops[2], ("C", 3, 2, 4, 1, 4, 0))

    def test_quadratic_becomes_cubic(self):
        ops = self.ops("M0 0 Q3 3 6 0")
        close(self, ops[1][1:], (2, 2, 4, 2, 6, 0))

    def test_smooth_quadratic_reflects(self):
        ops = self.ops("M0 0 Q3 3 6 0 T12 0")
        close(self, ops[2][1:], (8, -2, 10, -2, 12, 0))

    def test_close_returns_to_subpath_start_for_relative_moves(self):
        ops = self.ops("M2 2 l1 0 z m1 1 l1 0")
        self.assertEqual(ops[3], ("M", 3, 3))

    def test_packed_arc_flags(self):
        a = self.ops("M0 0 a1 1 0 011 1")
        b = self.ops("M0 0 a1 1 0 0 1 1 1")
        self.assertEqual(a, b)


class Arcs(unittest.TestCase):
    def point_on_circle(self, ops, cx, cy, r):
        for op in ops:
            if op[0] == "C":
                self.assertAlmostEqual(math.hypot(op[5] - cx, op[6] - cy), r, places=6)

    def test_half_circle_sweep_1_goes_through_the_top(self):
        # From (6,12) to (18,12) radius 6, sweep 1 (clockwise on screen): passes (12,6).
        ops = s.parse_path("M6 12 A6 6 0 0 1 18 12")
        self.assertEqual(len([o for o in ops if o[0] == "C"]), 2)
        close(self, ops[1][5:], (12, 6))
        close(self, ops[-1][5:], (18, 12))
        self.point_on_circle(ops, 12, 12, 6)

    def test_sweep_0_goes_through_the_bottom(self):
        ops = s.parse_path("M6 12 A6 6 0 0 0 18 12")
        close(self, ops[1][5:], (12, 18))

    def test_large_arc_takes_the_long_way(self):
        ops = s.parse_path("M12 6 A6 6 0 1 1 6 12")
        self.assertEqual(len([o for o in ops if o[0] == "C"]), 3)
        self.point_on_circle(ops, 12, 12, 6)

    def test_radius_too_small_is_scaled_up(self):
        ops = s.parse_path("M0 0 A1 1 0 0 1 10 0")
        close(self, ops[1][5:], (5, -5))

    def test_cubic_midpoint_is_on_the_circle(self):
        (c1x, c1y, c2x, c2y, x, y), = s.arc_to_cubics(18, 12, 6, 6, 0, 0, 1, 12, 18)
        mx = 0.125 * 18 + 0.375 * c1x + 0.375 * c2x + 0.125 * x
        my = 0.125 * 12 + 0.375 * c1y + 0.375 * c2y + 0.125 * y
        self.assertAlmostEqual(math.hypot(mx - 12, my - 12), 6, places=3)

    def test_rotated_ellipse_arc_ends_on_target(self):
        ops = s.parse_path("M4 12 A8 4 30 0 1 20 12")
        close(self, ops[-1][5:], (20, 12))

    def test_zero_radius_is_a_straight_line(self):
        ops = s.parse_path("M0 0 A0 5 0 0 1 4 4")
        close(self, ops[1][1:], (0, 0, 4, 4, 4, 4))

    def test_relative_arcs_chain(self):
        ops = s.parse_path("M0 0 a5 5 0 0 1 10 0 a5 5 0 0 1 10 0")
        close(self, ops[-1][5:], (20, 0))
        self.point_on_circle(ops[:3], 5, 0, 5)
        self.point_on_circle(ops[3:], 15, 0, 5)

    def test_packed_implicit_arcs(self):
        ops = s.parse_path("M0 0 a1 1 0 011 1 1 1 0 011 1")
        close(self, ops[-1][5:], (2, 2))
        self.assertEqual(ops, s.parse_path("M0 0 a1 1 0 0 1 1 1 a1 1 0 0 1 1 1"))

    def test_large_arc_sweep_0(self):
        ops = s.parse_path("M12 6 A6 6 0 1 0 6 12")
        self.assertEqual(len([o for o in ops if o[0] == "C"]), 3)
        self.point_on_circle(ops, 6, 6, 6)  # the long way round the centre (6,6)
        close(self, ops[-1][5:], (6, 12))

    def test_rotated_scaled_up_arc_ends_on_target(self):
        ops = s.parse_path("M0 0 A1 0.5 30 1 0 10 4")
        close(self, ops[-1][5:], (10, 4))


class Transforms(unittest.TestCase):
    def test_translate_scale_mirror(self):
        (shape,) = s.parse_svg_text(svg('<g transform="translate(24 0) scale(-1 1)"><line x1="2" y1="3" x2="5" y2="3"/></g>'))
        self.assertEqual(shape.ops, [("M", 22, 3), ("L", 19, 3)])
        self.assertAlmostEqual(shape.weight, 1.0)

    def test_rotate_about_centre(self):
        (shape,) = s.parse_svg_text(svg('<g transform="rotate(90 12 12)"><line x1="12" y1="6" x2="12" y2="12"/></g>'))
        close(self, shape.ops[0][1:], (18, 12))

    def test_matrix_and_nested_groups(self):
        (shape,) = s.parse_svg_text(svg('<g transform="matrix(2 0 0 2 0 0)"><g transform="translate(1,1)">'
                                        '<line x1="0" y1="0" x2="1" y2="0"/></g></g>'))
        self.assertEqual(shape.ops, [("M", 2, 2), ("L", 4, 2)])
        self.assertAlmostEqual(shape.weight, 2.0)

    def test_skew_is_rejected(self):
        with self.assertRaisesRegex(s.SvgError, "skewX"):
            s.parse_svg_text(svg('<g transform="skewX(10)"><line x1="0" y1="0" x2="1" y2="1"/></g>'))

    def test_skew_matrix_and_non_uniform_scale_are_rejected(self):
        for tr in ("matrix(1 0 0.18 1 0 0)", "scale(2 1)"):
            with self.subTest(tr):
                with self.assertRaisesRegex(s.SvgError, "skew or non-uniform"):
                    s.parse_svg_text(svg(f'<g transform="{tr}"><line x1="0" y1="0" x2="1" y2="1"/></g>'))


class Errors(unittest.TestCase):
    def bad(self, body, pattern, whole=None):
        with self.assertRaisesRegex(s.SvgError, pattern):
            s.parse_svg_text(whole if whole is not None else svg(body))

    def test_unsupported_element(self):
        self.bad('<text>hi</text>', "unsupported element <text>")

    def test_unsupported_attribute(self):
        self.bad('<line x1="0" y1="0" x2="1" y2="1" opacity="0.5"/>', "'opacity'")

    def test_transform_outside_g(self):
        self.bad('<line x1="0" y1="0" x2="1" y2="1" transform="scale(2)"/>', "'transform'")

    def test_colour_other_than_current_color(self):
        self.bad('<line x1="0" y1="0" x2="1" y2="1" stroke="#f00"/>', "only none or currentColor")

    def test_bad_number(self):
        self.bad('<circle cx="12" cy="x" r="2"/>', "not a number")

    def test_bad_path_command(self):
        self.bad('<path d="M0 0 B1 1"/>', "unexpected 'B'")

    def test_path_missing_arguments(self):
        self.bad('<path d="M0 0 C1 1 2 2"/>', "C needs 6 numbers")

    def test_bad_arc_flag(self):
        self.bad('<path d="M0 0 A1 1 0 2 1 3 3"/>', "arc flag")

    def test_path_must_start_with_command(self):
        self.bad('<path d="1 1"/>', "must start with a command")

    def test_path_must_start_with_moveto(self):
        self.bad('<path d="L1 1"/>', "must start with a moveto")

    def test_negative_radius(self):
        self.bad('<circle cx="12" cy="12" r="-2"/>', "negative")
        self.bad('<rect x="0" y="0" width="-4" height="2"/>', "negative")
        self.bad('<ellipse cx="1" cy="1" rx="2" ry="-1"/>', "negative")

    def test_zero_size_shapes_are_skipped(self):
        shapes = s.parse_svg_text(svg('<rect x="1" y="1" width="4" height="0"/><circle cx="3" cy="3" r="0"/>'
                                      '<line x1="0" y1="0" x2="1" y2="1"/>'))
        self.assertEqual(len(shapes), 1)

    def test_wrong_view_box(self):
        self.bad('', "viewBox", whole='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><line x1="0" y1="0" x2="1" y2="1"/></svg>')

    def test_not_xml(self):
        self.bad('', "well-formed", whole="<svg")

    def test_empty_icon(self):
        self.bad('', "draws nothing")

    def test_bad_linecap(self):
        self.bad('<line x1="0" y1="0" x2="1" y2="1" stroke-linecap="pointy"/>', "stroke-linecap")

    def test_foreign_namespace(self):
        self.bad('<x:foo xmlns:x="urn:x"/>', "foreign namespace")


class RepositoryIcons(unittest.TestCase):
    def test_every_icon_in_the_repository_parses(self):
        files = sorted((ROOT / "icons" / "standard").glob("*.svg")) + sorted((ROOT / "icons" / "svg").glob("*.svg"))
        self.assertGreaterEqual(len(files), 98)
        for f in files:
            with self.subTest(f.name):
                self.assertTrue(s.parse_svg_file(f))

    def test_bounds_of_a_stroked_square(self):
        shapes = s.parse_svg_text(svg('<polygon points="6 6 18 6 18 18 6 18"/>'))
        close(self, s.bounds(shapes), (5.4, 5.4, 18.6, 18.6))


if __name__ == "__main__":
    unittest.main()
