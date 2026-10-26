"""Small native code-reading exercises with saved intelligence consequences."""
from life_rework.content import p,scene,set_,inc,seq,logic


def build(a,base):
    a.prop('SpyAge1106',-1,-1,999);a.prop('SpyStep1106',0,0,3);a.prop('SpyScore1106',0,0,3)
    home=scene('war_country1106')
    a.page('war_information1106','News and intelligence','Your country’s wartime briefing, intelligence work and historical symbols.',[
        ('Intelligence exercise',scene('spy_start1106')),('Recruitment and propaganda',scene('war_propaganda1106')),('Historical flags',scene('war_flags1106')),('Back',home)],'newspaper')
    row=a.edit('war_country1106');row['Choice1_Text']='News and intelligence';row['Choice1_RouteTo']=scene('war_information1106')
    a.page('war_flags1106','Historical flags','The flag shown in the country briefing follows the wartime government. Imperial Germany and Nazi Germany use different designs. Italy shows its royal flag, and the United States uses its 48-star flag. Imperial Japan’s national flag is distinct from its naval ensign.',[
        ('Japanese naval ensign',scene('war_japan_ensign1106')),('Back',scene('war_information1106'))],'newspaper')
    a.page('war_japan_ensign1106','Japanese naval ensign','The rising-sun naval ensign was used by the Imperial Japanese Navy. It is shown here as a military ensign; the country briefing and civilian national flag use the red sun on white.',[('Back',scene('war_flags1106'))],'newspaper');a.edit('war_japan_ensign1106')['BigImageString']='mayomods1106/flags/jp_naval'
    guard=((f'({p("War")} == 0) || ({p("WarSide")} == 0) || (<hero:age> < 18)',scene('war_peace')),(f'({p("SpyAge1106")} >= <hero:age>)',scene('spy_wait1106')))
    start=a.gate(seq(set_('SpyAge1106','<hero:age>'),set_('SpyStep1106',0),set_('SpyScore1106',0),scene('spy_round1106_1')),extra=guard)
    a.page('spy_start1106','An intelligence desk exercise','Allied and Axis intelligence services use intercepted messages and field reports. Your task is a short training exercise: decode messages and check claims. It is separate from real historical cryptanalysis.',[('Begin the exercise',start),('Back',scene('war_information1106'))],'memo')
    rounds=[('The key is 1=A, 2=B, 3=C. Decode 231.',['CAB','BCA','ABC'],1),('The key is 1=C, 2=A, 3=B. Decode 312.',['BCA','CAB','ABC'],0),('A report claims a city is secure, but two independent observers report fighting there. What should you do?',['Repeat the first claim','Discard all three reports','Verify the conflicting accounts'],2)]
    for step,(question,answers,correct)in enumerate(rounds,1):
        choices=[]
        for i,answer in enumerate(answers):
            effects=[set_('SpyStep1106',step)]
            if i==correct:effects+=[inc('SpyScore1106')]
            next_=scene('spy_round1106_'+str(step+1))if step<3 else scene('spy_result1106')
            choices.append((answer,a.gate(seq(*effects,next_),extra=((f'({p("SpyStep1106")} != {step-1}) || ({p("SpyAge1106")} != <hero:age>)',scene('spy_wait1106')),))))
        a.page('spy_round1106_'+str(step),'Intelligence exercise · '+str(step)+'/3',question,choices,'memo')
    win=a.outcome('spy_success1106','Checked the dispatches and identified unreliable claims. The command office added your work to its intelligence briefing. Better intelligence improves campaign decisions.',scene('war_hub1106'),[set_('SpyStep1106',0),inc('WarIntel',15),inc('WarTraining',3)],extra=((f'({p("SpyStep1106")} != 3)',scene('spy_wait1106')),))
    lose=a.outcome('spy_failure1106','Misread the dispatches. The command office rejected the report and asked you to review the evidence before trying again next year.',scene('war_hub1106'),[set_('SpyStep1106',0),inc('WarIntel',-5)],extra=((f'({p("SpyStep1106")} != 3)',scene('spy_wait1106')),))
    a.page('spy_result1106','The intelligence report','Your answers determine whether the report is useful to command.',[('Hand in the report',logic([(f'({p("SpyScore1106")} >= 2)',win)],lose))],'memo')
    a.page('spy_wait1106','Exercise closed','You can complete one intelligence exercise each year. Old answers cannot award more intelligence.',[('Back to the briefing',scene('war_information1106'))],'memo')
