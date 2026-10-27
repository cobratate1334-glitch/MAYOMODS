"""Restore only earlier war/post-war colours and the original illustrated log."""
import json
from pathlib import Path
from types import SimpleNamespace
from native_immersion.backgrounds import hooks as original_background

def hooks(b):
    templates=json.loads((Path(__file__).resolve().parent/'theme_templates.json').read_text())
    b.redirect(b.resolved('v46_native_era_theme_colors')['name'],templates['v46_native_era_theme_colors_1108_5'])
    b.redirect(b.resolved('v46_refresh_era_theme')['name'],templates['v46_refresh_era_theme'])
    # Reuse the audited original helper, with a fresh private root slot.
    # Original phase selection/country/date rules and 0.30 tint are unchanged.
    owner=SimpleNamespace(state=b.state,states=b.states,string=b.string,
        install=lambda name,site,code:b.install('restored_war_journal_background',site,code))
    original_background(owner)
