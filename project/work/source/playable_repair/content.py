"""Overlay exact delivered 1110 data. Preserve IDs and original-game menus."""
import csv,io,json
from life_repair.content import Author
from life_rework.content import csv_text
from ui_integrity.content import repair_csv


def build(base):
    a=Author(base)
    from playable_repair import school_content,sports_jobs,family_service,action_content
    for module in [school_content,sports_jobs,family_service,action_content]:
        if hasattr(module,'build'):module.build(a,base)
    # New and revised scenarios are resolved by every native annual controller.
    # Preserve its eligibility fields while using one authoritative definition.
    school_content.refresh_annual_copies(a,base)
    action_content.refresh_annual_copies(a,base)
    a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header))
    a.assets['genesis_rework_defaults']=csv_text(a.schema)
    return repair_csv(a.assets,base)
