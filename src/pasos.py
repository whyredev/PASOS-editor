from manim import *
import numpy as np
from .expression_evaluator import create_node_visitor, pasos_eval

def get_angle_between_mobs(A: Mobject, B: Mobject) -> float:
    if not (len(A.get_all_points()) and len(B.get_all_points())):
        return 0

    A_fpp = A.get_all_points()[0] - A.get_center()
    B_fpp = B.get_all_points()[0] - B.get_center()
    # fpp stands for "first point position"

    return np.arctan2(A_fpp[1], A_fpp[0]) - np.arctan2(B_fpp[1], B_fpp[0])

def get_ratio_between_mobs(A: Mobject, B: Mobject) -> float:
    if not (len(A.get_all_points()) and len(B.get_all_points())):
        return 1

    A_fpp = A.get_all_points()[0] - A.get_center()
    B_fpp = B.get_all_points()[0] - B.get_center()
    # fpp stands for "first point position"

    return np.linalg.norm(A_fpp) / (np.linalg.norm(B_fpp) or 1)

def become_mob_or_empty(mob: Mobject, new_thing: Mobject):
    if isinstance(new_thing, EmptyVMobject):
        new_thing = mob.copy().set_opacity(0)
    mob.become(new_thing)

# this animation extracts a specific frame (alpha) of an animation (anim)
def get_animation_frame(anim: Animation, alpha: float) -> Mobject:
    anim.begin()
    anim.interpolate(alpha)
    partial = anim.mobject.copy()
    anim.finish()
    return partial

def evaluate_formula(f: str, init_value, alpha: float, node_visitor):
    if f[:3] == "E: ": # E stands for "Expression evaluation"
        return pasos_eval("lambda t: " + f[3:], node_visitor)(alpha)
    elif alpha == 1:
        return pasos_eval(f[3:], node_visitor)
    if f[:3] == "L: ": # L stands for "Linear interpolation"
        end_value = pasos_eval(f[3:], node_visitor)
        if isinstance(end_value, list):
            end_value = np.array(end_value)
        return init_value + (end_value - init_value) * alpha
    if f[:3] == "G: ": # G stands for "Geometric interpolation"
        end_value = pasos_eval(f[3:], node_visitor)
        return init_value * (end_value/init_value)**alpha
    if f[:3] == "C: ": # C stands for "Creation"
        end_value = pasos_eval(f[3:], node_visitor)
        if isinstance(init_value, EmptyVMobject):
            return get_animation_frame(Create(end_value, rate_func=linear), alpha)
        if isinstance(end_value, EmptyVMobject):
            return get_animation_frame(Uncreate(init_value.copy(), rate_func=linear), alpha)
        return VGroup(get_animation_frame(Create(end_value, rate_func=linear), alpha), get_animation_frame(Uncreate(init_value.copy(), rate_func=linear), alpha))
    if f[:3] == "W: ": # W stands for "Writing"
        end_value = pasos_eval(f[3:], node_visitor)
        if isinstance(init_value, EmptyVMobject):
            return get_animation_frame(Write(end_value, rate_func=linear), alpha)
        if isinstance(end_value, EmptyVMobject):
            return get_animation_frame(Unwrite(init_value, rate_func=linear), alpha)
        return VGroup(get_animation_frame(Write(end_value, rate_func=linear), alpha), get_animation_frame(Unwrite(init_value.copy(), rate_func=linear), alpha))
    if f[:3] == "T: ": # T stands for "Transformation"
        end_value = pasos_eval(f[3:], node_visitor)
        return get_animation_frame(Transform(init_value.copy(), end_value, rate_func=linear), alpha)
    if f[:3] == "S: ": # S stands for "Submobject transformation" (btw i'm not sure if i'll keep this as a default prefix)
        end_value = pasos_eval(f[3:], node_visitor)
        return VGroup(*[get_animation_frame(Transform(submob, end_value, rate_func=linear), alpha) for submob in init_value.copy()])

class EmptyVMobject(VMobject): pass

