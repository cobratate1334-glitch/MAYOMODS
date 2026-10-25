"""Author Life+ content using original BitLife table schemas and enum values.

Inspired by MusicLifeSim's social dilemmas and career setbacks. No imported
JavaScript, invented currencies, or unsupported save-state fields.
"""
import json, sys, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
if len(sys.argv)>1:
    import UnityPy
    from build_prison_expansion import decode,records
    with zipfile.ZipFile(sys.argv[1]) as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
    TABLES={}
    for obj in env.objects:
        if obj.type.name!='TextAsset':continue
        a=obj.read()
        if a.m_Name.endswith('-enc'):
            try:TABLES[a.m_Name]=records(decode(a.m_Script))
            except (ValueError,UnicodeError,AssertionError):pass
else:
    TABLES=json.loads((ROOT.parent/'firearms_inspection/tables.json').read_text())
CONTENT={}
def rows(name):
    h,*rs=TABLES[name]
    return [dict(zip(h,r)) for r in rs]
def add(name,row):
    h=TABLES[name][0]
    assert set(row)<=set(h),(name,set(row)-set(h))
    CONTENT.setdefault(name,[]).append({f:str(row.get(f,'')) for f in h})
def lines(s):return [x.strip() for x in s.strip().splitlines() if x.strip()]

# Choice annotations map to Karma, Discipline, Happiness, Intelligence,
# Appearance. Choices produce bounded stat changes, not imaginary payments,
# promotions, inventory items, or persistent club memberships.
EFFECTS={'care':(2,1,1,0,0),'learn':(0,2,0,2,0),'rest':(0,1,2,0,0),
 'social':(1,0,2,0,0),'bold':(0,-1,2,0,0),'avoid':(0,0,-1,0,0),
 'selfish':(-2,-1,1,0,0),'dishonest':(-2,-2,0,0,0),'focus':(0,3,-1,1,0),
 'speak':(1,1,0,1,0),'style':(0,1,1,0,1),'calm':(1,2,1,0,0)}
def event(line,group,number):
    title,body,*options=line.split('|')
    assert len(options)==4,(title,len(options))
    r={'Index':str(number),'Hero Min Age':'11' if group=='School' else '18',
       'Hero Max Age':'25' if group=='School' else '', 'Student':'x' if group=='School' else '',
       'Job':'x' if group=='Work' else '', 'Randomize Choices':'x',
       'Exterior Title':'School' if group=='School' else 'Situation',
       'Title':'Life+: '+title,'Body':body,'CTA':'What will you do?'}
    for i,o in enumerate(options,1):
        choice,narrative,profile=o.split('~')
        r[f'Choice {i}']=choice;r[f'Narrative {i}']=narrative
        for f,v in zip(['Karma','Discipline','Happiness','Intelligence','Appearance'],EFFECTS[profile]):
            r[f'{f} Impact {i}']=str(v) if v else ''
    add('a16_dumb-scenarios-universal-enc',r)

