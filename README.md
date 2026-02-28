# PASOS Editor
The **PASOS Editor** is a GUI program built with [Manim](https://github.com/ManimCommunity/manim) where scenes are rendered using **timelines** instead of traditional imperative animation code.

Scenes are rendered using the **PASOS Engine**, which controls each mobject
through five independent timelines:
- **P**osition (where it's placed)
- **A**ngle (how much it's rotated)
- **S**cale (how much it's scaled)
- **O**pacity (how visible it is)
- **S**prite (the VMobject that defines its appearence)

---

## Table of Contents

- [Timelines and Events](#timelines-and-events)
- [Example](#example)
- [Usage](#usage)
- [Requirements](#requirements)
- [History](#history)
- [Project status](#project-status)

## Timelines and Events

Each timeline is a list of events defined by:
- `start` (when the event starts in seconds)
- `duration` (how long it lasts)
- `easing` (the rate function being used)
- `formula` (how the value must change over time)

### Example
An event that moves a mobject from `ORIGIN` to `RIGHT * 2` starting at `t = 2s` and ending at `t = 3.5s` is interpreted as `[2, 1.5, "smooth", "L: [2, 0, 0]"]` (here, `L: ` means it's a linear interpolation).

## Requirements
- Python
- PyQt6
- Manim (Community Edition)
- Pygame

## Usage

This program is written entirely in Python and is distributed as source code.

To use the PASOS Editor, you must install the dependencies, clone one of the stable versions (avaliable in the Tags section of this repository) and run it locally using `main.pyw`.

> Currently there are no stable versions.

## History

While working on my first math video for Youtube, I noticed some of problems with manim:
- Animating purely through code makes bugs easier to show up
- The lack of visual feedback makes it hard to position things correctly
- To see how anything looks, you have to render part of the video, which takes time

That led me to the idea of creating a program that would make the animating process faster. One where I could see changes in real time and adjust parameters of animations based on how they look. That idea eventually became the PASOS Editor.

In order to see things in real time, I needed a way for the program to know how the object should look at any given moment, and for that reason I made the separate timelines. If two events occur sequentially in a timeline, the program can simple ignore the first one after it ends. Having multiple timelines also makes it possible to change different aspects of the mobject independently, and that includes running multiple animations at the same time.

The first time I ever thought about PASOS, I called it by the generic name "Manim Automation Engine" and wrote:

> *"The idea: there's a list of objects `[o₁, o₂, o₃, ... oₙ]`. For each `oₙ`, there's a sequence of: position (a 3D Vector); scale (a positive real number); angle (an element of `[0, 2π)`); visual (either a VMobject or a VGroup)"*

The core idea was already there, but notice I said "either a VMobject or a VGroup". At the time, vgroups were a problem because I didn't know how to animate their submobjects independently.

The (still unimplemented) solution I came with was to treat every single mobject as a main scene mobject. Mobjects that exist only to form a vgroup would be made invisible, and the vgroup would simply reference them. This way, mobjects inside a vgroup could still change over time and it would also be possible to transform a single mobject into multiple mobjects.

In **Novemeber**, due to the frustration caused by a part of my video that was taking too long, I finally started actively developing PASOS.

## Project Status

Bugs are expected since it's not released, I might make a file for reporting bugs or maybe even make a section for them in this README.

At the moment, it's not possible to animate in the PASOS Editor because the **timeline editor** and **event editor** are still under development.
