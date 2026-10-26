"""Small native parent pages and one clear World War Service entrance."""
import csv,io,json
from life_rework.content import csv_text,scene,menu,p,set_,logic


def build(a,base):
    a.prop('FieldReady1111',0,0,1)
    body='<GFC.relationship21.ParentAvailability1108><br>Age: <GFC.relationship21.SelectedAge1106><br>Born in: <GFC.relationship21.BirthCountry1106><br><br>Personality<br><GFC.relationship21.ParentCharacter1108><br><br>Life story<br><GFC.relationship21.Story>'
    for role in (0,1):
        row=a.edit('parent_'+str(role)+'1108');row.update(Body=body,ExteriorTitle='Family')
    a.page('stepparent1111','<GFC.relationship21.SelectedName1106>',body,[('Close','')],'handshake',stats=[('Discipline','<GFC.relationship21.Discipline1108>'),('Loyalty','<GFC.relationship21.Loyalty1108>'),('Kindness','<GFC.relationship21.Generosity1108>')])
    a.edit('stepparent1111')['ExteriorTitle']='Family'
    a.assets['genesis_stepparent1111']=json.dumps(dict(ListID='genesis_stepparent1111',Title='Personality & Life Story',PresentationMode='Normal',Items=[a.tile('Personality & Life Story',scene('stepparent1111'),'handshake','Their story and personality')]),indent=2)
    text=a.assets.get('genesis_feature_containers',base['genesis_feature_containers']);at=text.index('ContainerId,');registry=list(csv.DictReader(io.StringIO(text[at:])))
    template=registry[0];entry=dict.fromkeys(template,'');entry.update(ContainerId='stepparent1111',DisplayName='Personality & Life Story',EntryMenu='StepparentStory1111',EntryLabel='Personality & Life Story',EntryEmoji='handshake',EntrySecondLine='Their story and personality',EntryOrder='0',EntryListID='genesis_stepparent1111');registry.append(entry)
    for row in registry:
        if row['ContainerId']=='recruit1110':row.update(DisplayName='World War Service',EntryLabel='World War Service',EntrySecondLine='WWI and WWII drafts and missions')
        if row['ContainerId']=='military_entry1108':row.update(EntryLabel='My service',EntrySecondLine='Training and postings and benefits')
    a.assets['genesis_feature_containers']=text[:at]+csv_text(registry)
    a.page('world_war_service1111','World War Service','Open the draft office. Your country and age decide if you can serve.<br><br>Pass the medical check. Accept induction. Complete two drills. Then choose an assignment.',[
        ('Draft office',scene('native_draft1109')),('Training',scene('native_training1109')),('War missions',scene('world_war_missions1111')),('Back',menu('genesis_recruit1110'))],'rescue-helmet')
    wait=scene('world_war_training1111')
    a.page('world_war_training1111','Training comes first','You need a military job and two completed drills. Your country must be fighting in WWI or WWII.<br><br>Neutral countries have no world-war draft.',[('Draft office',scene('native_draft1109')),('Training',scene('native_training1109')),('Back',scene('world_war_service1111'))],'rescue-helmet')
    def ready(route):return logic([(f'({p("FieldReady1111")} != 1)',wait)],route)
    a.page('world_war_missions1111','War missions','Read the briefing. Choose your route. Watch your supplies.<br><br>Wrong moves can cause injuries or death.',[
        ('Trench patrol',ready(scene('trench_start1106'))),('Air mission',ready(scene('flight_start1106'))),('Clear a minefield',ready(set_('NativeMinefield1106',1))),('Back',scene('world_war_service1111'))],'rescue-helmet')
    a.assets['genesis_recruit1110']=json.dumps(dict(ListID='genesis_recruit1110',Title='World War Service',PresentationMode='Normal',Items=[
        a.tile('Draft office',scene('native_draft1109'),'rescue-helmet','Your call-up and medical check'),
        a.tile('Training',scene('native_training1109'),'boxing','Complete drills and choose a role'),
        a.tile('War missions',scene('world_war_missions1111'),'map','Trenches and aircraft and mines'),
        a.tile('War papers',scene('war_magazines1110'),'newspaper','Wartime news and magazines'),
        a.tile('How to serve',scene('world_war_service1111'),'memo','Four steps from call-up to orders'),
        a.tile('Veteran education',scene('gi_record1110'),'books','Check your college benefit')]),indent=2)
    # Old mission IDs remain valid for saves. Their deployed check formerly
    # required a stock deployment counter that training/assignment never set.
    for row in a.rows:
        if any(term in row['ScenarioID']for term in ['.trench_','.flight_','.war_missions1106']):
            for column,value in row.items():
                if isinstance(value,str) and '<GFC.life_rework.Deployed>'in value:row[column]=value.replace('<GFC.life_rework.Deployed>','<GFC.life_rework.FieldReady1111>')
    # Keep a compact shortcut inside the real military occupation menu.
    listing=json.loads(a.assets.get('genesis_military1108',base['genesis_military1108']))
    listing['Title']='My service'
    for row in listing['Items']:
        if row['Title']=='Draft & service':row.update(Title='Draft office',SecondLine='Your next service step')
        if 'minigames'in row['Title'].lower():row.update(Title='War missions',SecondLine='Trenches and aircraft and mines',ActionList=a.tile('War missions',scene('world_war_missions1111'),'map')['ActionList'])
    a.assets['genesis_military1108']=json.dumps(listing,indent=2)
