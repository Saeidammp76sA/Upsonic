"""Skills layer: local SKILL.md folders + builtin skills (summarization).

Upsonic's Skills container gives the agent progressive-disclosure tools
(list available skills / read a skill / run its scripts) automatically.
"""

from __future__ import annotations

from upsonic.skills import BuiltinSkills, LocalSkills, Skills

from config.settings import settings


def build_skills() -> Skills:
    return Skills(loaders=[
        LocalSkills(str(settings.skills.skills_dir)),
        BuiltinSkills(["summarization"]),
    ])
