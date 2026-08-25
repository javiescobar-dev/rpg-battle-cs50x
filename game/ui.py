# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Rendering layer for the battle screen.

CharacterSprite draws a character placeholder and its HP/MP bars,
and LogPanel renders the formatted battle log. Step 5 adds the
animation classes here.
"""

import math, random, pygame
from collections import deque
from game.config import (
    COLOR_BORDER, COLOR_TEXT, COLOR_BAR_BG, BAR_HEIGHT, COLOR_HP_BAR, COLOR_MP_BAR, COLOR_ACCENT, COLOR_FIREBALL, COLOR_SHADOW_BOLT, PANEL_BORDER, PANEL_ALPHA,
    LUNGE_DURATION, FLASH_DURATION, RECOIL_DURATION, FLOAT_DURATION, FLY_DURATION, LUNGE_GAP, RECOIL_DISTANCE, RETURN_JUMP_HEIGHT, LUNGE_SCALE_DEPTH, FLASH_RADIUS, PROJ_RADIUS,
    FLASH_COLOR, COLOR_DAMAGE, COLOR_CRIT, FLOAT_SPEED, FLOAT_FADE_START, FONT_FLOAT_SIZE, FONT_CRIT_SIZE, FONT_NAME, COLOR_HEAL, COLOR_GUARD, COLOR_GRAY, SFX,
    TRAIL_LENGTH, TRAIL_MIN_RADIUS, TRAIL_MIN_ALPHA, PULSE_AMPLITUDE, PULSE_SPEED, IMPACT_RING_COUNT, IMPACT_RING_SPEED, IMPACT_RING_WIDTH,
    PARTICLE_INITIAL_BURST, PARTICLES_PER_FRAME, PARTICLE_LIFE, PARTICLE_SPEED, PARTICLE_MIN_RADIUS, COLOR_FIREBALL_CORE, COLOR_SHADOW_BOLT_CORE,
    FIREBALL_PARTICLE_COLORS, SHADOW_BOLT_PARTICLE_COLORS, IMPACT_PARTICLE_COUNT, IMPACT_PARTICLE_SPEED, IMPACT_PARTICLE_LIFE
)
from game.assets import play_sound

class Animation:
    """Base class for one-shot timed effects driven by dt (never sleep)."""
    def __init__(self, duration):
        self.duration = duration
        self.elapsed = 0.0

    def update(self, dt):
        """Advance the animation by dt (seconds)."""
        self.elapsed += dt

    def is_done(self):
        """Return True when the animation has finished."""
        return self.elapsed >= self.duration

    def draw(self, surface):
        """Draw the effect. Base class draws nothing."""
        pass


class AttackAnimation(Animation):
    """Implements the attacker's movement (lunge forward and recoil) and the hit flash."""
    def __init__(self, attacker, defender, event, on_impact=None, duration=LUNGE_DURATION + FLASH_DURATION + RECOIL_DURATION + FLOAT_DURATION):
        # set base duration all animations will last this amount of time (seconds)
        super().__init__(duration)

        self.attacker = attacker
        self.defender = defender
        self.event = event
        self.damage = event.get("damage", 0)
        self.is_crit = event.get("is_crit", False)
        self.on_impact = on_impact      # optional callback fired exactly at the moment of the hit to update the HUD
        self._impact_fired = False      # flag to prevent the callback from being called more than once

        # phase boundaries (attributes so SpellAnimation can override them)
        self.t_flash = LUNGE_DURATION + FLASH_DURATION  # duration of the lunge and flash phases
        self.t_float = self.t_flash + RECOIL_DURATION   # duration of the recoil phase
        self.t_flash_start = LUNGE_DURATION             # duration of the lunge phase for the attacker movement and projectile motion

        # unit vector pointing from the attacker to the defender (diagonal movement)
        dx = defender.x - attacker.x
        dy = defender.y - attacker.y
        dist = max(1, math.hypot(dx, dy))  # hypot is the square root of the sum of the squares of the arguments, used to get the distance between the attacker and the defender
        # get the direction from the attacker to the defender (unit vector)
        self.ux = dx / dist
        self.uy = dy / dist

        # the attacker stops LUNGE_GAP px short of the defender along that direction
        self.land_x = defender.x - self.ux * LUNGE_GAP
        self.land_y = defender.y - self.uy * LUNGE_GAP
        self.dx = self.land_x - attacker.x   # total horizontal travel
        self.dy = self.land_y - attacker.y   # total vertical travel
        self.scale_target = 1 + self.uy * LUNGE_SCALE_DEPTH  # grows when approaching the camera (uy > 0)
        self.recoil = RECOIL_DISTANCE * defender.scale

        # flags to track the attacker's pose
        self._pose_lunge_done = False    # already switched to "run" at impact
        self._pose_recover_done = False  # already switched to "lunge" at recovery
        self._pose_recoil_done = False   # already switched to "idle" at recoil

        # create font and pre-render the floating damage number with an outline
        self.font = pygame.font.SysFont(FONT_NAME, FONT_CRIT_SIZE if self.is_crit else FONT_FLOAT_SIZE)
        # get the text to display
        text = f"{self.damage}!" if self.is_crit else str(self.damage)
        # get the color based on whether it's a critical hit
        color = COLOR_CRIT if self.is_crit else COLOR_DAMAGE
        # pre-render the floating damage number with an outline
        self._float_surf = render_outlined_text(self.font, text, color)

    def _phase(self):
        """Return the current phase name based on elapsed time."""
        if self.elapsed < LUNGE_DURATION:
            return "lunge"
        if self.elapsed < self.t_flash:
            return "flash"
        if self.elapsed < self.t_float:
            return "recoil"
        return "float"

    def update(self, dt):
        """Update the animation state based on elapsed time."""
        super().update(dt)
        phase = self._phase()

        # set the attacker to run the first time the lunge phase starts
        if phase == "lunge" and not self._pose_lunge_done:
            self.attacker.set_animation("run")
            self._pose_lunge_done = True
            # play lunge sound effect
            play_sound(SFX["lunge"])

        if phase == "flash":
            # set the defender to hit the first time the flash phase starts and attacker to lunge
            if not self._pose_recover_done:
                self.attacker.set_animation("lunge")
                # if the defender has the "hit" animation, set it to hit
                if "hit" in self.defender.animations:
                    self.defender.set_animation("hit")
                self._pose_recover_done = True
            # fire the impact callback the first time the flash phase starts
            if not self._impact_fired:
                self._impact_fired = True
                if self.on_impact:
                    self.on_impact()  # update the HUD

        if phase == "recoil":
            if not self._pose_recoil_done:
                self.attacker.set_animation("idle")
            self._pose_recoil_done = True

        # calculate the attacker's offset based on the current phase
        if phase == "lunge":
            progress = self.elapsed / LUNGE_DURATION  # 0 -> 1
            self.attacker.offset_x = self.dx * progress
            self.attacker.offset_y = self.dy * progress
            self.attacker.scale_factor = 1 + (self.scale_target - 1) * progress  # grows when approaching the camera (uy > 0)
        elif phase == "flash":
            self.attacker.offset_x = self.dx  # attacker stays at max extension
            self.attacker.offset_y = self.dy
            self.attacker.scale_factor = self.scale_target  # reaches peak scale
        elif phase == "recoil":
            progress = (self.elapsed - LUNGE_DURATION - FLASH_DURATION) / RECOIL_DURATION  # 0 -> 1
            self.defender.offset_x = self.ux * self.recoil * progress  # knocked back along the blow
            self.defender.offset_y = self.uy * self.recoil * progress
        elif phase == "float":
            progress = (self.elapsed - self.t_float) / FLOAT_DURATION  # 0 -> 1
            # the attacker hops back in an arc (up then down) while keeping its eyes on the target
            self.attacker.offset_x = self.dx * (1 - progress)
            # sin pi * progress goes from 0 to 1 (if progress is 0 to 1), so this subtracts a value that goes from 0 to 1 (if progress is 0 to 1)
            self.attacker.offset_y = self.dy * (1 - progress) - RETURN_JUMP_HEIGHT * math.sin(math.pi * progress)
            self.defender.offset_x = self.ux * self.recoil * (1 - progress)
            self.defender.offset_y = self.uy * self.recoil * (1 - progress)
            self.attacker.scale_factor = 1 + (self.scale_target - 1) * (1 - progress)  # shrinks back to normal size

        # reset attacker and defender offsets once the full animation completes
        if self.is_done():
            # reset to zero offsets and default scale when animation finishes
            self.attacker.offset_x = 0
            self.attacker.offset_y = 0
            self.defender.offset_x = 0
            self.defender.offset_y = 0
            self.attacker.scale_factor = 1.0  # return to base scale
            # reset animations
            self.attacker.set_idle_pose()
            self.defender.set_idle_pose()

    def draw(self, surface):
        """Draw the animation (centered on attacker/defender)."""
        phase = self._phase()
        if phase == "flash":
            self._draw_flash(surface)
        elif phase == "float":
            self._draw_float(surface)

    def _draw_flash(self, surface):
        """Draw a fading flash circle over the defender."""
        # calculate progress when the flash should start (when lunge ends)
        progress = (self.elapsed - self.t_flash_start) / FLASH_DURATION   # 0 -> 1
        alpha = int(255 * (1 - progress))                             # fade out
        radius = FLASH_RADIUS
        # Create an overlay surface for the flash
        overlay = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # Draw the flash circle on the overlay surface
        pygame.draw.circle(overlay, (*FLASH_COLOR, alpha), (radius, radius), radius)
        # Blit the overlay surface on the screen
        surface.blit(overlay, (self.defender.x + self.defender.offset_x - radius, self.defender.y + self.defender.offset_y - radius))

    def _draw_float(self, surface):
        """Draw the floating damage number rising and fading."""
        # calculate elapsed time for the float phase
        float_elapsed = self.elapsed - self.t_float
        # calculate progress (0 -> 1)
        progress = float_elapsed / FLOAT_DURATION
        # stay fully opaque for the first part of the float, then fade out
        fade = (progress - FLOAT_FADE_START) / (1 - FLOAT_FADE_START)
        self._float_surf.set_alpha(255 if progress < FLOAT_FADE_START else int(255 * (1 - fade)))
        # calculate the y position of the text
        y = self.defender.y + self.defender.offset_y - 30 * self.defender.scale - FLOAT_SPEED * float_elapsed
        surface.blit(self._float_surf, (self.defender.x + self.defender.offset_x - self._float_surf.get_width() // 2, y))


class SpellParticle:
    """A single particle trailing behind a spell projectile."""
    def __init__(self, x, y, ux, uy, colors, radial=False, speed_mult=1.0, life=None):
        """
        Initialize a particle.

        Args:
            x: Initial x-coordinate
            y: Initial y-coordinate
            ux: Unit vector x-component of the projectile (for direction)
            uy: Unit vector y-component of the projectile (for direction)
            color: RGB tuple for the particle color
        """
        self.x = x
        self.y = y
        self.color = random.choice(colors)
        # if life is not specified, use the default particle life
        self.life = life if life is not None else PARTICLE_LIFE
        # Store the maximum life of the particle
        self.max_life = self.life
        # if radial is True, the particle will be spawned in a random direction (for explosions)
        # otherwise, it will be spawned in the direction opposite to the projectile
        if radial:
            angle = random.uniform(0, 2 * math.pi)  # full 360°
        else:  # direction opposite to the projectile with ±30° variation
            angle = math.atan2(-uy, -ux) + random.uniform(-0.52, 0.52)  # ±30° opposite

        # Randomize speed slightly around the base speed
        speed = PARTICLE_SPEED * speed_mult * random.uniform(0.6, 1.0)

        # Set velocity components
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.uniform(PARTICLE_MIN_RADIUS, PARTICLE_MIN_RADIUS + 2)

    def update(self, dt):
        """Update the particle's position and remaining life."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def is_alive(self):
        """Check if the particle is still alive."""
        return self.life > 0

    def draw(self, surface):
        """Draw the particle."""
        # Get the current progress (1 -> 0 as time goes on)
        progress = self.life / self.max_life
        # Calculate alpha and radius based on progress
        alpha = int(200 * progress)
        radius = self.radius * progress
        # if radius or alpha are too small, don't draw the particle
        if radius < 0.5 or alpha < 1:
            return
        size = int(radius * 2) + 2
        # create an overlay surface with per-pixel alpha
        overlay = pygame.Surface((size, size), pygame.SRCALPHA)
        # draw the particle circle
        pygame.draw.circle(overlay, (*self.color, alpha), (size // 2, size // 2), int(radius))
        surface.blit(overlay, (self.x - radius, self.y - radius))


class SpellAnimation(AttackAnimation):
    """Spell attack. Identical to AttackAnimation in Phase 2."""
    def __init__(self, attacker, defender, event, projectile_color, projectile_color_core, particle_colors, on_impact=None):
        # set base duration all animations will last this amount of time (seconds)
        duration = FLY_DURATION + FLASH_DURATION + FLOAT_DURATION
        super().__init__(attacker, defender, event, on_impact, duration)

        # override phase boundaries
        self.t_flash_start = FLY_DURATION          # flash starts when projectile lands
        self.t_flash       = FLY_DURATION + FLASH_DURATION
        self.t_float       = self.t_flash          # float starts when flash ends

        # set the projectile color
        self.projectile_color = projectile_color
        self.projectile_color_core = projectile_color_core
        self.particle_colors = particle_colors

        # secondary color for the impact rings (darker version)
        self.impact_color = (
            max(0, self.projectile_color[0] - 100),
            max(0, self.projectile_color[1] - 50),
            max(0, self.projectile_color[2] - 70),
        )

        # flag to indicate if the cast pose has been set
        self._pose_cast_done = False

        # flag to indicate if the cast sound effect has been played
        self._cast_sound_played = False

        # trail positions and fade for the projectile (spell effect)
        self.trail = deque(maxlen=TRAIL_LENGTH)  # Use a deque to store the last TRAIL_LENGTH positions
        self._trail_cleared = False

        # particles for the spell
        self.particles = []

    def _phase(self):
        """Returns the current phase."""
        if self.elapsed < FLY_DURATION:
            return "fly"
        if self.elapsed < self.t_flash:
            return "flash"
        return "float"

    def update(self, dt):
        """Update the spell animation."""
        # only increment elapsed time via Animation base class (only increment duration, not entire AttackAnimation logic)
        Animation.update(self, dt)

        phase = self._phase()

        # current projectile position (needed for continuous particle spawn)
        fly_progress = self.elapsed / FLY_DURATION if self.elapsed < FLY_DURATION else 1.0
        proj_x = self.attacker.x + (self.defender.x - self.attacker.x) * fly_progress
        proj_y = self.attacker.y + (self.defender.y - self.attacker.y) * fly_progress

        # play spell cast sound effect the first time the fly phase starts
        if phase == "fly" and not self._cast_sound_played:
            play_sound(SFX["cast_spell"])
            self._cast_sound_played = True
            # spawn particles at the attacker's position
            dx = self.defender.x - self.attacker.x
            dy = self.defender.y - self.attacker.y
            # Get the distance and unit vector for direction
            dist = max(1, math.hypot(dx, dy))
            ux, uy = dx / dist, dy / dist
            # Spawn particles
            for _ in range(PARTICLE_INITIAL_BURST):
                self.particles.append(SpellParticle(self.attacker.x, self.attacker.y, ux, uy, self.particle_colors))

        # set the defender to hit the first time the flash phase starts
        if phase == "flash" and not self._pose_cast_done:
            self.defender.set_animation("hit")
            self._pose_cast_done = True

        # trigger impact callback when the flash phase starts
        if phase == "flash" and not self._impact_fired:
            play_sound(SFX["spell_hit"])
            self._impact_fired = True
            if self.on_impact:
                self.on_impact()
            # Clear the trail when the spell hits the target (visual effect)
            if not self._trail_cleared:
                self.trail.clear()
                self._trail_cleared = True
            # spawn impact burst particles at defender position
            self.particles.clear()
            for _ in range(IMPACT_PARTICLE_COUNT):
                self.particles.append(SpellParticle(
                    self.defender.x + self.defender.offset_x,
                    self.defender.y + self.defender.offset_y,
                    0, 0,  # ux, uy ignored when radial=True
                    self.particle_colors,
                    radial=True,
                    speed_mult=IMPACT_PARTICLE_SPEED / PARTICLE_SPEED,
                    life=IMPACT_PARTICLE_LIFE,
                ))

        # update particles during fly and flash phases
        if phase in ("fly", "flash"):
            for p in self.particles:
                p.update(dt)
            # Keep only living particles
            self.particles = [p for p in self.particles if p.is_alive()]

        # continuous particle emission from current projectile position (fly only)
        if phase == "fly":
            for _ in range(PARTICLES_PER_FRAME):
                dx = self.defender.x - self.attacker.x
                dy = self.defender.y - self.attacker.y
                dist = max(1, math.hypot(dx, dy))
                ux, uy = dx / dist, dy / dist
                self.particles.append(SpellParticle(proj_x, proj_y, ux, uy, self.particle_colors))

        # reset offsets when animation finishes
        if self.is_done():
            self.attacker.offset_x = 0
            self.attacker.offset_y = 0
            self.defender.offset_x = 0
            self.defender.offset_y = 0
            self.attacker.scale_factor = 1.0
            # reset animations
            self.attacker.set_idle_pose()
            self.defender.set_idle_pose()

    def draw(self, surface):
        """Draw the spell animation."""
        phase = self._phase()
        if phase == "fly":
            self._draw_projectile(surface)
        elif phase == "flash":
            self._draw_impact(surface)
        elif phase == "float":
            super()._draw_float(surface)

    def _draw_projectile(self, surface):
        """Draw the projectile moving from attacker to defender."""
        # get the current animation progress (0 -> 1)
        progress = self.elapsed / FLY_DURATION
        # interpolate position from attacker to defender
        x = self.attacker.x + (self.defender.x - self.attacker.x) * progress
        y = self.attacker.y + (self.defender.y - self.attacker.y) * progress

        # add current position to trail
        self.trail.append((x, y))

        # draw the trail (spell effect) before drawing the projectile
        for i, (tx, ty) in enumerate(self.trail):  # iterate through the trail
            # i goes from 0 (oldest) to len-1 (most recent)
            t = (i + 1) / len(self.trail)  # 0 -> 1, from oldest to most recent
            trail_radius = TRAIL_MIN_RADIUS + (PROJ_RADIUS - TRAIL_MIN_RADIUS) * t  # radius of each point in the trail
            trail_alpha = int(TRAIL_MIN_ALPHA + (200 - TRAIL_MIN_ALPHA) * t)  # alpha of each point in the trail
            # create a surface for each point in the trail
            trail_overlay = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
            # draw a semi-transparent circle for each point in the trail
            pygame.draw.circle(trail_overlay, (*self.projectile_color, trail_alpha), (trail_radius, trail_radius), trail_radius)
            # blit the trail to the surface at the current position
            surface.blit(trail_overlay, (tx - trail_radius, ty - trail_radius))

        # 3-Layer radical glow around the projectile
        pulse = PULSE_AMPLITUDE * math.sin(PULSE_SPEED * self.elapsed)
        center_radius = PROJ_RADIUS // 2 + pulse * 0.5
        # layer data: (radius multiplier, alpha)
        glow_layers = [
            (2.5, 40),   # outer: large, very transparent
            (1.5, 70),   # middle: medium, semi-transparent
            (1.0, 100),  # inner: small, strongest glow
        ]
        # draw each glow layer from largest (outer) to smallest (inner)
        for multiplier, alpha in glow_layers:
            # calculate radius with pulse effect
            r = PROJ_RADIUS * multiplier + pulse
            size = int(r * 2)
            # create surface for the glow layer
            overlay = pygame.Surface((size, size), pygame.SRCALPHA)
            # draw the glow layer
            pygame.draw.circle(overlay, (*self.projectile_color, alpha), (int(r), int(r)), int(r))
            # blit the glow layer to the surface at the projectile's position
            surface.blit(overlay, (x - r, y - r))

        # bright core (center circle)
        core_size = int(center_radius * 2) + 2
        # create surface for the bright core
        core_overlay = pygame.Surface((core_size, core_size), pygame.SRCALPHA)
        # draw the bright core
        pygame.draw.circle(core_overlay, (*self.projectile_color_core, 255), (core_size // 2, core_size // 2), max(1, int(center_radius)))
        # blit the bright core to the surface at the projectile's position
        surface.blit(core_overlay, (x - core_size // 2, y - core_size // 2))

        # draw particles
        for p in self.particles:
            p.draw(surface)

    def _draw_impact(self, surface):
        """Draw expanding rings and a brief central flash on impact."""
        impact_elapsed = self.elapsed - FLY_DURATION  # time since impact
        center_x = self.defender.x + self.defender.offset_x
        center_y = self.defender.y + self.defender.offset_y

        # create expanding rings for the impact
        for i in range(IMPACT_RING_COUNT):
            delay = i * 0.15  # stagger start: ring 0 starts at 0s, ring 1 at 0.15s
            ring_elapsed = impact_elapsed - delay
            # if the ring has not started yet, skip it
            if ring_elapsed <= 0:
                continue
            # get the current ring progress (0 -> 1)
            ring_progress = ring_elapsed / FLASH_DURATION  # 0 -> 1
            # if the ring has finished expanding, skip it
            if ring_progress > 1:
                continue
            # calculate the radius and alpha of the current ring
            radius = IMPACT_RING_SPEED * ring_progress
            alpha = int(255 * (1 - ring_progress))
            width = max(1, IMPACT_RING_WIDTH - int(ring_progress * 2))  # width of the ring decreases as it expands
            # interpolate between primary and secondary color
            color = tuple(
                int(self.projectile_color[c] * (1 - ring_progress) + self.impact_color[c] * ring_progress)  # primary + secondary color
                for c in range(3)
            )
            # create a surface for the current ring
            ring_overlay = pygame.Surface((int(radius * 2) + 4, int(radius * 2) + 4), pygame.SRCALPHA)
            # draw the ring
            pygame.draw.circle(ring_overlay, (*color, alpha), (int(radius) + 2, int(radius) + 2), int(radius), width)
            # blit the ring to the surface at the impact position
            surface.blit(ring_overlay, (center_x - radius - 2, center_y - radius - 2))

        # brief central flash (0.05s) at the moment of impact
        if impact_elapsed < 0.05:
            flash_alpha = int(255 * (1 - impact_elapsed / 0.05))
            flash_radius = FLASH_RADIUS
            flash_overlay = pygame.Surface((flash_radius * 2, flash_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_overlay, (*self.projectile_color, flash_alpha), (flash_radius, flash_radius), flash_radius)
            surface.blit(flash_overlay, (center_x - flash_radius, center_y - flash_radius))

        # draw impact burst particles
        for p in self.particles:
            p.draw(surface)


class TextAnimation(Animation):
    """Shows a floating message that rises and fades above a sprite."""
    def __init__(self, sprite, text, color):
        # create an object that inherits from Animation with the duration of the animation
        super().__init__(FLOAT_DURATION)
        # set the sprite and pre-render the outlined message
        self.sprite = sprite
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont(FONT_NAME, FONT_FLOAT_SIZE)
        self._surf = render_outlined_text(self.font, text, color)

    def draw(self, surface):
        """Draw the text animation."""
        # calculate progress (0 -> 1)
        progress = self.elapsed / FLOAT_DURATION
        # stay fully opaque for the first part, then fade out
        fade = (progress - FLOAT_FADE_START) / (1 - FLOAT_FADE_START)
        self._surf.set_alpha(255 if progress < FLOAT_FADE_START else int(255 * (1 - fade)))
        # calculate the y position of the text
        y = self.sprite.y - 30 * self.sprite.scale - FLOAT_SPEED * self.elapsed
        # blit the text on the screen
        surface.blit(self._surf, (self.sprite.x - self._surf.get_width() // 2, y))


class EventPlayer:
    """Plays battle events as animations, one at a time, driven by dt."""
    def __init__(self, hero_sprite, enemy_sprite, on_event=None):
        # map each Character to its sprite, so events (which carry Characters) resolve to sprites
        self.sprites = {
            hero_sprite.character: hero_sprite,
            enemy_sprite.character: enemy_sprite,
        }
        # map each Character to its battle side ("hero" / "enemy"), to read snapshots
        self._sides = {
            hero_sprite.character: "hero",
            enemy_sprite.character: "enemy",
        }
        self.on_event = on_event   # optional callback(event) fired when an animation starts
        self.queue = deque()       # pending events
        self.current = None        # active Animation or None

    def push(self, event):
        """Queue an event to be animated."""
        self.queue.append(event)

    def _snapshot_of(self, character, event):
        """Return the (hp, mp) of a fighter recorded in the event snapshot."""
        # get the side of the character
        side = self._sides[character]
        # return the hp and mp of the character from the event snapshot
        return event[f"{side}_hp"], event[f"{side}_mp"]

    def _apply_display(self, character, hp=None, mp=None):
        """Update the HUD display values of a fighter's sprite."""
        # get the sprite of the character
        sprite = self.sprites[character]
        # update the hp if it's not None
        if hp is not None:
            sprite.display_hp = hp
        # update the mp if it's not None
        if mp is not None:
            sprite.display_mp = mp

    def _apply_stat_changes(self, event):
        """Sync the HUD display values for an event that just started animating.

        The engine snapshots every fighter's HP/MP at the moment each event is
        logged, so revealing them one animation at a time shows the round
        progressively instead of all at once.
        """
        action = event["action"]
        if action in ("attack", "spell"):
            # mana is spent as soon as the attack starts; the defender's HP
            # drops at the moment of impact (handled by the animation's callback)
            actor = event["attacker"]
            _, mp = self._snapshot_of(actor, event)
            self._apply_display(actor, mp=mp)
        elif action == "defeated":
            # the last HP drop: empty the defeated fighter's bar
            defender = event["defender"]
            hp, _ = self._snapshot_of(defender, event)
            self._apply_display(defender, hp=hp)
        else:
            # For actions like "heal", "potion", "guard", "flee", " victory", "defeat", "fled"
            # These actions may not have an "actor" (e.g. "fled", "victory", "defeat"), so we check if it exists
            actor = event.get("actor")
            if actor is not None:
                # get the hp and mp of the actor
                hp, mp = self._snapshot_of(actor, event)
                # update the display
                self._apply_display(actor, hp=hp, mp=mp)

    def _make_animation(self, event):
        """Build the right Animation for an event."""
        # get the action from the event
        action = event["action"]

        # if the action is attack, create an AttackAnimation
        if action in ("attack", "spell"):
            # the defender's HP is revealed at the moment of impact
            defender = event["defender"]
            hp = event[f"{self._sides[defender]}_hp"]
            # create an AttackAnimation for the attack event
            if action == "attack":
                return AttackAnimation(
                    self._sprite_of(event["attacker"]),
                    self._sprite_of(defender),
                    event,
                    on_impact=lambda: self._apply_display(defender, hp=hp)  # update the HUD when the animation impacts
                )
            # create an SpellAnimation for the spell event
            else:
                is_hero = self._sides[event["attacker"]] == "hero"
                return SpellAnimation(
                    self._sprite_of(event["attacker"]),
                    self._sprite_of(defender),
                    event,
                    COLOR_FIREBALL if is_hero else COLOR_SHADOW_BOLT,
                    COLOR_FIREBALL_CORE if is_hero else COLOR_SHADOW_BOLT_CORE,
                    FIREBALL_PARTICLE_COLORS if is_hero else SHADOW_BOLT_PARTICLE_COLORS,
                    on_impact=lambda: self._apply_display(defender, hp=hp)  # update the HUD when the animation impacts
                )

        # get the actor from the event. "defeated" has no "actor"
        actor = self._sprite_of(event.get("actor") or event.get("defender"))
        # get the text and color for the event
        text, color = self._text_for(event)
        # create a TextAnimation for the event
        return TextAnimation(actor, text, color)

    def _sprite_of(self, character):
        """Return the sprite of a character."""
        return self.sprites[character]

    def _apply_sprite_pose(self, event):
        """Apply the sprite pose for the given event."""
        action = event["action"]
        if action == "attack":
            self._sprite_of(event["attacker"]).set_animation("lunge")
        elif action == "spell":
            self._sprite_of(event["attacker"]).set_animation("use_magic")
        elif action == "guard":
            self._sprite_of(event["actor"]).set_animation("defend")
        elif action == "heal":
            self._sprite_of(event["actor"]).set_animation("use_magic")
        elif action == "potion":
            self._sprite_of(event["actor"]).set_animation("potion")
        elif action == "flee_success":
            self._sprite_of(event["actor"]).set_animation("flee")
        elif action == "defeated":
            self._sprite_of(event["defender"]).set_animation("defeated")
        else:
            # The animation is handled by the TextAnimation class, so we don't need to set a pose.
            pass

    def _reset_sprite_pose(self):
        """Reset the sprite pose for all characters."""
        # set all characters to idle if they are alive
        for character in self.sprites:
            if character.is_alive:
                self._sprite_of(character).set_idle_pose()

    def _text_for(self, event):
        """Return text and color for a given event."""
        # get the action from the event
        action = event["action"]

        # for every possible action, return the text and color for it
        if action == "guard":
            return "Guard", COLOR_GUARD
        elif action == "heal" or action == "potion":
            return f"+{event['amount']}", COLOR_HEAL
        elif action == "mana_fail":
            return "Not enough mana", COLOR_GRAY
        elif action == "potion_fail":
            return "No potions left", COLOR_GRAY
        elif action == "flee_success":
            return "Fled!", COLOR_GRAY
        elif action == "flee_fail":
            return "Failed to flee!", COLOR_GRAY
        elif action == "defeated":
            return "Defeated!", COLOR_CRIT

        # for every other case, return the event as a string and COLOR_GRAY
        return str(event), COLOR_GRAY

    def update(self, dt):
        """Advance the current animation; pull the next event when it finishes."""
        # if there is no current animation and there is a queue, pop the next event
        if self.current is None and self.queue:
            # get the next event
            event = self.queue.popleft()
            # apply the sprite pose
            self._apply_sprite_pose(event)
            # create the animation
            self.current = self._make_animation(event)
            # sync the HUD display values to this event's snapshot
            self._apply_stat_changes(event)
            # if there is an on_event callback, call it with the event
            if self.on_event:
                self.on_event(event)
            # play the sound effect for the action
            action = event["action"]
            if action in SFX and action != "spell":  # spell sound effect is handled in SpellAnimation class
                play_sound(SFX[action])
        # if there is a current animation, update it
        if self.current is not None:
            self.current.update(dt)
            # if the current animation is done, set it to None
            if self.current.is_done():
                # reset the sprite pose
                self._reset_sprite_pose()
                self.current = None

    def is_idle(self):
        """True when no animation is playing or waiting."""
        return self.current is None and not self.queue

    def draw(self, surface):
        """Draw the active animation effect on top of the sprites."""
        if self.current is not None:
            self.current.draw(surface)


# Base class for sprite of characters
class CharacterSprite:
    """Wraps a Character and draws it as a placeholder built with primitives."""
    def __init__(self, character, x, y, scale=1.0, animations=None, flip_x=False):
        self.character = character
        self.x = x
        self.y = y
        self.scale = scale
        self.offset_x = 0   # Horizontal offset for simple animation
        self.offset_y = 0   # Vertical offset for simple animation
        self.scale_factor = 1.0   # animated scale multiplier (depth during lunge)
        # values currently shown in the HUD; updated as each battle event animates
        self.display_hp = character.hp
        self.display_mp = character.mp
        self.animations = animations
        self.set_animation("idle")
        self.flip_x = flip_x  # Flip the sprite on the x-axis

    def set_animation(self, name):
        """Set the current animation."""
        self.animation_name = name
        self.current_animation = self.animations[name]
        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_speed = 0.1  # time to wait before switching to the next frame
        self.frame_count = len(self.current_animation)

    def set_idle_pose(self):
        """Set the current animation to idle or caution based on HP."""
        if self.display_hp / self.character.max_hp > 0.2:  # use display_hp instead of character.hp to show the current HP
            self.set_animation("idle")
        else:
            self.set_animation("caution")

    def update(self, dt):
        """Advance the current animation; pull the next event when it finishes."""
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % self.frame_count

    def draw(self, surface):
        """Draw the character as a placeholder rectangle with a border and a head."""
        # get the current frame from the animation
        frame = self.current_animation[self.frame_idx]

        # flip if needed (basic left/right mirroring)
        if self.flip_x:
            frame = pygame.transform.flip(frame, True, False)  # flip the sprite on the x-axis

        # scale the frame to the desired size
        scale = self.scale * self.scale_factor
        width = int(frame.get_width() * scale)
        height = int(frame.get_height() * scale)

        # smoothly scale the frame to the desired size
        scaled = pygame.transform.smoothscale(frame, (width, height))

        # Draw the character's sprite based on current animation and frame
        surface.blit(scaled, (self.x + self.offset_x - width // 2, self.y + self.offset_y - height // 2))


# class to display battle log
class LogPanel:
    """Displays the last N battle log messages inside a panel."""

    def __init__(self, rect, max_messages=6):
        self.rect = pygame.Rect(rect)
        # deque = queue with maximum length, removes the old value when a new one exceeds the maximum length limit
        self.messages = deque(maxlen=max_messages)

    # method to add message to the queue
    def add(self, text):
        self.messages.append(text)

    # method to wrap text into lines that fit within max_width pixels
    def _wrap(self, font, text, max_width):
        """Split text into lines that fit within max_width pixels."""
        lines = []
        current = ""
        # iterate over the words in the text
        for word in text.split(" "):
            candidate = current + " " + word if current else word
            # if the candidate text fits within max_width pixels, update the current text
            if font.size(candidate)[0] <= max_width:
                current = candidate
            # if the candidate text does not fit within max_width pixels, add the current text to the lines and update the current text
            else:
                lines.append(current)
                current = word
        # if the current text is not empty, add it to the lines
        if current:
            lines.append(current)
        return lines

    # method to draw the box of the log and show messages of the battle
    def draw(self, surface, font):
        # draw the box of the log
        bg = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg.fill((*PANEL_BORDER, PANEL_ALPHA))
        surface.blit(bg, self.rect.topleft)
        # draw the border of the log
        pygame.draw.rect(surface, PANEL_BORDER, self.rect, 2)
        # calculate max width for the lines
        max_width = self.rect.width - 10
        # create a list of wrapped lines from the messages in the queue (top to bottom)
        lines = [wrapped for text in self.messages
                for wrapped in self._wrap(font, text, max_width)]
        # calculate height position of first line
        y = self.rect.bottom - 8
        # iterate over the lines of messages (in reverse order) so the last message is at the bottom
        for line in reversed(lines):
            # get height of the line
            height = font.get_height()
            # stop rendering if we run out of panel height
            if y - height < self.rect.top + 8:
                break
            # render each line
            rendered = font.render(line, True, COLOR_TEXT)
            # blit the line on the surface
            surface.blit(rendered, (self.rect.left + 8, y - height))
            # update height position of next line
            y -= height + 4


# class menu (with methods to draw options and manage keyboard/mouse input)
class Menu:
    """Show menu options, manage selection and highlight"""
    def __init__(self, rect, options, font, border_color=None, accent_color=None, option_text_color=None):
        self.rect = pygame.Rect(rect)  # panel for menu
        self.options = options  # list of options (attack, skill, etc)
        self.font = font  # font to render options
        self.cursor = 0  # index of the currently selected option
        if border_color is None:
            self.border_color = PANEL_BORDER
        else:
            self.border_color = border_color
        if accent_color is None:
            self.accent_color = COLOR_ACCENT
        else:
            self.accent_color = accent_color
        if option_text_color is None:
            self.option_text_color = COLOR_TEXT
        else:
            self.option_text_color = option_text_color

    def move_cursor(self, delta):
        """Move cursor up or down, wrapping around the ends.

        Args:
            delta: +1 to move down, -1 to move up
        """
        # store the current selection, module (%) is used to wrap around the ends
        # (if cursor > options, it goes to the end; if cursor < 0, it goes to the begining)
        self.cursor = (self.cursor + delta) % len(self.options)
        # play cursor movement sound effect
        play_sound(SFX["cursor"])

    def index_at(self, pos):
        """Convert a pixel position into an option index (0-based), or return None if outside the menu area.

        Args:
            pos: (x, y) tuple of screen coordinates

        Returns:
            The index of the option at the given position, or None if outside the menu area.
        """
        # convert screen coordinates to coordinates relative to the menu's top-left corner
        x, y = pos

        # height of each row (option)
        row_height = self.font.get_height() + 8

        # check if pos is inside the menu area
        if not self.rect.collidepoint(x, y):
            return None

        # calculate the row index, rect.top convert to local coords of the panel
        index = (y - self.rect.top) // row_height

        # check if index is within the range of the options
        if 0 <= index < len(self.options):
            return index

        return None

    def handle_click(self, pos):
        """Handle a mouse click on the menu.

        Args:
            pos: (x, y) tuple of screen coordinates

        Returns:
            The index of the option clicked, or None if no option was clicked.
        """

        # by now only return the index of the option, later can be used to implement click logic
        return self.index_at(pos)

    def draw(self, surface):
        """Draw menu options on a panel at the bottom right of the screen.

        Args:
            surface: pygame surface to draw on
        """

        # Draw the background of the menu panel
        bg = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg.fill((*self.border_color, PANEL_ALPHA))
        surface.blit(bg, self.rect.topleft)

        # Draw the border of the menu panel
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        # get the height of each row (option)
        row_height = self.font.get_height() + 8

        # iterate over every option
        for i, option in enumerate(self.options):
            # calculate the rectangle for each option
            row_rect = pygame.Rect(self.rect.left, self.rect.top + i * row_height, self.rect.width, row_height)

            # highlight row if cursor is on it (is the current option selected by keyboard or mouse)
            if i == self.cursor:
                hl = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
                hl.fill((*self.accent_color, 200))
                surface.blit(hl, row_rect.topleft)
            # render option text
            text = self.font.render(option, True, self.option_text_color)
            # blit (draw) the option text centered in its row (half of the row height and half of the text height)
            surface.blit(text, (row_rect.centerx - text.get_width() // 2, row_rect.centery - text.get_height() // 2))


# methods to draw HUD
def draw_bar(surface, x, y, width, height, current_value, max_value, color):
    """Draw a proportional fill bar with background and border."""
    # Draw the background of the bar
    pygame.draw.rect(surface, COLOR_BAR_BG, (x, y, width, height))
    # Calculate the fill width based on current value and max value
    fill = int(width * current_value / max_value)
    # Draw the filled portion of the bar
    pygame.draw.rect(surface, color, (x, y, fill, height))
    # Draw the border of the bar
    pygame.draw.rect(surface, COLOR_BORDER, (x, y, width, height), 2)


def draw_hud(surface, sprite, font, rect):
    """Draw a fixed status card (Name, Health and Mana bars) at the given rect."""
    # get character of sprite
    char = sprite.character
    card = pygame.Rect(rect)                       # position comes from the caller
    # frame: background + border, same style as the other panels
    bg = pygame.Surface((card.width, card.height), pygame.SRCALPHA)
    bg.fill((*PANEL_BORDER, PANEL_ALPHA))
    surface.blit(bg, card.topleft)
    pygame.draw.rect(surface, PANEL_BORDER, card, 2)

    # Hero portrait from idle frame 0
    idle_frame = sprite.animations["idle"][0]  # frame 96x96
    head_crop = pygame.Rect(16, 8, 64, 56)     # head crop
    head = idle_frame.subsurface(head_crop).copy()
    head = pygame.transform.smoothscale(head, (48, 48))
    # head drawn at the left, centered vertically
    head_x = card.left + 8
    head_y = card.centery - 24
    surface.blit(head, (head_x, head_y))

    # name aligned at right of head
    text_x = card.left + 64  # 8 (margin) + 48 (head) + 8 (gap)
    name = font.render(char.name, True, COLOR_TEXT)
    surface.blit(name, (text_x, card.top + 6))

    # HP and MP bars below name
    bar_x = text_x
    bar_width = card.right - bar_x - 6  # remaining space minus margin
    draw_bar(surface, bar_x, card.top + 26, bar_width, BAR_HEIGHT, sprite.display_hp, char.max_hp, COLOR_HP_BAR)
    draw_bar(surface, bar_x, card.top + 42, bar_width, BAR_HEIGHT, sprite.display_mp, char.max_mp, COLOR_MP_BAR)


def draw_enemy_name(surface, sprite, font):
    """Draw the enemy's name above the enemy sprite."""
    # get character of sprite
    char = sprite.character
    # get name with render style
    name = font.render(char.name, True, COLOR_TEXT)
    # some space between the text and the border
    padding = 4
    # build the plate from the sprite's animated position, keeping it above its head
    bg_rect = pygame.Rect(0, 0, name.get_width() + padding * 2, name.get_height() + padding * 2)
    bg_rect.centerx = int(sprite.x + sprite.offset_x)
    bg_rect.centery = int(sprite.y + sprite.offset_y - 40 * (sprite.scale * sprite.scale_factor) - 36)
    bg = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg.fill((*PANEL_BORDER, PANEL_ALPHA))
    surface.blit(bg, bg_rect.topleft)
    # Draw the enemy's name centered in its rectangle, blit needs a tuple (x, y), not two separate numbers
    surface.blit(name, (bg_rect.centerx - name.get_width() // 2, bg_rect.centery - name.get_height() // 2))


def render_outlined_text(font, text, color):
    """Render text with a black 1px outline baked onto a transparent surface."""
    # render the text with the given font
    base = font.render(text, True, color)
    # render the outline
    outline = font.render(text, True, (0, 0, 0))
    # get the size of the text
    width, height = base.get_size()
    # create a surface for the text with the outline
    surf = pygame.Surface((width + 2, height + 2), pygame.SRCALPHA)
    # loop through the outline offsets
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                surf.blit(outline, (1 + dx, 1 + dy))
    surf.blit(base, (1, 1))
    return surf