SCHOOL=r'''
Exam Freeze|Your mind goes blank during a practice exam.|Start with an easier question~I regained my focus by tackling an easier practice question.~calm|Ask for clarification~I asked for help understanding the practice exam instructions.~learn|Rush through every answer~I rushed my practice exam and barely checked my work.~bold|Leave the page blank~I gave up on a practice exam when I felt overwhelmed.~avoid
Study Group|A study group wants you to explain a topic you barely understand.|Admit I need help too~I admitted that I also needed help and learned with my study group.~learn|Research it before meeting~I prepared carefully before explaining a topic to my study group.~focus|Bluff my way through~I pretended to understand a topic during a study session.~dishonest|Suggest learning it together~I turned a confusing topic into a group learning session.~social
Lost Assignment|Your finished assignment has vanished just before the deadline.|Explain and show my notes~I explained my missing assignment and showed the work I could recover.~speak|Redo what I can~I rebuilt a missing assignment from my notes.~focus|Blame a classmate~I blamed someone else for my missing assignment.~dishonest|Give up on submitting~I let a missing assignment stop me from submitting any work.~avoid
Debate Nerves|You have been asked to open a class debate.|Prepare a short opening~I prepared a clear opening for a class debate.~learn|Practise with a friend~I rehearsed my debate opening with a friend.~social|Wing it confidently~I improvised my opening in a class debate.~bold|Ask for a smaller role~I requested a smaller role in a class debate.~calm
AI Essay|A classmate offers you an AI-written essay to submit as your own.|Write my own essay~I wrote my own essay instead of submitting someone else's work.~focus|Ask about permitted tools~I checked which study tools my teacher allowed.~speak|Submit it unchanged~I submitted an essay I had not written.~dishonest|Use it to quiz myself~I used sample material to test my understanding before writing my essay.~learn
Group Chat|A school group chat is filling up with jokes about one student.|Ask them to stop~I challenged unkind jokes in a school group chat.~care|Check on the student~I privately checked on a student being mocked online.~social|Join in~I joined in with jokes at another student's expense.~selfish|Mute the chat~I muted a school chat that was becoming unpleasant.~calm
New Student|A new student is sitting alone at lunch.|Invite them over~I invited a new student to sit with my lunch group.~social|Show them around~I helped a new student learn their way around school.~care|Wait for someone else~I left it to someone else to welcome a new student.~avoid|Ask about their interests~I started a conversation with a new student about their interests.~social
Club Clash|Two clubs you want to join meet at the same time.|Choose one priority~I chose the school club that mattered most to me.~focus|Ask about alternating~I asked club organisers whether I could alternate meetings.~speak|Promise both my time~I committed to two school clubs with conflicting schedules.~bold|Take time to decide~I gave myself time to choose between two school clubs.~calm
Science Fair|Your science fair prototype stops working before judging.|Explain what failed~I explained my experiment honestly even though the prototype failed.~learn|Try a simple repair~I tried a careful last-minute repair on my science fair prototype.~focus|Fake the results~I invented results for a failed science fair experiment.~dishonest|Present my research instead~I presented the research behind my unsuccessful science fair prototype.~speak
Talent Night|A school talent show has an unexpected empty slot.|Perform a short song~I sang a short song at my school's talent show.~bold|Help backstage~I helped keep the school talent show running backstage.~care|Encourage another performer~I encouraged another student to take an open talent show slot.~social|Stay in the audience~I enjoyed the school talent show from the audience.~rest
Library Queue|The library has only one copy of a book several students need.|Share a reading schedule~I organised a fair reading schedule for a popular library book.~care|Find another source~I found another source for my school research.~learn|Hide the book for myself~I hid a library book that other students needed.~selfish|Ask the librarian for help~I asked a librarian for help finding study material.~speak
Feedback Sting|Your teacher's feedback is much harsher than you expected.|Ask for specific improvements~I asked for concrete ways to improve my schoolwork.~learn|Take a break then revise~I cooled off before revising work after difficult feedback.~calm|Argue in front of everyone~I argued publicly about feedback on my schoolwork.~bold|Ignore every comment~I ignored feedback that could have helped my schoolwork.~avoid
Presentation Glitch|Your slides refuse to load in front of the class.|Present from my notes~I carried on with a presentation using my notes.~focus|Explain and restart calmly~I calmly restarted a presentation after a technical problem.~calm|Blame the equipment loudly~I complained about the equipment during a class presentation.~bold|Ask a classmate to help~I asked a classmate for technical help during my presentation.~social
Exam Rumour|Someone claims they have leaked answers to the upcoming exam.|Refuse the answers~I refused to use supposedly leaked exam answers.~care|Tell the teacher privately~I alerted a teacher to a rumoured exam leak.~speak|Read them in secret~I secretly looked at supposed exam answers.~dishonest|Stick to my revision~I kept revising rather than chasing an exam rumour.~focus
School Newspaper|The school newspaper wants your opinion on an unpopular rule.|Write a thoughtful response~I wrote a measured opinion for the school newspaper.~speak|Ask other students first~I listened to classmates before writing about a school rule.~social|Make up an outrageous quote~I invented a dramatic quote for the school newspaper.~dishonest|Decline to comment~I declined to comment on a school newspaper story.~calm
Forgotten Lunch|A classmate has forgotten their lunch.|Share what I can~I shared some lunch with a classmate who had none.~care|Help them ask staff~I helped a classmate ask school staff for lunch assistance.~speak|Tease them about it~I teased a classmate for forgetting their lunch.~selfish|Offer company anyway~I kept a classmate company when they had forgotten lunch.~social
Revision Burnout|You have spent every evening revising and feel exhausted.|Plan a proper break~I took a planned break after tiring myself out with revision.~rest|Switch to short sessions~I changed to shorter study sessions to recover my focus.~learn|Study all night again~I pushed through another exhausting night of revision.~focus|Stop preparing completely~I abandoned exam preparation when it became tiring.~avoid
Fundraiser Count|The school fundraiser's recorded total does not match the cash counted.|Count it again with someone~I checked a school fundraiser's accounts with another student.~care|Ask a teacher to review it~I asked a teacher to review a fundraiser discrepancy.~speak|Change the record quietly~I altered a fundraiser record without explaining the discrepancy.~dishonest|Leave a note for organisers~I documented a fundraiser discrepancy for the organisers.~focus
Field Trip Seat|Your friend wants you to save several bus seats for people who have not arrived.|Save just one seat~I set a reasonable limit on saving field trip seats.~calm|Let everyone choose fairly~I kept field trip seating fair for my classmates.~care|Block a whole row~I blocked a row of field trip seats for my own group.~selfish|Suggest sitting together later~I suggested meeting up after the field trip bus journey.~social
Dance Playlist|You are helping choose music for the school dance.|Collect classmates' suggestions~I asked classmates what music they wanted at the school dance.~social|Choose a balanced playlist~I helped build a varied school dance playlist.~learn|Play only my favourites~I made a school dance playlist entirely about my own taste.~selfish|Hand the task to a volunteer~I found another volunteer to help choose dance music.~care
Team Selection|A friend was not picked for a school team and is upset.|Listen without judging~I listened to a friend after a disappointing team selection.~care|Offer to practise together~I offered to practise with a friend who missed team selection.~social|Say they never had a chance~I discouraged a friend after they missed team selection.~selfish|Give them some space~I gave a disappointed friend time to collect their thoughts.~calm
Homework Copy|A friend asks to copy your finished homework.|Explain the method~I helped a friend understand homework without handing over my answers.~learn|Offer a quick study session~I worked through difficult homework with a friend.~social|Send the answers~I let a friend copy my homework.~dishonest|Politely refuse~I set a boundary when a friend wanted to copy my homework.~calm
Uniform Debate|Students want to discuss changing the school uniform policy.|Write a respectful proposal~I wrote a respectful proposal about the school uniform policy.~speak|Help run a student survey~I helped gather student views on school uniforms.~social|Interrupt the assembly~I interrupted an assembly to protest the uniform policy.~bold|Stay out of the debate~I stayed out of a debate about school uniforms.~calm
Lost Property|You find a valuable pair of headphones in a classroom.|Hand them to lost property~I handed found headphones to school lost property.~care|Ask whose they are~I asked classmates about a pair of lost headphones.~social|Keep them secretly~I kept headphones that someone had lost at school.~selfish|Tell a teacher where they are~I told a teacher about headphones left in a classroom.~speak
Peer Tutoring|A younger student asks for help with a difficult topic.|Explain it step by step~I patiently explained a difficult topic to a younger student.~learn|Use a simple example~I helped a younger student learn through a simple example.~care|Do the work for them~I completed work for a younger student instead of teaching them.~dishonest|Find someone better suited~I helped a younger student find a suitable tutor.~social
Class Election|You have been nominated as a class representative.|Offer realistic ideas~I campaigned for class representative with realistic ideas.~speak|Listen to what classmates need~I listened to classmates during a class election.~social|Promise impossible changes~I made unrealistic promises in a class election.~dishonest|Decline the nomination~I declined a class representative nomination.~calm
Digital Portfolio|Your teacher suggests keeping a portfolio of work you are proud of.|Choose work and reflect on it~I reflected on my strongest work for a school portfolio.~learn|Include unfinished experiments~I documented both finished work and experiments in my portfolio.~bold|Claim another student's work~I claimed someone else's work in my school portfolio.~dishonest|Start with one small piece~I started a school portfolio with one manageable piece of work.~focus
Career Day|A guest speaker's career sounds completely different from your plans.|Ask how they got started~I asked a career day guest about their first steps.~learn|Discuss it with classmates~I talked with classmates about unexpected career possibilities.~social|Dismiss it without listening~I dismissed a career day speaker without listening.~selfish|Take notes for later~I kept notes from a career day talk for future reflection.~focus
Deadline Collision|Three school projects are due in the same week.|Make a timetable~I planned my time around several overlapping school deadlines.~focus|Ask about flexible deadlines~I asked teachers about conflicting school deadlines.~speak|Work with a study partner~I coordinated study sessions during a busy school week.~social|Ignore the deadlines~I ignored several approaching school deadlines.~avoid
Quiet Classmate|A classmate rarely speaks during group work.|Invite their opinion gently~I made room for a quiet classmate to contribute.~care|Offer to read their notes~I helped a quiet classmate share written ideas.~social|Speak over them~I talked over a quiet classmate during group work.~selfish|Let them choose their role~I let a quiet classmate choose a comfortable group role.~calm
Art Critique|A classmate asks what you think of an unfinished drawing.|Offer kind specific feedback~I gave thoughtful feedback on a classmate's drawing.~care|Ask what they were aiming for~I asked a classmate about the idea behind their art.~learn|Mock the mistakes~I mocked a classmate's unfinished drawing.~selfish|Point out my favourite detail~I encouraged a classmate by noticing a strong detail in their drawing.~social
Coding Challenge|Your coding exercise works but you do not understand why.|Test it with different inputs~I tested my code to understand its behaviour.~learn|Ask a classmate to explain~I learned from a classmate during a coding exercise.~social|Copy more code blindly~I copied code without understanding it.~dishonest|Read the instructions again~I carefully reviewed the instructions for a coding exercise.~focus
Rumour Correction|A rumour about you is spreading around school.|Correct it calmly~I calmly corrected a false rumour at school.~speak|Speak to someone I trust~I sought support while dealing with a school rumour.~care|Start a rumour back~I retaliated against a school rumour with another rumour.~selfish|Avoid the conversation~I avoided confronting a rumour at school.~avoid
School Garden|The school garden needs volunteers during a busy week.|Help for a short session~I made time to help in the school garden.~care|Organise a shared rota~I helped organise volunteers for the school garden.~learn|Promise help then disappear~I promised to help in the school garden but did not show up.~dishonest|Support another volunteer~I encouraged someone else who could help the school garden.~social
Performance Credit|Your group gets praised but one member did most of the work.|Credit their contribution~I made sure a hardworking classmate received credit.~care|Thank the whole group~I thanked my group after a successful project.~social|Take all the praise~I took credit for work a classmate had mostly done.~selfish|Suggest fairer roles next time~I suggested sharing group project responsibilities more fairly.~speak
Mock Interview|Your class is practising job interviews.|Prepare examples of my skills~I prepared practical examples for a mock job interview.~learn|Practise with a partner~I rehearsed job interview answers with a classmate.~social|Invent achievements~I invented achievements during a mock interview.~dishonest|Ask for feedback afterwards~I asked for feedback after a practice job interview.~focus
Chess Upset|You lose a school chess match you expected to win.|Review the match~I studied my mistakes after losing a school chess match.~learn|Congratulate my opponent~I congratulated a classmate who beat me at chess.~care|Accuse them of cheating~I made an unsupported cheating accusation after a chess loss.~selfish|Take a break and try later~I recovered from a chess loss before playing again.~rest
Assembly Spotlight|You are unexpectedly asked to speak at assembly.|Share a brief thank-you~I gave a short thank-you when asked to speak at assembly.~social|Speak honestly about my nerves~I acknowledged my nerves while speaking at assembly.~speak|Make a joke and carry on~I used a joke to settle my nerves at assembly.~bold|Politely pass the microphone~I politely declined an unexpected assembly speech.~calm
Lab Partnership|Your lab partner keeps rushing the experiment instructions.|Read the instructions together~I checked experiment instructions with my lab partner.~learn|Ask the teacher to clarify~I asked for clarification before continuing a school experiment.~speak|Rush along with them~I rushed through a school experiment without checking instructions.~bold|Suggest swapping responsibilities~I agreed clearer responsibilities with my lab partner.~care
Study Playlist|Your favourite music keeps distracting you from revision.|Try instrumental music~I adjusted my study music to improve concentration.~learn|Use a timer and music breaks~I balanced study sessions with music breaks.~focus|Turn revision into karaoke~I let a study session turn into karaoke.~bold|Study in quiet~I chose a quiet space for revision.~calm
Open Day|Your school asks for volunteers to welcome visitors.|Guide a small group~I volunteered to show visitors around my school.~social|Help prepare displays~I helped prepare school open day displays.~care|Pretend to know every answer~I bluffed answers while showing visitors around school.~dishonest|Help with a task behind the scenes~I helped run a school open day behind the scenes.~focus
Practice Test|Your practice test result is lower than you hoped.|Identify weak topics~I used a practice test to identify what I needed to learn.~learn|Ask for a revision plan~I sought help making a better revision plan.~speak|Hide the result and forget it~I avoided learning from a disappointing practice test.~avoid|Give myself a calm reset~I regrouped calmly after a disappointing practice test.~rest
Class Podcast|Your class is recording a short podcast.|Research the topic~I researched material for a class podcast.~learn|Record an interview~I helped record an interview for a class podcast.~social|Invent a sensational story~I made up a sensational story for a school podcast.~dishonest|Edit the audio carefully~I carefully edited audio for a class podcast.~focus
Lunch Club|Students want a quiet lunchtime club for people who dislike noisy breaks.|Help organise it~I helped organise a quieter place to spend lunch breaks.~care|Suggest a simple activity~I suggested an inclusive activity for a lunchtime club.~social|Make fun of the idea~I mocked students for wanting a quieter lunch break.~selfish|Ask staff for a suitable room~I asked school staff about a space for a lunchtime club.~speak
Revision Shortcut|An online video claims you can master a subject in ten minutes.|Check it against my notes~I checked an online revision shortcut against my school notes.~learn|Use it as a quick recap~I treated a short revision video as a recap rather than a complete course.~focus|Trust it instead of studying~I relied on a revision shortcut instead of preparing properly.~avoid|Ask my teacher about it~I asked a teacher about an online revision claim.~speak
School Play|A performer drops out of the school play close to opening night.|Help run through the lines~I helped the school play cast rehearse after a setback.~care|Offer a smaller supporting role~I offered practical help to the school play.~social|Demand the lead immediately~I demanded a starring role when the school play had a vacancy.~selfish|Assist with props instead~I supported the school play by helping with props.~focus
Exchange Visitor|An exchange student wants to learn about everyday life at your school.|Describe my routine~I explained my school routine to an exchange student.~social|Ask about their school too~I learned about another school through an exchange student.~learn|Make up ridiculous rules~I invented false school rules to confuse an exchange student.~dishonest|Introduce them to classmates~I helped an exchange student meet more classmates.~care
Photo Permission|A classmate wants to post a photo of you that you dislike.|Ask them not to post it~I calmly set a boundary about a school photo.~speak|Suggest another photo~I helped find a photo everyone was comfortable sharing.~social|Post an embarrassing photo back~I retaliated in a disagreement about a school photo.~selfish|Discuss privacy with the group~I started a respectful discussion about photo privacy.~care
Sports Balance|School sport is taking up time you planned to use for study.|Plan both in advance~I balanced school sport and study with a clearer schedule.~focus|Talk to my coach~I discussed study pressures with my school coach.~speak|Skip studying repeatedly~I repeatedly chose sport over planned schoolwork.~bold|Take a short recovery break~I took a break to recover before balancing school commitments.~rest
End-of-Term Review|Your teacher asks you to reflect on the school term.|Name one improvement goal~I chose a clear learning goal for the next school term.~learn|Thank people who helped~I thanked the people who supported me through a school term.~care|Claim everything was perfect~I avoided honest reflection on my school term.~dishonest|Recognise progress and rest~I recognised my school progress and allowed myself a break.~rest
'''
GENERAL=r'''
Forgotten Birthday|You remember a friend's birthday late in the evening.|Send an honest message~I admitted I remembered a friend's birthday late and sent kind wishes.~care|Plan a belated catch-up~I suggested a belated birthday catch-up with a friend.~social|Pretend my message failed~I lied about why I missed a friend's birthday.~dishonest|Say nothing~I let a forgotten birthday pass without reaching out.~avoid
Family Expectations|Relatives keep comparing your plans with someone else's success.|Explain my own goals~I explained that my goals did not need to match someone else's.~speak|Ask about their concerns~I listened to family concerns before discussing my plans.~care|Turn it into an argument~I argued with relatives who compared me to someone else.~bold|Change the subject politely~I set aside an unhelpful family comparison.~calm
Overbooked Weekend|You promised to attend two gatherings on the same day.|Explain the clash early~I honestly explained conflicting weekend commitments.~care|Split my time carefully~I planned how to honour two weekend invitations.~focus|Invent an excuse for both~I invented excuses to escape conflicting invitations.~dishonest|Choose a quiet weekend~I decided I needed a quieter weekend.~rest
Old Hobby|You find something from a hobby you used to love.|Try it again for an hour~I revisited a hobby I once loved.~rest|Share the memory with a friend~I shared an old hobby memory with a friend.~social|Learn a new technique~I learned something new while revisiting an old hobby.~learn|Put it away again~I put away reminders of an old hobby without revisiting it.~avoid
Credit for Creativity|Someone shares your creative work without mentioning you.|Request a credit politely~I politely asked someone to credit my creative work.~speak|Explain why credit matters~I explained why creative credit mattered to me.~learn|Insult them publicly~I publicly insulted someone in a dispute over creative credit.~selfish|Thank people who noticed~I thanked people who recognised my creative work.~social
Community Poster|A community group needs help promoting a small event.|Design a simple poster~I helped design a poster for a community event.~care|Share accurate information~I shared accurate details about a community event.~social|Make exaggerated promises~I exaggerated what a community event would offer.~dishonest|Offer feedback on the draft~I gave useful feedback on a community poster.~learn
Unexpected Criticism|A stranger leaves a harsh comment on something you made.|Use the useful part~I found a useful lesson in harsh feedback.~learn|Ask a trusted friend~I asked a trusted friend for perspective on criticism.~social|Start a comment fight~I fought with a stranger over a harsh comment.~bold|Take a break from comments~I took a break after reading harsh online comments.~rest
Friend's Big News|A friend achieves something you have been working towards.|Congratulate them sincerely~I sincerely congratulated a friend on their achievement.~care|Ask what helped them~I learned from a friend's successful effort.~learn|Minimise their achievement~I belittled a friend's achievement out of jealousy.~selfish|Reflect on my own progress~I focused on my own progress after hearing a friend's good news.~calm
Budget Temptation|An advertisement makes an unnecessary purchase feel urgent.|Wait before deciding~I gave myself time before making an impulse purchase.~calm|Review my priorities~I reviewed my priorities after seeing a tempting advertisement.~learn|Keep browsing for hours~I let a tempting advertisement distract me for hours.~bold|Ask a friend for perspective~I sought perspective before reacting to a tempting advertisement.~social
Borrowed Keepsake|A friend returns a keepsake slightly damaged.|Explain why it matters~I explained why a damaged keepsake mattered to me.~speak|Ask what happened~I listened before reacting to a damaged keepsake.~care|Damage something of theirs~I retaliated after a borrowed keepsake was damaged.~selfish|Accept an apology calmly~I calmly accepted an apology about a damaged keepsake.~calm
Neighbour Noise|A neighbour's noisy hobby is interrupting your evenings.|Arrange a polite conversation~I discussed evening noise politely with a neighbour.~speak|Suggest agreed quiet hours~I suggested a fair schedule for a noisy hobby.~care|Make even more noise back~I retaliated against a noisy neighbour with more noise.~selfish|Find a quieter place to relax~I found a quieter way to spend an evening.~rest
Volunteer Shortage|A local volunteer event has fewer helpers than expected.|Help with a small task~I helped a volunteer event with a manageable task.~care|Contact willing friends~I asked friends if they could help a volunteer event.~social|Promise help without attending~I promised volunteer help but failed to attend.~dishonest|Help organisers simplify plans~I helped simplify plans for an understaffed volunteer event.~learn
Family Photo|Your relatives want a family photo when everyone is tired.|Keep it quick and kind~I helped make a tired family's photo session easier.~care|Suggest another time~I suggested taking a family photo at a better time.~calm|Complain through every photo~I complained throughout a family photo session.~selfish|Make everyone laugh~I lightened the mood during a family photo session.~social
Creative Slump|A project you care about has stopped feeling exciting.|Try a smaller experiment~I tried a small experiment to recover creative momentum.~learn|Rest and return later~I took a break from a project that felt stale.~rest|Ask a friend for ideas~I discussed a creative slump with a friend.~social|Pretend I never cared~I dismissed a project to avoid admitting I felt stuck.~avoid
Online Misunderstanding|A short message you sent has upset someone.|Clarify what I meant~I clarified a message that had been misunderstood.~speak|Apologise for the wording~I apologised for wording that caused confusion.~care|Tell them they are too sensitive~I dismissed someone who was upset by my message.~selfish|Talk in person instead~I chose a more personal conversation to clear up a misunderstanding.~social
Friendship Distance|You realise you have not checked in with a friend for months.|Send a thoughtful message~I reached out thoughtfully to a friend I had not seen in months.~care|Suggest a simple catch-up~I suggested a simple catch-up with an old friend.~social|Wait for them to reach out~I left an old friendship waiting for the other person to reach out.~avoid|Ask about their recent life~I asked an old friend how life had been treating them.~social
Skill Challenge|A friend invites you to try a hobby you know nothing about.|Let them teach me~I let a friend introduce me to an unfamiliar hobby.~learn|Try it with a sense of humour~I approached an unfamiliar hobby with humour.~social|Pretend I am an expert~I pretended to know more about a hobby than I did.~dishonest|Observe before trying~I watched and learned before attempting a new hobby.~calm
Public Praise|Someone praises you for a group effort.|Mention the others~I shared credit when praised for a group effort.~care|Thank them briefly~I graciously accepted praise for a group effort.~social|Take all the credit~I took all the credit for a group effort.~selfish|Explain what I learned~I reflected on what I learned from a successful group effort.~learn
Changed Plans|Bad weather ruins plans you were looking forward to.|Suggest an indoor alternative~I found an indoor alternative after bad weather changed plans.~social|Enjoy a quiet day~I made the most of a quiet day after plans changed.~rest|Blame everyone involved~I blamed others when weather disrupted my plans.~selfish|Reschedule calmly~I calmly rescheduled plans disrupted by weather.~calm
Family Advice|A relative gives advice that does not suit your situation.|Thank them and explain~I explained why a relative's advice did not fit my situation.~speak|Ask why they suggested it~I listened to the reasoning behind family advice.~care|Mock their experience~I mocked a relative's experience when rejecting advice.~selfish|Consider it privately~I reflected privately on advice from a relative.~learn
Digital Cleanup|Old notifications and unread messages are overwhelming you.|Sort them in small batches~I organised my digital clutter in manageable batches.~focus|Set notification boundaries~I set boundaries on distracting notifications.~calm|Reply thoughtfully to a few~I made time for a few important messages.~social|Ignore everything indefinitely~I let digital clutter keep building up.~avoid
Helpful Stranger|A stranger gives you useful help on a difficult day.|Thank them properly~I expressed gratitude to a stranger who helped me.~care|Help someone else later~I passed on a stranger's kindness.~social|Act as if it was owed~I acted entitled after a stranger helped me.~selfish|Remember what worked~I reflected on help that made a difficult day easier.~learn
Friend's Project|A friend wants honest feedback on an ambitious project.|Offer one practical suggestion~I offered useful feedback on a friend's project.~learn|Ask what support they need~I asked how I could support a friend's project.~care|Praise it without looking~I praised a friend's work without actually looking at it.~dishonest|Make time to review it~I carefully reviewed a friend's creative project.~focus
Disappointing Milestone|Reaching a personal milestone feels less exciting than expected.|Reflect on what it means~I reflected honestly on a personal milestone.~learn|Celebrate quietly with someone~I marked a milestone with a quiet celebration.~social|Compare myself to everyone~I let comparisons overshadow a personal milestone.~avoid|Take time to rest~I gave myself time to rest after reaching a milestone.~rest
Borrowing Boundaries|A friend keeps borrowing small things without asking.|Set a clear boundary~I set a respectful boundary about borrowing my things.~speak|Ask them to check first~I asked a friend to get permission before borrowing.~care|Hide their belongings back~I retaliated in a disagreement about borrowing.~selfish|Discuss a fair arrangement~I discussed a fair borrowing arrangement with a friend.~calm
Family Tradition|You are asked to help continue a family tradition.|Learn its history~I learned more about a family tradition.~learn|Help in my own way~I contributed to a family tradition in a way that suited me.~care|Dismiss it as pointless~I dismissed a family tradition without listening.~selfish|Suggest a small update~I suggested a thoughtful update to a family tradition.~social
Local Performance|A small local performer has a nearly empty audience.|Stay and listen~I supported a local performer by listening.~care|Invite a friend over~I invited a friend to support a local performance.~social|Heckle for attention~I heckled a performer to draw attention to myself.~selfish|Notice something to learn~I learned from watching a small local performance.~learn
Overnight Success|An acquaintance seems to have become successful overnight.|Ask about the unseen effort~I learned about the work behind someone else's success.~learn|Congratulate them~I congratulated an acquaintance on their success.~care|Spread a jealous rumour~I spread a rumour out of jealousy over someone else's success.~dishonest|Refocus on my own goals~I refocused on my goals after hearing about someone else's success.~focus
Reunion Awkwardness|An old acquaintance expects you to remember every detail of your shared past.|Admit my memory is hazy~I admitted that I did not remember every detail of an old acquaintance.~speak|Ask them to remind me~I invited an old acquaintance to share their memories.~social|Invent a shared story~I invented a memory to impress an old acquaintance.~dishonest|Enjoy the conversation anyway~I enjoyed reconnecting without pretending to remember everything.~calm
Lost Wallet|You spot a wallet left behind in a public place.|Give it to venue staff~I handed a found wallet to the venue's staff.~care|Ask staff to locate the owner~I helped staff try to locate a lost wallet's owner.~speak|Walk away without telling anyone~I left a lost wallet without notifying anyone.~avoid|Keep it for myself~I kept a wallet that someone had lost.~selfish
Neighbour's Garden|A neighbour asks you to watch their garden while they are away.|Agree only to what I can do~I made a realistic commitment to help a neighbour.~care|Ask for clear instructions~I asked for clear instructions before helping a neighbour.~learn|Promise more than I can manage~I overpromised when asked to help a neighbour.~dishonest|Politely decline~I politely declined a favour I could not manage.~calm
Personal Boundaries|Someone keeps sending messages late at night.|Explain my quiet hours~I explained my boundaries around late-night messages.~speak|Reply the next day~I kept my evening quiet and replied the next day.~rest|Send an angry rant~I responded angrily to late-night messages.~bold|Mute notifications politely~I protected my rest by muting late-night notifications.~calm
Shared Playlist|Your friends want everyone to contribute to a shared playlist.|Add a few thoughtful picks~I contributed thoughtful choices to a shared playlist.~social|Listen to unfamiliar picks~I explored music my friends recommended.~learn|Remove everyone else's songs~I made a shared playlist all about my own taste.~selfish|Help keep it varied~I helped maintain variety in a shared playlist.~care
Memory Box|You find a box of old photos and notes.|Organise a few favourites~I organised some favourite personal memories.~focus|Share a memory with someone~I shared a fond memory with someone from my past.~social|Take a quiet moment~I took a quiet moment to reflect on old memories.~rest|Put it aside for now~I set aside a box of memories until I had more time.~calm
Learning Setback|A new skill is taking much longer to learn than you hoped.|Break it into small steps~I broke a difficult skill into manageable steps.~learn|Find a patient mentor~I sought help from a patient mentor.~social|Claim I already mastered it~I pretended to have mastered a skill I was still learning.~dishonest|Take a short break~I rested before returning to a challenging new skill.~rest
Friend's Burnout|A friend seems drained after a busy run of commitments.|Listen and check in~I checked in with a friend who seemed exhausted.~care|Suggest a low-pressure hangout~I offered an exhausted friend a relaxed catch-up.~social|Demand more of their time~I pressured an exhausted friend for more attention.~selfish|Give them breathing room~I gave a tired friend some breathing room.~calm
Community Dispute|A community group is divided over a small change.|Listen to both sides~I listened to different views in a community disagreement.~learn|Suggest a trial period~I suggested a measured compromise in a community dispute.~speak|Escalate the argument~I escalated a small community disagreement.~bold|Help summarise shared goals~I helped people find common ground in a community dispute.~care
Offline Evening|You realise you have spent the entire evening scrolling.|Put the phone away~I chose to step away from scrolling for the evening.~rest|Message one friend meaningfully~I turned passive scrolling into a real conversation.~social|Keep scrolling until morning~I let scrolling consume the rest of my night.~avoid|Learn something useful instead~I redirected my screen time towards learning.~learn
Celebration Pressure|People expect a bigger celebration than you wanted.|Explain what feels right~I explained how I wanted to celebrate a personal occasion.~speak|Plan something simple together~I planned a simple celebration with people close to me.~social|Agree then complain all evening~I agreed to a celebration then complained throughout it.~selfish|Take time to decide~I gave myself time to choose a comfortable celebration.~calm
Small Kindness|You notice someone struggling with a simple task.|Ask if they want help~I politely offered help to someone who seemed to need it.~care|Show a useful shortcut~I shared a useful way to make a task easier.~learn|Make fun of them~I mocked someone who was struggling with a task.~selfish|Give them space if they decline~I respected someone's choice to handle a task themselves.~calm
'''
WORK=r'''
Credit at Work|A colleague presents your idea without mentioning your contribution.|Clarify my role calmly~I calmly clarified my contribution to a workplace idea.~speak|Speak to them privately~I privately discussed sharing credit with a colleague.~care|Start a public argument~I argued publicly over credit at work.~bold|Document future contributions~I started keeping clearer records of my workplace contributions.~focus
Training Opportunity|Your workplace offers an optional training session during a busy week.|Make a realistic plan~I planned time for optional workplace training.~focus|Ask for the materials~I requested training materials to study at a suitable time.~learn|Sign up and never attend~I signed up for workplace training without attending.~dishonest|Discuss priorities with my supervisor~I discussed training and workload priorities with my supervisor.~speak
Meeting Overload|Back-to-back meetings leave little time for your actual work.|Suggest a shorter agenda~I suggested a clearer agenda to make meetings more useful.~speak|Protect a focused work block~I planned focused work time around meetings.~focus|Complain without offering ideas~I complained about meetings without suggesting improvements.~bold|Ask what can be postponed~I clarified priorities during a meeting-heavy week.~learn
New Coworker|A new coworker is struggling to understand the team's routines.|Explain the basics~I helped a new coworker understand team routines.~care|Share a useful checklist~I shared practical guidance with a new coworker.~learn|Let them struggle alone~I left a new coworker to struggle with unfamiliar routines.~selfish|Introduce them to teammates~I helped a new coworker meet the team.~social
Presentation Setback|A work presentation does not go as smoothly as you planned.|Ask for useful feedback~I asked for feedback after a difficult work presentation.~learn|Review it calmly~I calmly reviewed a disappointing work presentation.~calm|Blame a teammate~I blamed a teammate for my work presentation difficulties.~dishonest|Practise the weak sections~I practised the parts of a presentation that needed work.~focus
Inbox Flood|Your inbox fills with urgent-looking messages at once.|Sort genuine priorities~I identified real priorities in a crowded work inbox.~focus|Ask for deadline clarity~I asked for clearer deadlines on incoming work.~speak|Mark everything done without reading~I falsely marked unread work as complete.~dishonest|Handle one task at a time~I dealt with a busy work inbox one task at a time.~calm
Shared Deadline|A teammate is falling behind on a deadline you both share.|Ask what help they need~I offered practical support on a shared deadline.~care|Agree a revised task split~I agreed clearer responsibilities for a shared work deadline.~learn|Take over and resent them~I took over a shared task without discussing it.~bold|Raise the risk early~I reported a shared deadline risk before it became a crisis.~speak
Breakroom Debate|A breakroom conversation is turning into a heated argument.|Change to a lighter topic~I helped cool a heated breakroom conversation.~social|Set a respectful boundary~I set a respectful boundary in a workplace debate.~speak|Provoke both sides~I stirred up a workplace argument for entertainment.~selfish|Return to my work~I stepped away from a heated workplace conversation.~calm
Feedback Request|Your supervisor asks what would help the team work better.|Give a practical suggestion~I gave a practical suggestion to improve teamwork.~learn|Mention an overlooked success~I highlighted something the team was doing well.~care|Insult the team's competence~I insulted the team when asked for constructive feedback.~selfish|Ask colleagues for input~I gathered colleagues' views before giving team feedback.~social
Unclear Assignment|You receive a work task with almost no instructions.|Ask focused questions~I asked clear questions about an unclear work assignment.~speak|Summarise my understanding~I checked my understanding before starting a work task.~learn|Pretend I understand~I pretended to understand a vague work assignment.~dishonest|Draft a simple plan~I made a careful first plan for an unclear work task.~focus
Work-Life Balance|A coworker expects instant replies after your workday ends.|Explain my availability~I explained when I could reasonably respond to work messages.~speak|Discuss a response schedule~I helped set realistic expectations for work messages.~care|Answer all night and lose sleep~I let work messages consume my rest time.~focus|Protect a quiet evening~I took a quiet evening away from work messages.~rest
Small Error|You notice a small mistake in work you already submitted.|Flag it and correct it~I openly corrected a mistake in submitted work.~care|Check whether it affects anything~I assessed the impact of a small work error.~learn|Hide it and hope~I concealed a mistake in my work.~dishonest|Ask for a second check~I asked someone to help verify a correction.~social
Mentor Advice|A mentor suggests a career path you had not considered.|Ask about the first steps~I asked a mentor how to explore a new career direction.~learn|Reflect on what suits me~I reflected on career advice from a mentor.~calm|Pretend I have decided already~I pretended to have firm career plans when I did not.~dishonest|Talk to someone in that field~I sought another perspective on a possible career path.~social
Team Milestone|Your team completes a difficult project.|Thank the quiet contributors~I thanked less-visible contributors to a successful project.~care|Share what we learned~I reflected on lessons from a team project.~learn|Claim I carried everyone~I claimed sole credit for a team achievement.~selfish|Enjoy a modest celebration~I enjoyed a modest celebration after a team project.~social
Job Advertisement|An interesting job advertisement makes you question your current direction.|Compare the requirements~I carefully compared a possible job's requirements with my skills.~learn|Discuss my longer-term goals~I discussed my longer-term career goals with someone I trusted.~social|Boast that I am leaving immediately~I boasted about changing jobs before making a plan.~bold|Write a realistic development plan~I planned how to develop towards future career options.~focus
Customer Confusion|A customer has misunderstood what your team can provide.|Clarify the limits politely~I explained realistic limits to a confused customer.~speak|Ask what they actually need~I listened carefully to understand a customer's needs.~care|Promise something impossible~I made an unrealistic promise to a customer.~dishonest|Find someone who can clarify~I found suitable help for a customer's question.~learn
Late Recognition|Your recent effort has gone unnoticed.|Explain what I completed~I calmly described work that had gone unnoticed.~speak|Keep a clear work record~I kept a clearer record of my completed work.~focus|Undermine another colleague~I undermined a colleague to draw attention to myself.~selfish|Seek honest feedback~I asked for feedback on work that had not received recognition.~learn
Shared Resources|Two teams need the same limited workplace equipment.|Arrange a fair schedule~I helped arrange fair access to shared workplace equipment.~care|Discuss alternatives~I explored alternatives to a shared equipment bottleneck.~learn|Reserve everything for myself~I monopolised equipment that other teams needed.~selfish|Ask for priorities to be clarified~I asked for clarity on competing equipment needs.~speak
Office Rumour|A workplace rumour suggests a major change is coming.|Wait for verified information~I waited for reliable information about a workplace change.~calm|Ask a suitable person~I asked an appropriate person about a workplace rumour.~speak|Spread a dramatic version~I exaggerated a rumour about a workplace change.~dishonest|Focus on today's tasks~I focused on current work instead of chasing rumours.~focus
Shift Swap|A coworker asks for a shift swap that would disrupt your plans.|Explain my limits kindly~I kindly explained why a shift swap would be difficult.~care|Look for a fair compromise~I helped look for a fair solution to a shift request.~speak|Agree then fail to show~I agreed to a shift arrangement and did not honour it.~dishonest|Check my schedule first~I checked my commitments before agreeing to a shift swap.~focus
Difficult Feedback|A coworker reacts badly to feedback you gave.|Listen to their perspective~I listened to a coworker's response to difficult feedback.~care|Make the feedback more specific~I clarified feedback so it was more useful.~learn|Repeat it more harshly~I escalated a disagreement about workplace feedback.~selfish|Arrange a calmer conversation~I suggested a calmer discussion about feedback.~calm
Lunch Invitation|Coworkers invite you to lunch when you feel drained.|Join briefly~I joined coworkers for a brief lunch catch-up.~social|Explain I need quiet time~I politely took a quiet lunch break.~rest|Accept then ignore everyone~I accepted a lunch invitation but ignored my colleagues.~selfish|Suggest another day~I suggested catching up with coworkers another day.~calm
Task Shortcut|A shortcut would save time but bypass an important review.|Keep the review~I kept an important review step in my work.~care|Suggest a better process~I suggested a more efficient process that preserved review.~learn|Skip it and hide it~I concealed a skipped workplace review.~dishonest|Ask for approval first~I asked before changing a work process.~speak
Remote Misread|A colleague reads your brief work message as rude.|Clarify the tone~I clarified the tone of a brief work message.~speak|Apologise for unclear wording~I apologised for a work message that sounded harsher than intended.~care|Mock their reaction~I mocked a colleague for misunderstanding a message.~selfish|Arrange a quick conversation~I cleared up a work misunderstanding through conversation.~social
Learning Curve|A new workplace tool feels frustratingly complicated.|Practise with a small task~I learned a new workplace tool through manageable practice.~learn|Ask for a demonstration~I asked for a demonstration of an unfamiliar work tool.~social|Pretend it is working~I pretended to understand a work tool that confused me.~dishonest|Take notes and try again~I used notes to improve with a new workplace tool.~focus
Career Comparison|A former classmate's promotion leaves you feeling behind.|Review my own goals~I reviewed my own career goals after hearing someone else's news.~learn|Congratulate them~I congratulated a former classmate on a promotion.~care|Belittle their role~I belittled someone else's promotion out of jealousy.~selfish|Recognise my own progress~I recognised my own progress without comparing careers.~calm
Volunteer Lead|Your team needs someone to coordinate a small internal project.|Offer a clear plan~I offered a practical plan for an internal project.~focus|Share leadership responsibilities~I suggested sharing responsibility for a team project.~care|Demand control without a plan~I demanded control of a workplace project without preparing.~selfish|Support another organiser~I supported a colleague organising an internal project.~social
Onboarding Notes|Your team's guidance document is outdated.|Suggest accurate updates~I suggested corrections to outdated workplace guidance.~learn|Ask new staff what is confusing~I asked new staff where guidance could be clearer.~care|Copy errors into the new version~I reused inaccurate guidance without checking it.~dishonest|Improve one section carefully~I carefully improved part of an onboarding document.~focus
Quiet Achievement|You complete a task that solved a recurring problem.|Explain the useful improvement~I explained how my work addressed a recurring problem.~speak|Write down the solution~I documented a useful workplace solution.~learn|Keep it secret to feel essential~I withheld a useful solution to make myself seem indispensable.~selfish|Share it with the team~I shared a helpful solution with my colleagues.~care
Career Reset|You feel uncertain about the next stage of your working life.|List what matters to me~I reflected on what mattered in my working life.~learn|Speak with someone I trust~I discussed career uncertainty with someone I trusted.~social|Pretend nothing needs thought~I avoided reflecting on my career direction.~avoid|Make one manageable plan~I made a manageable plan for my next career steps.~focus
'''
for group,data,want in [('School',SCHOOL,50),('Life',GENERAL,40),('Work',WORK,30)]:
    assert len(lines(data))==want,(group,len(lines(data)))
    for l in lines(data):event(l,group,200001+len(CONTENT.get('a16_dumb-scenarios-universal-enc',[])))

