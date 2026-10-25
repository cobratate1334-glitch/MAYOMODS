"""Route, schema and gameplay regression checks using the actual content overlay."""
import copy,csv,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(SOURCE)]
from life_followup.content import build
from life_rework.content import scene
from life_rework.validate_content import Model as Previous
from social_roblox.test_content import Model as Foundation


class Model(Previous):
    def __init__(self,base,age=20):
        Foundation.__init__(self,age);self.assets={**base,**build(base)};self.rows={};self.native=[]
        for name,value in self.assets.items():
            if value.startswith('ScenarioID,'):self.rows.update({r['ScenarioID']:r for r in csv.DictReader(io.StringIO(value))})
        lines=self.assets['genesis_feature_containers'].splitlines();start=next(i for i,s in enumerate(lines)if s.startswith('ContainerId,'));self.registry=list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))))
        for row in self.registry:
            sheet=row.get('InitDataSheet')
            if not sheet or not self.assets.get(sheet,'').startswith('key,'):continue
            defs={r['key']:r for r in csv.DictReader(io.StringIO(self.assets[sheet]))};self.schemas[row['ContainerId']]=defs
            self.props[row['ContainerId']]={k:int(r['value'])if r['type']=='int'else r['value']for k,r in defs.items()}


def validate(base_path,out):
    base=json.loads(Path(base_path).read_text());m=Model(base);checks=[]
    def check(value,label):assert value,label;checks.append(label)
    icons={r['EmojiString']for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}
    for name,value in build(base).items():
        if not value.startswith('{'):continue
        data=json.loads(value)
        for item in data.get('Items',data.get('ListItems',[])):
            for action in item.get('ActionList',[]):
                for condition in action.get('ConditionList',[]):
                    if 'ScenarioID'in condition:
                        target=condition['ScenarioID'];check(target in m.rows,'list row has a real registered scenario '+str(target))
                    if 'ListID'in condition:check(condition['ListID']in m.assets,'list row has a registered child list')
    for row in [r for k,r in m.rows.items()if k.startswith('scenario.lifeRework.')]:
        check(row['EmojiString']in icons or row['EmojiString'].startswith(('mayomods49/','mayomods1104/')),'registered icon '+row['EmojiString'])
        for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):check(key in m.schemas[owner],'readable field '+owner+'.'+key)
        for i in range(1,5):
            if not row.get(f'Choice{i}_Text'):continue
            advanced=row[f'Choice{i}_AdvancedLogic'];routes=[row[f'Choice{i}_RouteTo']]
            if advanced:
                data=json.loads(advanced);routes=[c['then']['route_options'][0]['route_to']for c in data['cases']]+[data['else_when_no_matches']['route_options'][0]['route_to']]
                for c in data['cases']:m.condition(c['if'])
            for route in routes:
                check(isinstance(route,str),'flat Genesis destination')
                for part in m.split(route):
                    if part.startswith('scenario.'):check(part in m.rows,'registered scene '+part)
                    if part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in m.assets,'registered parent '+part)
                    if part.startswith('BP_GFC_'):
                        owner,key=part.split('=',1)[1].split(':',2)[:2];check(key in m.schemas[owner],'registered write '+owner+'.'+key)
    for age in [4,8,15,25]:
        t=Model(base,age);t.r['Year']=2026;t.choose('rap_entry1105');check(t.r['RapActive']==int(age>=8),'rapper entry age '+str(age))
    t=Model(base);t.r.update(Year=1915);t.choose('rap_entry1105');check(t.r['RapActive']==0,'no hip-hop career in 1915')
    t=Model(base,10);t.r.update(SchoolEligible=1,SchoolPeerPresent1105=1)
    t.choose('exam_start1105');t.choose('exam_1_1105',1);t.choose('exam_2_1105',2);t.choose('exam_3_1105',3);t.choose('exam_mark1105')
    check(t.r['ExamPoints1105']==3 and t.r['SchoolExam']==100 and 11 in t.native,'answers affect actual grade command; perfect paper is 100')
    snapshot=copy.deepcopy(t.r);t.choose('exam_mark1105');check(t.r==snapshot,'marked exam cannot award repeated grade')
    for sport,kind,answers in [('basket',11,[2,1,3]),('soccer',1,[2,3,1]),('football',3,[1,3,2])]:
        t=Model(base);before_skill=t.props['seasons_v18']['Skill'];t.r['SportsEligible'+str(kind)]=1;t.choose(sport+'_drill_start1105')
        for step,index in enumerate(answers,1):t.choose(sport+'_drill'+str(step)+'_1105',index)
        t.choose(sport+'_finish1105');check(t.r[sport.title()+'1105DrillPoints']==3 and t.props['seasons_v18']['Skill']>before_skill,'play reads improve existing '+sport+' season')
        snapshot=copy.deepcopy(t.props);t.choose(sport+'_finish1105');check(t.props==snapshot,'sports drill reward cannot replay '+sport)
    t=Model(base);t.r.update(NativeInPrison1105=1,NativeBank1105=1000,PrisonRecruitCap1105=8);t.choose('prison_gang_names1105',1)
    check(t.r['PrisonGang1105']==1 and 128 in t.native,'crew creation records native leader action')
    t.choose('prison_gang1105',2);check(t.r['PrisonRecruits1105']==2 and 127 in t.native,'recruitment records real roster name action')
    t=Model(base);t.r.update(NativeInPrison1105=0);t.choose('prison_gang_names1105',1);check(t.r['PrisonGang1105']==0,'free characters cannot form prison crews')
    t=Model(base);t.r.update(Married1105=1);t.choose('marriage_case1105',2);check(t.r['MarriagePhase1105']==2,'divorce filing persists')
    t.choose('marriage_hearing1105',2);check(t.r['NativeDivorce1105']==0,'same-age finalization rejected')
    t.age+=1;t.choose('marriage_hearing1105',2);check(t.r['NativeDivorce1105']==1,'later finalization reaches original divorce bridge')
    for strong in [False,True]:
        t=Model(base);t.r.update(RapDiss=70 if strong else 10,RapVocabulary=60 if strong else 10);before=t.props['music_studio']['Fans'];t.choose('rap_peer1105_0',3)
        check(t.props['music_studio']['Fans']-before==(150 if strong else 25),'diss skill changes the audience result '+str(strong))
        t=Model(base);t.r.update(RapFreestyle=70 if strong else 10,RapFlow=60 if strong else 10);before=t.r['RapRep'];t.choose('rap_peer1105_0',1)
        check(t.r['RapRep']-before==(4 if strong else 2),'freestyle and flow change respect '+str(strong))
    for injured in [False,True]:
        t=Model(base);t.r.update(NativeInPrison1105=1,PrisonFightStage1105=0,PrisonInjury1105=40 if injured else 0,PrisonStamina1105=45);t.choose('prison_round1_1105',1)
        check(t.r['PrisonFightScore1105']==int(not injured),'injury changes the same prison fight choice '+str(injured))
    check('energy'not in ' '.join(r['key'].lower()for r in csv.DictReader(io.StringIO(m.assets['genesis_rework_defaults']))),'rapper has no energy meter')
    report=dict(passed=True,checks=len(checks),scenarios=sum(k.startswith('scenario.lifeRework.')for k in m.rows),Genesis_API_modeled=True,phone_tested=False)
    Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)


if __name__=='__main__':validate(*sys.argv[1:])
