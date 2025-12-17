from manim import *

class Logo(Scene):
    def construct(self):
        preferences = {"dark_theme": True, "icon_form": True}

        manim_logo = ManimBanner()
        
        single_event_clip = RoundedRectangle(width=manim_logo[0].get_width(), height=0.9, stroke_width=8, fill_opacity=1, corner_radius=0.1)
        event_clips = VGroup(
            single_event_clip.copy().set_color(LOGO_RED).next_to(manim_logo[0].get_corner(UP), DOWN, buff=0),
            single_event_clip.copy().set_color(LOGO_BLUE).move_to(manim_logo[0]),
            single_event_clip.copy().set_color(LOGO_GREEN).next_to(manim_logo[0].get_corner(DOWN), UP, buff=0)
            )
        for mob in event_clips:
            mob.set_stroke_color(mob.get_color().darker(0.5))
        
        text_color = LOGO_WHITE if preferences["dark_theme"] else LOGO_BLACK
        mathbb_P = MathTex("\mathbb{P}", color=text_color).scale(7).next_to(manim_logo[1].get_corner(LEFT), RIGHT, buff=0)
        mathbb_ASOS = MathTex("\mathbb{ASOS}", color=text_color).scale(1.75).next_to(manim_logo[1].get_corner(DR) + UP * 0.25, UL, buff=0)
        
        pasos_logo = VGroup(event_clips, mathbb_P, mathbb_ASOS)
        if preferences["icon_form"]:
            event_clips.move_to(ORIGIN)
            VGroup(mathbb_P, mathbb_ASOS).move_to(ORIGIN)

        #self.add(manim_logo.scale(0.75).move_to(LEFT * 3 + DOWN/2), pasos_logo.scale(0.75).move_to(RIGHT * 3 + DOWN/2))
        #self.add(Text("Manim logo:").next_to(manim_logo, UP, buff=0.5), Text("PASOS logo:").next_to(pasos_logo, UP, buff=0.5))
        self.add(pasos_logo)

class Testing(Scene):
    def construct(self):
        line1 = DashedLine(start=3 * LEFT, end=3 * RIGHT)
        line1.rotate(angle=31 * DEGREES, about_point=ORIGIN)
        line2 = DashedLine(start=3 * UP, end=3 * DOWN)
        line2.rotate(angle=12 * DEGREES, about_point=ORIGIN)

        arc = TangentialArc(line1, line2, radius=2.25, corner=(1, 1), color=TEAL)
        self.add(arc, line1, line2)