# New careers inherit supported qualifications/company types, then receive
# distinct visible career and promotion names. Generic existing icons apply.
CAREERS=r'''
Game Designer|Mobile App Developer
Game Quality Analyst|Mobile App Developer
Cybersecurity Analyst|Mobile App Developer
Cloud Systems Engineer|Mobile App Developer
Data Analyst|Mobile App Developer
User Experience Designer|Animator
Digital Illustrator|Animator
Motion Graphics Designer|Animator
Accessibility Specialist|Mobile App Developer
Technical Writer|Writer
Copy Editor|Writer
Content Strategist|Public Relations
Community Manager|Public Relations
Event Coordinator|Public Relations
Sustainability Coordinator|Corporate Analyst
Research Coordinator|Professor
Museum Educator|Museum Worker
Archive Technician|Librarian
Literacy Coordinator|Librarian
Learning Support Officer|Teacher
Education Programme Coordinator|Teacher
Student Services Officer|Academic Administrator
Library Programme Coordinator|Librarian
Audio Editor|Disk Jockey
Podcast Producer|Disk Jockey
Music Rights Coordinator|Public Relations
Live Sound Technician|Disk Jockey
Lighting Technician|Set Designer
Production Coordinator|Set Designer
Location Coordinator|Set Designer
Brand Designer|Animator
Market Research Analyst|Corporate Analyst
Customer Experience Analyst|Corporate Analyst
Operations Coordinator|Corporate Analyst
Quality Assurance Coordinator|Corporate Analyst
Recruitment Coordinator|Corporate Analyst
Training Coordinator|Corporate Analyst
Logistics Planner|Corporate Analyst
Digital Archivist|Librarian
Exhibition Coordinator|Museum Worker
'''
career_names={r['Career']:r for r in rows('a16_careers-enc')}
# Resolve actual baseline labels explicitly rather than assuming names.
ALIASES={'Public Relations':'Business Analyst','Corporate Analyst':'Business Analyst',
 'Professor':'Professor','Museum Worker':'Museum Worker','Librarian':'Librarian',
 'Teacher':'School Teacher','Academic Administrator':'School Administrator','Set Designer':'Set Designer'}
