from content import *
c='newlife_body20';p=lambda k:G(c,k)
for k,v,lo,hi in [('Height',178,140,235),('Weight',72,40,180),('Reach',2,-10,20),('NativeBodyCommit20',0,0,1),('NativeBodyCancel20',0,0,1)]:prop(c,k,v,lo,hi)
prop('life_v18','AdultWeight',72,40,180);prop('life_v18','BodyVersion20',0,0,20)
menu(c,'New Life · Body & Build',[tile('Choose body measurements',S('newlife_body20'),'running-shoe'),tile('US regions and hazards',S('us_map20'),'earth'),tile('Start this life',M(c,'NativeBodyCommit20',1),'hero'),tile('Back to New Life',M(c,'NativeBodyCancel20',1),'memo')])
add('newlife_body20','Body & Build','Choose projected adult measurements for this new life. Childhood height and weight grow toward this build. Your original Appearance editor stays separate.',[('Adult height',home('newlife_heights20')),('Adult weight',home('newlife_weights20')),('Wingspan / reach',home('newlife_reach20')),('Back',home(c))],icon='running-shoe',tables=table(Adult_height_cm=p('Height'),Adult_weight_kg=p('Weight'),Wingspan_extra_cm=p('Reach')))
for kind,field,values in [('heights','Height',[140,150,160,168,175,178,183,190,198,203,208,213,220,225,230,235]),('weights','Weight',[40,45,55,65,72,75,85,95,105,115,130,150,180]),('reach','Reach',[-10,-5,0,2,5,10,15,20])]:
 items=[]
 for i,value in enumerate(values):
  label=f'{value} kg' if field=='Weight' else f'{value:+} cm compared with height' if field=='Reach' else f'{value} cm · {int(value/2.54)//12}′{round(value/2.54)%12}″'
  items.append(tile(label,seq(M(c,field,value),S('newlife_body20')),'running-shoe'))
 menu('newlife_'+kind+'20',{'Height':'Adult Height','Weight':'Adult Weight','Reach':'Wingspan'}[field],items)
# Legacy body editor links are safe read-only routes, never live measurement writes.
for name in ['heights','weights','reach']:
 menu(name,'My Measurements',[tile('Measurements are set in New Life',seq(M('life_v18','NativeLifeSync',1),S('body')),'running-shoe')])
 for i in range(20):add(name+str(i),'My Measurements','Choose body measurements when creating your next custom life.',[('My measurements',seq(M('life_v18','NativeLifeSync',1),S('body')))],icon='running-shoe')