# this animation is basically what makes PASOS work in render_mode, it calls update_mobs() at every frame
class always_update_mobs(Animation):
    def __init__(self, scene, update, **kwargs):
        self.scene = scene
        self.update = update # this exists because otherwise i could make changes in the animation and Manim would just ignore them and render using cached data
        super().__init__(self.scene.pmobs, **kwargs)

    def interpolate(self, time_over_duration):
        for i in self.scene.invisible_objects:
            self.scene.remove(self.scene.pmobs[i])
        self.scene.update_mobs()

class PASOS(MovingCameraScene):
    empty_mobject = EmptyVMobject()
    edtv = {} # editor variables, this is shared between pygame, pyqt's main window and its widgets

    def __init__(self, render_mode: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nv = create_node_visitor(self)
        self.render_mode = render_mode

        self.duration = 1 # i have to create the duration variable here cuz Scene already has a duration variable lol
        self.timeline = []
        self.invisible_objects = []
        
    def construct(self):
        self.update_visible_mobs()

        if self.render_mode:
            update = [self.duration, self.timeline, self.invisible_objects]
            self.play(always_update_mobs(self, update), run_time=self.duration)

    def update_visible_mobs(self):
        self.pmobs = Group(*[EmptyVMobject() for _ in range(len(self.timeline)//5)])
        self.mob_data = [{"position": ORIGIN, "angle": 0, "scale": 1, "opacity": 1, "sprite": EmptyVMobject()} for _ in self.pmobs]
        self.current_indexes = [0] * 5 * len(self.mob_data)
        self.into_event = [False] * 5 * len(self.mob_data)
        self.init_values = sum([[ORIGIN, 0, 1, 1, EmptyVMobject()] for _ in self.mob_data], [])

        self.clear()
        for i in self.pmobs:
            if not i in self.invisible_objects:
                self.add(i)

    def update_mobs(self):
        for i, event_list in enumerate(self.timeline):
            if not event_list:
                continue

            time = self.time if self.render_mode else self.edtv["time"]

            # update the current index
            idx = self.current_indexes[i]
            update_init_values = False
            while idx + 1 < len(event_list) and time >= event_list[idx][0] + event_list[idx][1]:
                idx += 1
                update_init_values = True
            while idx > 0 and time < event_list[idx-1][0] + event_list[idx-1][1]:
                idx -= 1
                update_init_values = True
            self.current_indexes[i] = idx
            
            if update_init_values:
                if idx == 0:
                    self.init_values[i] = [ORIGIN, 0, 1, 1, EmptyVMobject()][i%5]
                else:
                    self.init_values[i] = evaluate_formula(event_list[idx-1][3], self.init_values[i], 1, self.nv)
                self.into_event[i] = True

            e_start, e_dur, e_rate_func, e_formula = event_list[idx] # e stands for event, dur stands for duration
            if time >= e_start: # update mob data
                self.into_event[i] = True
                self.mob_data[i//5][["position", "angle", "scale", "opacity", "sprite"][i%5]] = evaluate_formula(e_formula, self.init_values[i], eval(e_rate_func)((time-e_start)/e_dur), self.nv)

            if not self.into_event[i]:
                continue

            if time < e_start:
                self.mob_data[i//5][["position", "angle", "scale", "opacity", "sprite"][i%5]] = self.init_values[i]
                self.into_event[i] = False

            mob = self.pmobs[i//5]
            mob_props = self.mob_data[i//5] # properties of the mobject
            event_type = i%5
            center = mob_props["position"]
            if event_type >= 3: # sprite or opacity
                become_mob_or_empty(mob, mob_props["sprite"])
                mob.shift(center).rotate(mob_props["angle"], about_point=center).scale(mob_props["scale"], about_point=center).fade(1 - mob_props["opacity"])
            #elif event_type == 3: # only opacity
            #    mob.fade(1 - mob_props["opacity"])
            else:
                mob.move_to(mob_props["sprite"].get_center() + center)
                mob.rotate(mob_props["angle"] + get_angle_between_mobs(mob_props["sprite"], mob), about_point=center)
                mob.scale(mob_props["scale"] * get_ratio_between_mobs(mob_props["sprite"], mob), about_point=center)