for l in lines(CAREERS):
    name,base=l.split('|');base=ALIASES.get(base,base)
    assert base in career_names,base
    r=career_names[base].copy();r.update({'Career':name,'Seniority Track':f'Assistant {name}, {name}, Senior {name}',
      'Seniority Track Years':'12','Can Skip Positions':'0','Required Working Years':'0',
      'Commonness Score':'3','Max Fame':'','Holiday':'','Exclude Third Persons':'','Unavailable':'',
      'Diseases':'','Gender':'','Min Age':'18','Max Age':'','Too Old Age':'85',
      'Starting Salary':'$32,000.00','Salary Cap':'$105,000.00','Stress Score':'3'})
    if base in ['Disk Jockey','Writer']:r['Required Education']='High School';r['Required Major']=''
    add('a16_careers-enc',r)

PARTTIME=r'''
Homework Club Assistant|Grader
Peer Study Mentor|Grader
Campus Media Assistant|Office Assistant
Student Helpdesk Assistant|Office Assistant
Open Day Assistant|Campus Tour Guide
School Bookroom Assistant|Library Assistant
Reading Programme Assistant|Library Assistant
Research Survey Assistant|Lab Assistant
Student Events Assistant|Office Assistant
Digital Archive Assistant|Library Assistant
Library Shelving Assistant|Library Assistant
Community Garden Assistant|Camp Counselor
Weekend Market Assistant|Department Store Associate
Craft Fair Assistant|Department Store Associate
Board Game Cafe Assistant|Ice Cream Scooper
Museum Visitor Assistant|Office Assistant
Exhibition Desk Assistant|Office Assistant
Art Studio Assistant|Office Assistant
Music Rehearsal Assistant|Office Assistant
Recording Studio Runner|Office Assistant
Podcast Editing Assistant|Office Assistant
Theatre Programme Seller|Concessions Attendant
Venue Cloakroom Assistant|Concessions Attendant
Festival Information Assistant|Concessions Attendant
Community Centre Receptionist|Gym Receptionist
Charity Shop Assistant|Department Store Associate
Repair Cafe Assistant|Bike Shop Mechanic
Plant Nursery Assistant|Flower Shop Assistant
Aquarium Visitor Assistant|Office Assistant
Bookshop Assistant|Department Store Associate
Toy Shop Assistant|Department Store Associate
Mobile Device Setup Assistant|Office Assistant
Print Shop Assistant|Office Assistant
Photo Booth Attendant|Concessions Attendant
Sports Centre Attendant|Gym Receptionist
Weekend Bakery Assistant|Donut Maker
Homework Resource Assistant|Grader
Student Newsletter Assistant|Grader
Campus Accessibility Assistant|Campus Tour Guide
Community Workshop Assistant|Camp Counselor
'''
pt={r['Job']:r for r in rows('a16_part-time-jobs-enc')}
for i,l in enumerate(lines(PARTTIME)):
    name,base=l.split('|');r=pt[base].copy();r.update({'Job':name,'Gender':'','Min Age':'16','Max Age':'',
      'Min Hourly Rate':'$10 ','Max Hourly Rate':'$22 ','Commonness Score':'3','Tiring Score':'2',
      'Min Weekly Hours':'4','Max Weekly Hours':'16','Requires Driving License':'','Requires Vehicle':'',
      'Must Be Student':'x' if i<10 or 36<=i<39 else '', 'Min Intelligence':'20',
      'Min Appearance':'','Min Happiness':'','Min Health':''})
    if i in [4,7,38]:r['Min Age']='18'
    add('a16_part-time-jobs-enc',r)

