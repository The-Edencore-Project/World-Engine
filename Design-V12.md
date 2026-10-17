# DESIGN — v12 (The Engine Refactor)

## What this is
V11 was a monolith. V12 breaks the monolith into Systems. It does not add a new biome yet. It builds the stage so that V13 (The Forest) can be added without rewriting the app.

## The Shift

### 1. The Avatar Engine (Morphology)
We stop hardcoding "Turtle" or "Jellyfish." We define **Archetypes**:
- `Heavy`: Solon (Turtle -> Tortoise -> Golem)
- `Drifter`: Lumen (Jellyfish -> Moth -> Spirit)
- `Scuttler`: Vertex (Crab -> Beetle -> Spider)
- `Flitter`: Prism (Angel Fish -> Dragonfly -> Owl)
- `Slinker`: Ripple (Seahorse -> Lizard -> Cat)

The movement logic (inertia, bobbing, scuttling) is tied to the Archetype, not the creature. 

### 2. The Biome Engine
We create a `BIOMES` dictionary. Each biome holds its background functions, its floor functions, and its colour palette.
`BIOMES["water"]["draw_bg"]()` vs `BIOMES["forest"]["draw_bg"]()`

### 3. The Shared Word Pool
The WikiTree is no longer biome-specific. It uses universal anchors:
- `Surface` (Water: top of pond. Forest: canopy. Castle: ceiling.)
- `Ground` (Water: sand. Forest: dirt. Castle: stone.)
- `Light` (Water: rays. Forest: sunbeams. Castle: torches.)
The Story Engine plugs these props into the sentences.

### 4. The Geometry
The Inverted Pentagon remains the anchor. In Water, it floats. In Forest, it sits on the dirt. The coordinates `SEAT_HOME_X` and `SEAT_HOME_Y` are mapped to the centre of the screen, and the `Perspective` engine handles the rest.

## What doesn't change
The `SeatNet` class. The Arbiter. The Harmony Field math. The 5-tap privacy ritual. The psychological themes.

## What we build first
We build the framework and one test biome (Forest). If we can swap a Turtle for a Tortoise and a Jellyfish for a Moth without breaking the neural nets, the Engine works.