CLUBS=r'''
Game Development Club|Hobby|Nerd Activity
Digital Art Club|Arts|Arts Activity
Animation Club|Arts|Arts Activity
Podcast Club|Arts|Arts Activity
Songwriting Club|Arts|Arts Activity
Music Production Club|Arts|Band Activity
Sound Design Club|Arts|Arts Activity
Stagecraft Club|Arts|Acting Activity
Screenwriting Club|Arts|Arts Activity
Documentary Club|Arts|Arts Activity
Media Literacy Club|Career Interest|Nerd Activity
Cybersecurity Club|Career Interest|Nerd Activity
Data Science Club|Career Interest|Nerd Activity
App Design Club|Career Interest|Nerd Activity
Accessibility Design Club|Community|Nerd Activity
Digital Citizenship Club|Community|Nerd Activity
Community Garden Club|Community|
Peer Mentoring Club|Community|
Volunteer Projects Club|Community|
Local History Club|Hobby|Nerd Activity
Citizen Science Club|Hobby|Nerd Activity
Climate Action Club|Community|
Renewable Energy Club|Career Interest|Nerd Activity
Entrepreneurship Club|Career Interest|
Personal Finance Club|Career Interest|Nerd Activity
Tabletop Design Club|Hobby|Gaming Activity
Esports Strategy Club|Hobby|Gaming Activity
Stop-Motion Club|Arts|Arts Activity
Digital Photography Club|Arts|Arts Activity
Public Speaking Workshop|Career Interest|
'''
template=rows('a16_school-activities-enc')[1]
for i,l in enumerate(lines(CLUBS),200121):
    name,kind,flag=l.split('|');r=template.copy()
    for f in ['Sports Activity','Nerd Activity','Band Activity','Arts Activity','Acting Activity','Gaming Activity','Weeb Activity']:r[f]=''
    r.update({'Index':str(i),'Activity':name,'Type':kind,'Commonness':'3','Weekly Hours':'4',
      'Min Grades':'','Min Smarts':'20' if flag=='Nerd Activity' else '',
      'Exists in Middle School':'x','Exists in High School':'x','Exists in College':'x'})
    if flag:r[flag]='x'
    add('a16_school-activities-enc',r)

def school_actions(table,data,kind='General'):
    for action in lines(data):
        r={'Type':kind,'Feedback Scenario':'You '+action+'.','Log Version':'I '+action.replace('your','my').replace('you appreciated','I appreciated')+'.',
          'Elementary School':'','High School':'x','College':'x',
          'Third Person':'<classmate> '+action.replace('your','their')+'.','Seriousness Score':'1',
          'Hero Min Age':'11','Hero Max Age':'25','Classmate Gender':'both','Clean':'x'}
        add(table,{k:v for k,v in r.items() if k in TABLES[table][0]})

CALLOUTS=r'''
asks why you brought revision notes to a practice session
reads your typo aloud even after you corrected it
calls your careful question a waste of time
suggests you copied a good answer without checking
jokes about your presentation nerves in front of the class
compares your project unfairly with another student's
criticises your handwriting instead of discussing your ideas
interrupts your explanation before hearing it out
announces your low practice mark to everyone
refuses to acknowledge a correction you made
teases you for carrying extra study materials
calls your chosen project topic boring
singles you out when several students are talking
makes a joke about your unfamiliar vocabulary
insists your original drawing must have been traced
reads an unfinished draft aloud without asking
dismisses a reasonable request for clearer instructions
compares your quietness with a more outgoing classmate
accuses you of not listening while you are taking notes
criticises your presentation outfit during the lesson
laughs at your first attempt to pronounce a new word
calls your organised folder obsessive
suggests your club is pointless in front of classmates
announces that your essay title sounds childish
criticises your choice of library book without explaining why
calls your helpful suggestion a distraction
mocks your careful pronunciation during a reading exercise
assumes you caused a group project's delay
describes your practice answer as embarrassing
tells the class your question should have been obvious
'''
for action in lines(CALLOUTS):
    add('a16_school-teacher-call-outs-enc',{'Type':'General','Feedback Scenario':'In class, <teacher> '+action+'.',
      'Log Version':'<teacher> '+action.replace('your','my').replace('you','me')+'.',
      'Elementary School':'','High School':'x','College':'x','Inappropriateness Score':'2'})

SUCKUPS=r'''
thanked <teacher> for clear revision guidance
made a neat thank-you card for <teacher>
offered to tidy classroom materials after <teacher-possessive> lesson
complimented <teacher-possessive> useful presentation slides
said <teacher-possessive> example finally made a topic clear
left a positive note about <teacher-possessive> patience
offered to organise books for <teacher>
asked <teacher> for a recommendation for extra reading
thanked <teacher> for helpful project feedback
praised <teacher-possessive> clear explanations to classmates
made a small paper bookmark for <teacher>
offered to help prepare a classroom display for <teacher>
said you appreciated <teacher-possessive> fair grading
thanked <teacher> for noticing your progress
helped collect worksheets for <teacher>
complimented <teacher-possessive> enthusiasm for the subject
offered to help distribute class materials for <teacher>
thanked <teacher> for staying after class to explain a topic
pointed out how much clearer <teacher-possessive> new diagram was
offered to label shared classroom folders for <teacher>
left <teacher> a note about your favourite lesson
thanked <teacher> for making room for quieter students
praised <teacher-possessive> careful approach to an experiment
offered to help sort the class resource shelf for <teacher>
said <teacher-possessive> feedback helped you revise a draft
thanked <teacher> for explaining a difficult word
offered to set out chairs before <teacher-possessive> presentation
complimented <teacher-possessive> choice of reading material
said <teacher-possessive> class inspired a new hobby
thanked <teacher> for a thoughtful end-of-term review
thanked <teacher> for helping you prepare for an exam
praised <teacher-possessive> well-organised lesson notes
offered to help archive old classroom handouts for <teacher>
said <teacher-possessive> practice quiz revealed what you needed to revise
thanked <teacher> for encouraging your creative ideas
complimented <teacher-possessive> useful reading recommendations
offered to help carry lightweight teaching materials for <teacher>
thanked <teacher> for listening to your questions
praised <teacher-possessive> clear field trip instructions
said <teacher-possessive> lesson helped you understand a difficult concept
'''
school_actions('a16_school-teacher-suckups-enc',SUCKUPS)
DISRESPECT=r'''
rolled your eyes dramatically while <teacher> explained a task
called <teacher-possessive> lesson a loading screen
claimed <teacher-possessive> slides belonged in a museum
gave <teacher> an exaggerated slow clap
imitated <teacher-possessive> instructions under your breath
asked <teacher> if the lesson came with a skip button
said <teacher-possessive> homework needed a refund
called <teacher-possessive> explanation a plot hole
claimed <teacher> was arguing with the dictionary
announced that <teacher-possessive> worksheet had defeated everyone
pretended to fall asleep while <teacher> answered a question
called <teacher-possessive> timetable a personal attack
made a sarcastic award for <teacher-possessive> longest lecture
interrupted <teacher> with a fake sports commentary
claimed <teacher-possessive> example needed a sequel
asked <teacher> to put the lesson on fast-forward
called <teacher-possessive> surprise quiz a villain origin story
said <teacher-possessive> marking pen needed a holiday
compared <teacher-possessive> lesson to an endless tutorial
announced that <teacher> had lost the class audience
pretended to review <teacher-possessive> lesson like a bad film
said <teacher-possessive> instructions required a decoder
asked <teacher> whether the homework had a fan club
described <teacher-possessive> lecture as an endurance event
said <teacher-possessive> lesson title was misleading advertising
mocked <teacher-possessive> carefully drawn diagram
gave <teacher-possessive> explanation an imaginary one-star rating
said <teacher-possessive> worksheet was your new sworn enemy
interrupted <teacher> with a sarcastic round of applause
claimed <teacher-possessive> lesson needed a better soundtrack
'''
school_actions('a16_school-teacher-disrespects-enc',DISRESPECT)
ACTUP=r'''
answered every question in the voice of a sports commentator
made a paper crown and wore it throughout the lesson
started a dramatic countdown to the end of class
held up an imaginary applause sign after each answer
narrated your note-taking like a nature documentary
pretended your pencil was a microphone during instructions
wrote fake movie credits at the end of your worksheet
made a tiny paper flag for every wrong answer
conducted an imaginary orchestra while the class read quietly
whispered a dramatic theme tune whenever the door opened
tried to turn the attendance register into a talent show
announced fictional weather reports from your desk
held a silent staring contest during group instructions
pretended to interview your eraser about the lesson
made a desk sign saying you were on a lunch break
answered a serious question with an unrelated slogan
read worksheet headings in a theatrical trailer voice
started a running tally of how often the clock ticked
pretended to auction your unfinished homework
gave an imaginary acceptance speech for finishing one question
folded your notes into a paper throne
introduced every group member as a celebrity guest
made elaborate sound effects while opening your folder
announced a fictional advert break halfway through class
kept asking whether the lesson had downloadable content
pretended the classroom floor was a dance stage
used a ruler as an imaginary television remote
gave a dramatic farewell to a snapped pencil
made a fake documentary about the classroom clock
bowed to your classmates after borrowing a pen
'''
school_actions('a16_school-act-up-scenarios-enc',ACTUP)
MESS=r'''
gave <classmate> an imaginary award for loudest pencil sharpener
left <classmate> a harmless note written entirely backwards
challenged <classmate> to explain a joke that made no sense
pretended to interview <classmate> about a missing eraser
made a silly paper nameplate for <classmate>
sent <classmate> an exaggerated review of the cafeteria queue
offered <classmate> a fake certificate for surviving Monday
challenged <classmate> to a silent dramatic eyebrow contest
gave <classmate> a deliberately ridiculous study tip
asked <classmate> to name an imaginary classroom mascot
drew a tiny cartoon of <classmate-possessive> overstuffed backpack
called <classmate-possessive> desk a command centre
challenged <classmate> to read a tongue twister
pretended <classmate> was a famous pencil collector
left <classmate> a paper ticket to an imaginary homework concert
asked <classmate> to judge a competition between two erasers
gave <classmate> a silly nickname based on a classroom joke
challenged <classmate> to explain the lesson using only sound effects
described <classmate-possessive> notes as a secret treasure map
offered <classmate> an imaginary medal for finding a spare pen
'''
school_actions('a16_school-classmate-mess-scenarios-enc',MESS)

TRIPS=r'''
a community printmaking studio|art
a local animation exhibition|art
a public sculpture garden|art
a photography conservation workshop|art
a theatre costume exhibition|art
a community mural gallery|art
a regional design museum|art
a renewable energy learning centre|science
a planetarium with guided demonstrations|science
a robotics discovery lab|science
a botanical research garden|science
a weather observation centre|science
a marine discovery exhibition|science
a geology learning centre|science
a local railway heritage museum|history
a community oral history archive|history
a restored historic town hall|history
a printing press heritage workshop|history
a regional migration history exhibition|history
a historic communication technology museum|history
'''
for l in lines(TRIPS):
    location,theme=l.split('|');add('a16_backtoschool-field-trip-location-enc',{'Location':location,'Theme':theme,'Hero Minimum Age':'11','Hero Maximum Age':'17'})
TRIP_COLOR=r'''
You learned how artists plan a mural before painting it.|learning|art
You compared a rough sketch with the finished painting.|learning|art
You tried a simple printmaking demonstration.|learning|art
You learned why museum lighting matters for fragile artwork.|learning|art
You saw how animation frames create the impression of movement.|learning|art
You asked how a sculptor chooses materials.|learning|art
You noticed details in a photograph that you had missed at first.|learning|art
You learned how theatre costumes tell a story.|learning|art
You compared several interpretations of the same artwork.|learning|art
You learned why artists keep experiment notebooks.|learning|art
You watched a small robot follow a programmed route.|learning|science
You learned how weather measurements are recorded.|learning|science
You compared several renewable energy models.|learning|science
You saw how researchers label plant samples.|learning|science
You learned how fossils can preserve evidence of ancient life.|learning|science
You asked how a telescope is focused.|learning|science
You watched a model demonstrate water filtration.|learning|science
You learned why scientists repeat measurements.|learning|science
You compared different materials under a microscope.|learning|science
You learned how a controlled experiment isolates one question.|learning|science
You listened to recorded memories from local residents.|learning|history
You compared old maps with the streets you know today.|learning|history
You learned how messages travelled before mobile phones.|learning|history
You saw how a printing press helped spread information.|learning|history
You read a diary describing an ordinary day long ago.|learning|history
You compared historic clothing with modern styles.|learning|history
You learned why archives preserve everyday documents.|learning|history
You asked how historians check conflicting accounts.|learning|history
You looked at old photographs of a familiar landmark.|learning|history
You learned how transport changed the local community.|learning|history
You and <classmate> compared your favourite exhibits.|socializing|
You helped <classmate> find the right meeting point.|socializing|
You and <classmate> swapped questions to ask the guide.|socializing|
You and <classmate> planned a short summary of the trip.|socializing|
You and <classmate> laughed about your oversized packed lunches.|socializing|
You tried to narrate the trip like a dramatic documentary.|goofing off|
You counted every gift-shop souvenir shaped like an animal.|goofing off|
You posed like an imaginary tour guide for your classmates.|goofing off|
You gave your packed lunch a theatrical introduction.|goofing off|
You invented a silly award for the longest exhibit label.|goofing off|
'''
for l in lines(TRIP_COLOR):
    s,f,t=l.split('|');add('a16_backtoschool-field-trip-color-enc',{'String':s,'Focus':f,'Theme':t})
THEMES=lines('''Neon Nights
Under the Stars
Retro Arcade
Enchanted Garden
Ocean Lights
Winter Lanterns
Golden Hour
Rainbow Disco
Comic Book Gala
Space Odyssey
Silver Screen
Midnight Carnival
Electric Dreams
Secret Garden
Festival of Colours
Vintage Promenade
Moonlight Ball
Pixel Party
Around the World
Music Through Time''')
for t in THEMES:add('a16_backtoschool-school-dance-theme-enc',{'Theme':t})
DANCE_FEEDBACK=lines('''You helped a nervous classmate feel welcome on the dance floor.
You discovered that your quietest classmate had excellent dance moves.
You and your friends invented a ridiculous group dance.
The DJ played a song your group had requested.
You spent more time laughing with friends than dancing.
You helped untangle a decoration before anyone tripped over it.
Your shoes turned out to be less comfortable than you expected.
You enjoyed a slow conversation away from the speakers.
You recognised a song from a childhood playlist.
You cheered when a shy classmate joined the dance floor.
You learned a new dance step from someone in your year.
You took a group photo that everyone actually liked.
You helped collect cups at the end of the evening.
Your carefully planned hairstyle survived the entire dance.
You laughed when everyone forgot the same dance move.
You and your friends shared your favourite moments on the way home.
You found a quiet seat when you needed a break.
You complimented a classmate's handmade accessory.
You discovered a shared favourite band with someone new.
You spent the final song dancing with your friends.
You helped pick up a decoration that had fallen down.
You joined a dance circle after watching from the side.
You enjoyed the lighting more than the loudest song.
Your class turned a familiar chorus into a group singalong.
You found your friends after a brief mix-up near the entrance.
You politely declined a dance and carried on enjoying the evening.
You noticed how much work the organisers had put into the room.
You helped a friend find the coat they had misplaced.
You managed to dance without spilling your drink.
You laughed at your own awkward first few steps.
You and your friends took turns choosing silly photo poses.
You enjoyed hearing a song you had not heard in years.
You thanked a volunteer who helped run the evening.
You moved away from the speakers to protect your ears.
You discovered that the refreshments table was the best meeting spot.
You stayed for one more song before heading home.
You helped make room for someone joining the group.
You compared favourite songs with classmates during a break.
You made a happy memory without needing to be the centre of attention.
You left tired from dancing and glad that you had gone.''')
for i,s in enumerate(DANCE_FEEDBACK):
    add('a16_backtoschool-school-dance-event-feedback-enc',{'String':s,'Hero Enjoyment Score':str(2+i%3),'NPC Enjoyment Score (if applicable)':'3'})

PARTIES=lines('''visit a community art fair
try a new board game together
watch a local outdoor film
explore a public sculpture trail
attend a daytime music workshop
have a relaxed picnic
visit a weekend craft market
share favourite playlists over lunch
try a beginner pottery session
watch a local theatre rehearsal
take photos on a walking trail
attend a bookshop reading
visit a small design exhibition
play cooperative puzzle games
help at a community garden day
try a casual drawing challenge
attend a local history talk
watch a community talent showcase
make a shared scrapbook
try a beginner dance workshop
visit a science discovery exhibition
attend a free lunchtime concert
have a friendly trivia evening
visit a second-hand book sale
try a short creative writing challenge
learn a simple song together
attend a neighbourhood food fair
visit a public botanical garden
help at a charity collection event
watch a favourite film at home''')
for action in PARTIES:
    add('a16_friend-party-scenarios-enc',{'Inbound Scenario':'<friend> has invited you to '+action+'.',
      'Outbound Scenario':'You joined <friend> to '+action+'.','Log Version':'I joined <friend> to '+action+'.',
      'Hero Min Age':'13','Friend Min Age':'13','Enjoyment Score':'4'})
ADVICE=lines('''balancing study with a new hobby
feeling left out of a group chat
preparing for a class presentation
setting boundaries around borrowed belongings
handling criticism of a creative project
reconnecting with an old friend
choosing between two clubs
making a realistic revision schedule
giving helpful feedback without sounding harsh
dealing with a forgotten birthday
trying a hobby for the first time
staying patient while learning a difficult skill
asking for credit on a group project
keeping online messages from taking over the evening
supporting a friend after disappointment
responding to an awkward misunderstanding
organising a small community event
deciding what to include in a creative portfolio
coping with comparisons to more successful people
making time for rest during a busy week
welcoming someone new to a group
preparing questions for a mentor
turning a vague goal into manageable steps
keeping a shared playlist fair
asking for clearer instructions
politely declining an invitation
handling nerves before a performance
finding motivation after a setback
sharing praise fairly with teammates
reflecting on a recent personal milestone''')
for topic in ADVICE:
    add('a16_friend-advice-enc',{'Scenario':'<friend> asks for your advice about '+topic+'.',
      'Log Version':'<friend> asked me for advice about '+topic+'.','Hero Min Age':'13','Friend Min Age':'13'})
ANNOY=lines('''reads every work message aloud
keeps interrupting your concentration with unrelated stories
leaves shared supplies in the wrong cupboard
talks over everyone during short meetings
plays the same notification sound repeatedly
uses the shared printer without checking the queue
leaves half-finished drafts in the final-work folder
changes a shared document without explaining why
asks questions already answered in the task brief
turns every small task into an emergency
forgets to return borrowed stationery
books meetings over everyone's lunch break
leaves unclear notes on shared tasks
repeats a joke long after everyone stopped laughing
keeps moving the breakroom chairs
announces every tiny achievement as breaking news
forwards long email chains with no explanation
starts a new group chat for every question
forgets which version of a document is current
speaks so quietly that you keep asking them to repeat things
uses confusing abbreviations in every message
changes meeting topics without finishing the first one
leaves snack wrappers beside the shared keyboard
insists on explaining a tool you already know
asks for instant replies to non-urgent messages
keeps rearranging the shared resource shelf
uses all the sticky notes for elaborate desk art
repeats instructions while you are following them
opens too many noisy browser tabs near you
turns routine updates into long speeches
leaves the team calendar full of vague entries
keeps forgetting to attach the files they mention
uses the reply-all button for private questions
starts conversations just as you are finishing a deadline
labels every folder with nearly identical names
reads motivational slogans during quiet work time
changes the room temperature without asking anyone
leaves empty containers in the breakroom fridge
sends voice messages for one-word answers
keeps asking whether it is Friday yet''')
for action in ANNOY:
    add('a16_coworker-annoy-scenarios-enc',{'Scenario':'At work, <coworker> '+action+'.',
      'Log Version':'<coworker> '+action.replace('your','my').replace('you','me')+'.'})

assert sum(map(len,CONTENT.values()))==600, {k:len(v) for k,v in CONTENT.items()}
(ROOT/'life_content.json').write_text(json.dumps(CONTENT,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:len(v) for k,v in CONTENT.items()},indent=2))
