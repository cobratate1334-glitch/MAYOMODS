"""Author table-driven Community+ content against the extracted current schemas.

The expansion deliberately uses existing menus, eligibility checks and impacts.
It does not invent new save fields or pretend to implement full racing/TV engines.
"""
import argparse, collections, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def author(tables):
    content=collections.defaultdict(list)
    def name(key): return 'a16_'+key+'-enc'
    def add(key, **values):
        target=name(key); row=dict.fromkeys(tables[target][0],'')
        assert set(values)<=set(row),(target,set(values)-set(row))
        row.update(values); content[target].append(row); return row
    def clone(key, original, **values):
        row=dict(zip(tables[name(key)][0],original));row.update(values)
        content[name(key)].append(row);return row
    def values(key, field):return {r[tables[name(key)][0].index(field)] for r in tables[name(key)][1:]}
    index=930000
    def next_id():
        nonlocal index
        index+=1;return str(index)

    # Real post-menu entries; platform eligibility and video/appeal are native fields.
    posts=[
      ('studio tour','showed viewers around your recording space',1),
      ('song breakdown','explained how you built a song from its first melody',1),
      ('beat challenge','built a beat using only everyday household sounds',1),
      ('mix comparison','compared an unfinished mix with your final version',1),
      ('songwriting diary','shared the story behind your latest lyrics',0),
      ('acoustic session','performed a stripped-back acoustic session',1),
      ('production tutorial','demonstrated how you layered a drum pattern',1),
      ('release countdown','shared a countdown to a new music release',0),
      ('fan questions','answered questions sent in by your followers',1),
      ('collaboration preview','shared a preview of a creative collaboration',1),
      ('study vlog','recorded a realistic afternoon of studying',1),
      ('revision tips','shared the study habits that helped you prepare',0),
      ('school project','showed a project you made for a class',1),
      ('club showcase','shared highlights from a community club showcase',1),
      ('career diary','described what you learned from a difficult working day',0),
      ('portfolio review','walked viewers through your creative portfolio',1),
      ('desk setup','showed how you arranged your workspace on a budget',1),
      ('budget diary','shared a week of small spending decisions',0),
      ('luxury review','reviewed the comfort of a luxury vehicle',1),
      ('charity livestream','streamed a community fundraiser',1),
      ('race analysis','discussed the strategy behind a fictional motor race',1),
      ('sports analysis','broke down the turning point in a sporting match',1),
      ('fitness progress','shared a measured update on your fitness routine',1),
      ('reality TV recap','discussed the editing choices in a reality show',1),
      ('behind the scenes','shared the preparation behind a creative project',1),
      ('digital art timelapse','recorded the creation of a digital illustration',1),
      ('community spotlight','introduced a small creator whose work you admire',0),
      ('fact check','explained how you checked a surprising online claim',0),
      ('cooking budget','made a simple meal with inexpensive ingredients',1),
      ('quiet livestream','hosted a calm stream with time for audience questions',1)]
    for i,(title,action,video) in enumerate(posts):
        row=add('social-media-post-types',**{'Post Type':title,'Scenario':f'You {action} on <channel>.',
          'Log Version':f'I {action.replace("your ","my ").replace("you ","I ")} on <channel>.',
          'Add Video':'x' if video else '', 'Appeal Score':str(2+i%3),'Impacted by Smarts':'x',
          'Viral Score':str(1+i%3),'Facebook':'x','Instagram':'x','TikTok':'x' if video else '',
          'Twitter':'x','YouTube':'x' if video else '', 'Twitch':'x' if video else ''})
    collabs=['building a song from audience suggestions','swapping unfinished beats','reviewing each other\'s portfolios',
      'writing a chorus in ten minutes','turning a phone recording into a melody','making a community playlist',
      'drawing each other\'s album artwork','hosting a charity quiz','comparing affordable studio equipment',
      'teaching each other a new instrument','sharing honest study tips','creating a fictional race strategy',
      'discussing sports recovery routines','recapping a fictional reality show','designing a student magazine',
      'visiting a local art exhibition','cooking with leftover ingredients','testing accessibility features',
      'answering questions from small creators','showcasing independent musicians']
    for i,s in enumerate(collabs):add('social-media-channels-of-collabstrings',**{'String':s,'Engagement Score':str(1+i%3),
      'Virality':str(i%2),'Controversy Score':'0','Commonness Score':'3'})
    products=['studio headphones','audio interfaces','portable keyboards','recording microphones','independent music distributors',
      'practice notebooks','digital art tablets','portfolio hosting services','study planners','language learning cards',
      'reusable lunch containers','desk lamps','running journals','recovery cushions','creator camera mounts',
      'captioning tools','music lesson vouchers','travel organizers','community event tickets','recycled stationery']
    for i,p in enumerate(products):add('social-media-promotion-products',**{'Product':p,'Description':'a brand of '+p,
      'Compensation Score':str(2+i%3),'Min Age':'18','Appeal Score':str(1+i%3)})
    remarks=['your drums sound like a washing machine','your studio has more cables than songs','your countdown needs its own countdown',
      'your desk setup looks like a spaceship','your budget diary skipped the snacks','your tutorial needs a tutorial',
      'your race predictions belong in a comedy show','your acoustic cover is mostly chair noises',
      'your livestream has too many loading screens','your playlist has identity issues']
    for s in remarks:
        add('social-media-troll-inbounds',**{'Scenario':f'<username> commented that {s} on <channel>.',
          'Log Version':f'<username> joked that {s.replace("your ","my ")} on <channel>.'})
    replies=['said the editing had more cuts than a salad','joked that the intro was longer than the whole topic',
      'asked whether the microphone was recording from another room','joked that the thumbnail deserved a plot summary',
      'said the countdown had become a full-time occupation','joked that the background music was the main character',
      'asked whether the sponsor had written the punchline','joked that the lighting needed a rehearsal',
      'said the captions were racing the speaker','joked that the chair had the best cameo']
    for s in replies:add('social-media-troll-outbounds',**{'Scenario':f'You {s} on <victim-possessive> <channel> post.',
      'Log Version':f'I {s} on <victim-possessive> <channel> post.'})

    # New producer/release decisions have distinct outcomes through existing fields.
    producer_cases=[
      ('Missing Stems','The vocalist sends a final recording without the separate backing tracks.', 'Request the missing tracks','Rebuild a simpler arrangement','Delay the session openly','Pretend the files arrived'),
      ('Credit Check','Two collaborators disagree over how their names should appear in the credits.','Review the session notes','Arrange a joint discussion','Pause until they agree','Credit only yourself'),
      ('The Quiet Mix','A client says your quieter mix sounds weak beside a heavily limited reference.','Explain the listening tradeoff','Prepare two balanced versions','Request another reference','Crush every sound'),
      ('Playback Test','The bass overwhelms the vocals when the mix is played on a small speaker.','Check several playback devices','Make a restrained bass adjustment','Ask for a second opinion','Ignore the test'),
      ('Session Backup','A collaborator asks how the current session files are being backed up.','Verify a second copy','Export important stems','Write a backup checklist','Say it is probably fine'),
      ('Release Window','The planned release clashes with a major local event.','Discuss a better release date','Keep the date with a clear plan','Ask the artist to decide','Change the date without asking'),
      ('Budget Session','A new artist has a small budget and a very ambitious arrangement.','Agree on a realistic scope','Build a focused demo first','Offer a shorter session','Promise unlimited revisions'),
      ('Sample Permission','The source of a proposed sample is unclear.','Ask for permission evidence','Replace it with an original part','Hold the sample out for now','Use it without checking'),
      ('Revision Spiral','Each revision request reverses something approved in the previous mix.','Agree on a revision checklist','Review the changes together','Archive both versions','Delete the earlier versions'),
      ('Remote Session','A remote recording arrives with distracting room noise.','Request a cleaner recording','Edit the quiet sections carefully','Use a restrained arrangement','Bury it under more noise'),
      ('Newcomer Confidence','A first-time vocalist loses confidence after hearing a rough take.','Explain what the rough take is for','Highlight a strong phrase','Take a short break','Mock the performance'),
      ('Studio Schedule','Two sessions have been booked for the same afternoon.','Tell both clients immediately','Offer a workable new schedule','Ask a colleague for help','Hope nobody notices'),
      ('Artist Direction','The artist wants a raw sound while the reference is extremely polished.','Discuss the intended character','Make a short comparison demo','Ask which elements matter most','Follow the reference blindly'),
      ('Headphone Bleed','The vocal microphone picked up the headphone backing track.','Adjust monitoring and record again','Repair the clearest take','Change the headphone level','Call the noise artistic'),
      ('Accessibility Notes','A promotional clip has no captions for spoken sections.','Prepare accurate captions','Ask the team to review captions','Simplify the spoken clip','Dismiss the request'),
      ('Last Minute Guest','A guest performer arrives after the arrangement was finalized.','Plan a clear space for the guest','Record a short alternate section','Arrange another session','Crowd every part together'),
      ('Reference Trap','The client asks for a song that sounds exactly like a current hit.','Discuss an original direction','Borrow only a broad mood','Try a contrasting demo','Copy the hook'),
      ('Studio Boundaries','A client sends revision requests throughout the night.','Agree on working hours','Schedule a review call','Reply during the next session','Send an angry public post'),
      ('Artist Handoff','Another producer will finish a project you started.','Send organized stems and notes','Prepare a clear handoff checklist','Explain the unfinished sections','Hide the useful files'),
      ('Release Metadata','The song title is spelled differently across the release paperwork.','Verify the agreed title','Check all release forms together','Ask the artist to confirm','Submit inconsistent forms'),
      ('Session Etiquette','A visitor interrupts every take with unsolicited opinions.','Set a polite session boundary','Ask for feedback between takes','Suggest a quieter waiting area','Join the interruptions'),
      ('Live Arrangement','The studio arrangement is too crowded for a small live band.','Build a playable live version','Identify the essential parts','Rehearse a simpler ending','Demand the impossible'),
      ('Competing Feedback','The artist likes the chorus, but the manager wants it rebuilt.','Compare feedback with the artist','Prepare a small alternate chorus','Clarify who approves the mix','Change it behind their backs'),
      ('Ear Fatigue','After a long day, every mix seems to need more treble.','Return with rested ears','Check a trusted reference quietly','Take a scheduled break','Keep boosting the treble'),
      ('Producer Portfolio','A client asks to hear examples of your finished work.','Share approved portfolio tracks','Explain your contribution honestly','Ask past clients for permission','Claim somebody else\'s work'),
      ('Intern Session','A studio intern asks to help with a simple recording task.','Explain the task and supervise','Give a useful checklist','Offer a short demonstration','Leave everything unexplained'),
      ('File Names','Several final mixes share the same vague filename.','Rename and version the mixes','Create an approved export folder','Confirm the correct version','Send a random file'),
      ('Clean Version','The release team needs a clean version for a daytime broadcast.','Prepare a careful alternate edit','Ask the artist to approve it','Check the broadcast requirements','Send the explicit version anyway'),
      ('Artwork Brief','The cover artist has misunderstood the mood of the record.','Write a clear visual brief','Discuss the song with the designer','Offer useful reference notes','Insult the draft'),
      ('Creative Credit','A session musician proposes the strongest new melody.','Discuss a fair credit','Record their contribution clearly','Ask the artist to review credits','Take sole credit'),
      ('Premiere Invitation','A local creator offers to premiere the finished track.','Check the audience and agreement','Arrange a short introduction','Ask the artist for approval','Promise exclusive rights casually'),
      ('Slow Upload','A file transfer is taking longer than the client expected.','Give a realistic delivery update','Send a smaller review copy','Offer a verified alternate transfer','Pretend delivery is complete'),
      ('The Wrong Tempo','A collaborator recorded a part against an outdated tempo guide.','Send the correct guide','Try a careful alignment','Arrange a new take','Blame the collaborator publicly'),
      ('Room Booking','The booked recording room becomes unavailable.','Discuss a suitable replacement','Rework the session schedule','Explain the delay honestly','Hide the change until arrival'),
      ('Festival Demo','An artist wants a demo ready for a festival application.','Prioritize a strong concise demo','Review the application requirements','Set a realistic timeline','Promise a finished album overnight'),
      ('Listener Notes','Test listeners keep missing the central lyric.','Improve the vocal clarity','Simplify the busiest passage','Compare two restrained versions','Add more competing layers'),
      ('Archive Request','A former client asks for the stems from an old project.','Check the archive and agreement','Organize the available exports','Explain what remains available','Send unrelated files'),
      ('Rehearsal Recording','A rehearsal take has more energy than the studio take.','Compare both with the artist','Preserve the strongest performance','Use the rehearsal as a guide','Erase it without listening'),
      ('Charity Project','A community group asks you to produce a short charity theme.','Agree on a clear scope','Build a simple memorable arrangement','Ask about approvals and credits','Use it to advertise only yourself'),
      ('Honest Promotion','A promoter suggests describing the release as a guaranteed hit.','Use accurate promotional language','Highlight the actual strengths','Let the music speak in a preview','Make the guarantee')]
    for title,body,*choices in producer_cases:
        row=add('music-producer-dumb-scenario',**{'Index':next_id(),'Hero Min Age':'18','Randomize Choices':'x',
          'Title':'Producer+: '+title,'Body':body,'CTA':'How will you handle it?'})
        for i,(choice,impact) in enumerate(zip(choices,[3,2,1,-3]),1):
            row[f'Choice {i}']=choice;row[f'Narrative {i}']=f'I chose to {choice[0].lower()+choice[1:]} during the {title.lower()} situation.';row[f'Reputation Impact {i}']=str(impact)
    release_cases=[
      ('First Upload','Your first independent track is ready, but its introduction takes a long time to reach the main idea.','Create a tighter opening','Keep a short atmospheric intro','Ask listeners for a comparison','Add another minute of silence'),
      ('Cover Contrast','The cover artwork becomes hard to read on a small screen.','Test a clear small-screen version','Simplify the lettering','Ask the designer for alternatives','Shrink every detail further'),
      ('Vocal Space','A new synth layer is masking the lead vocal.','Make room for the vocal','Lower the new layer','Compare the chorus without it','Turn up both parts'),
      ('Upload Quality','The preview file sounds noticeably rougher than the export.','Check the export settings','Compare a verified new export','Listen on another device','Upload the rough preview'),
      ('Release Description','You need a short description for a self-released track.','Tell the real story behind it','Describe its strongest musical idea','Keep the description concise','Claim millions of imaginary fans'),
      ('One More Chorus','You are deciding whether the last chorus needs another repeat.','Choose the strongest ending','Try a shorter final chorus','Ask for focused feedback','Repeat it six more times'),
      ('Listening Party','Friends offer to listen to the independent release before upload.','Ask for specific listening notes','Play two short versions','Focus on recurring feedback','Argue with every comment'),
      ('Track Names','Your title is easily confused with another track in your catalogue.','Choose a distinct title','Clarify the version name','Review the release details','Give every track the same title'),
      ('Stereo Test','A wide effect makes the main melody disappear in mono.','Check mono playback','Narrow the effect carefully','Use a simpler effect','Ignore the missing melody'),
      ('Click at the End','There is a short click at the end of the exported track.','Repair the final fade','Export and check again','Compare with the session','Tell listeners it is a feature'),
      ('Feedback Flood','The preview attracts contradictory suggestions.','Look for a recurring issue','Protect the central idea','Test one focused revision','Try every suggestion at once'),
      ('Artwork Credit','The artist who drew your cover asks for a credit in the description.','Add the agreed credit','Check the wording together','Confirm permission and credit','Remove their name'),
      ('Demo Hype','A teaser promises a very different sound from the finished track.','Use an honest new teaser','Explain the finished direction','Share a representative excerpt','Keep the misleading teaser'),
      ('Small Speaker','The track loses its rhythm on a small speaker.','Check the important midrange parts','Simplify the lowest layers','Test a modest revision','Only listen on huge speakers'),
      ('Listener Fatigue','Your intro, verse and chorus all use the same dense texture.','Create a useful contrast','Remove a layer from the verse','Try a simpler transition','Add layers everywhere'),
      ('Quiet Detail','A subtle melody is disappearing beneath the percussion.','Find space in the arrangement','Adjust the percussion gently','Compare a clearer mix','Boost everything at once'),
      ('Independent Identity','A friend suggests copying a popular creator\'s exact signature sound.','Develop your own recognizable detail','Experiment with a new texture','Keep a familiar but original mood','Copy their whole sound'),
      ('Release Preview','You are selecting the excerpt that introduces the upload.','Choose a representative hook','Use a strong short transition','Check the excerpt on a phone','Use the weakest passage'),
      ('Old Version','An early draft was accidentally selected for upload.','Replace it before release','Verify the approved export','Check the filename and duration','Release it without checking'),
      ('Noise Floor','A quiet passage exposes unwanted background noise.','Clean the affected recording','Use a careful fade','Try a less exposed arrangement','Amplify the noise'),
      ('Drum Balance','The drums overwhelm the emotional section of the song.','Shape a more restrained rhythm','Lower the busiest hits','Try an alternate drum pattern','Add more fills'),
      ('Different Mood','The artwork and description suggest a cheerful song, but the track is reflective.','Align the presentation with the music','Rewrite the description honestly','Ask for a more suitable cover','Advertise it as a party anthem'),
      ('Listener Invitation','You want new listeners to hear the independent release.','Share a useful short preview','Explain the song in a personal post','Invite constructive feedback','Spam unrelated conversations'),
      ('Intro Promise','The opening implies a dramatic drop that never arrives.','Create a satisfying transition','Revise the opening expectation','Test a more honest intro','Make the opening even bigger'),
      ('Acoustic Detail','A live instrument adds warmth but drifts from the rhythm.','Edit the timing gently','Record another focused take','Use its strongest phrase','Ignore the clashing rhythm'),
      ('Too Many Tags','You are choosing the genre tags for your independent release.','Use accurate tags','Choose the closest main genre','Check comparable original tracks','Select every tag available'),
      ('Return Listen','After a break, you notice the chorus loses energy.','Strengthen the main musical idea','Compare the chorus arrangement','Ask for a focused listening note','Make every section louder'),
      ('Creative Risk','An unusual bridge gives the song character but may surprise listeners.','Shape a clear return to the chorus','Keep a shorter version of the bridge','Try a restrained alternative','Make the bridge obscure everything'),
      ('Final Checklist','The release is ready for a last quality review.','Check audio and metadata together','Listen through the final export','Confirm the artwork and title','Skip every check'),
      ('Version Notes','You plan to upload an alternate version of an older song.','Name the alternate version clearly','Explain what changed','Keep the original available','Replace it with no explanation'),
      ('Meaningful Ending','The song ends abruptly before its main phrase resolves.','Create a deliberate ending','Try a short outro','Compare two final edits','Cut it in the middle of a word'),
      ('Creator Collaboration','A small creator wants to feature your independent track.','Agree on clear credits','Offer an approved preview','Check the proposed use','Demand exaggerated claims')]
    for title,body,*choices in release_cases:
        row=add('music-soundcloud-dumb-scenario',**{'Index':next_id(),'Hero Min Age':'18','Randomize Choices':'x',
          'Title':'Independent+: '+title,'Body':body,'CTA':'What will you do?'})
        for i,(choice,impact) in enumerate(zip(choices,[3,2,1,-3]),1):
            row[f'Choice {i}']=choice;row[f'Narrative {i}']=f'I chose to {choice[0].lower()+choice[1:]} for my independent release.';row[f'Reception Impact {i}']=str(impact)
    beats=['Half-time pocket','Loose brushed groove','Broken garage rhythm','Soft handclap pulse','Swinging boom-bap','Gentle triplet shuffle',
      'Minimal four-on-the-floor','Syncopated rimshot pattern','Double-time breakbeat','Sparse kick-and-snare','Rolling percussion bed','Warm live drum loop',
      'Offbeat shaker groove','Slow cinematic pulse','Dusty sampled rhythm','Punchy festival rhythm','Acoustic stomp pattern','Floating ambient pulse']
    vibes=['Midnight City Lights','Quiet Train Home','First Day Energy','Rain on the Windows','Small Room Big Dreams','After the Last Show',
      'Warm Summer Pavement','Letters Never Sent','Early Morning Confidence','End Credits Glow','Home Studio Hope','Underground Discovery',
      'Soft Focus Memory','Open Road Optimism','Library After Hours','The Long Way Back','Fresh Start Feeling','Neon Rooftop']
    for key,field,items in [('music-track-beat','Beat',beats),('music-track-vibe','Vibe',vibes)]:
        genre=', '.join(sorted({g.strip() for v in values(key,'Genre') for g in v.split(',') if g.strip()}))
        for s in items:add(key,**{field:s,'Genre':genre,'Commonness Score':'3'})
    sounds=['pencil tapping a mug','a soft door chime','pages turning in a notebook','a cassette latch clicking','a wooden desk knock',
      'a distant train bell','a spoon circling a glass','a short camera shutter','an elevator arrival chime','a folded paper snap',
      'rain tapping a studio window','a zipper sliding shut']
    for i,s in enumerate(sounds):add('music-signature-sound',**{'Sound':s,'Reception Impact Score':str(1+i%3),'Commonness Score':'3'})
    instruments=['electric kalimba','baritone guitar','upright felt piano','muted electric bass','glass harmonica','prepared acoustic guitar',
      'melodica ensemble','bowed vibraphone','hand percussion set','soft reed organ','plucked cello','analog string synthesizer']
    base=tables[name('music-soundcloud-track-instrument')][1]
    for s in instruments:clone('music-soundcloud-track-instrument',base,Instrument=s,**{'Commonness Score':'3'})
    projects=['Letters from the Moon','The Last Train North','A City Without Clocks','Tomorrow\'s Echo','Summer at Platform Nine',
      'The Borrowed Horizon','After the Lighthouse','An Ordinary Miracle','The Hidden Orchestra','The Longest Rehearsal',
      'Windows Facing East','The Map of Small Things']
    for s in projects:add('music-score-production-project-title',Name=s,**{'Project Type':'film','Commonness Score':'3'})
    comments=['That little melody stayed with me all afternoon.','The drums leave just enough room for the voice.',
      'This sounds like the walk home after a great night.','The quieter version has so much character.',
      'I found this through a tiny playlist and stayed for the chorus.','The ending makes me want to start it again.',
      'The artwork fits the mood perfectly.','That transition caught me by surprise in a good way.',
      'A small release with a really clear identity.','The live instrument gives this warmth.',
      'I can hear the care in the arrangement.','That bass line deserves headphones.',
      'The mix is clear without losing the rough edges.','I like that the intro gets straight to the idea.',
      'This would be lovely in a short film.','The hook works even on my old speaker.',
      'Please share how you built that unusual texture.','The second verse feels like a new room opening.',
      'This is why I follow independent creators.','The alternate version makes the lyrics shine.',
      'Your sound is becoming easier to recognize.','That bridge made the final chorus land.',
      'The understated percussion is my favourite detail.','I sent this to a friend who makes music.']
    for s in comments:add('music-soundcloud-comment',**{'String':s,'Log Version':'A listener wrote: '+s})

    # New occupations retain known employer/qualification categories.
    careerdefs=[('Reality TV Producer','Podcast Producer',48000,160000),('Race Engineer','Mechanical Engineer',62000,185000),
      ('Sports Physiotherapist','Physical Therapist',57000,125000),('Luxury Asset Manager','Financial Advisor',60000,200000),
      ('Community Moderator','Community Manager',31000,90000),('Independent Music Promoter','Music Rights Coordinator',36000,135000)]
    ch=tables[name('careers')][0]
    for title,template,salary,cap in careerdefs:
        base=next(r for r in tables[name('careers')][1:] if r[0]==template)
        clone('careers',base,Career=title,**{'Seniority Track':f'Assistant {title}, {title}, Senior {title}',
          'Can Skip Positions':'0','Seniority Track Years':'12','Starting Salary':f'${salary:,.2f}',
          'Salary Cap':f'${cap:,.2f}','Min Age':'18','Commonness Score':'3','Holiday':'','Unavailable':''})
    # Four distinct work problems per occupation, not empty pools for custom careers.
    contexts={
      'Game Designer':('a confusing tutorial','an overcomplicated level','a player accessibility request','an untested mechanic'),
      'Game Quality Analyst':('a reproducible loading bug','an incomplete test report','a rare controller failure','a regression after a patch'),
      'Cybersecurity Analyst':('a suspicious login alert','an outdated access list','an unverified security report','a missing incident note'),
      'Cloud Systems Engineer':('a failed deployment check','an expensive idle service','an incomplete backup plan','a confusing monitoring alert'),
      'Data Analyst':('an inconsistent spreadsheet','a misleading chart scale','a missing survey response','an unsupported conclusion'),
      'User Experience Designer':('an unclear navigation label','a difficult checkout step','a small-screen layout problem','an accessibility review'),
      'Digital Illustrator':('an unclear artwork brief','a mismatched colour palette','a forgotten contributor credit','a last-minute print change'),
      'Motion Graphics Designer':('an unreadable animated title','a rushed transition','a missing source asset','an export with the wrong dimensions'),
      'Accessibility Specialist':('an unlabelled form control','an inaccurate video caption','an inaccessible document','a confusing keyboard path'),
      'Technical Writer':('an outdated installation guide','an ambiguous warning','a missing procedure step','a contradictory reference page'),
      'Copy Editor':('an inconsistent character name','an unclear quotation source','a repeated paragraph','a rushed headline change'),
      'Content Strategist':('an unclear audience brief','a stale publishing schedule','a misleading campaign claim','an unreviewed content update'),
      'Community Manager':('an escalating community argument','an unclear moderation rule','a neglected member question','a misleading announcement'),
      'Event Coordinator':('a double-booked meeting room','an inaccessible event entrance','a delayed supplier delivery','an unclear attendee schedule'),
      'Sustainability Coordinator':('an incomplete waste audit','an unsupported environmental claim','an overlooked reuse option','an unclear energy report'),
      'Research Coordinator':('an incomplete participant schedule','an inconsistent research record','a delayed consent form','an unclear study handoff'),
      'Museum Educator':('an overlong exhibit talk','an inaccessible activity sheet','a confused visiting school group','an inaccurate display explanation'),
      'Archive Technician':('a mislabelled collection box','an incomplete digitization record','a damaged storage sleeve','an uncertain document date'),
      'Literacy Coordinator':('a learner who has lost confidence','an unsuitable reading exercise','an unclear volunteer timetable','a missing progress note'),
      'Learning Support Officer':('an inaccessible lesson resource','a confusing support plan','a student reluctant to ask for help','an overlooked classroom adjustment'),
      'Education Programme Coordinator':('a duplicated course session','an unclear learning objective','a delayed tutor handoff','a poorly explained enrolment change'),
      'Student Services Officer':('a student with conflicting appointments','an unclear application checklist','a missed support referral','an outdated information page'),
      'Library Programme Coordinator':('an overbooked reading workshop','an inaccessible event notice','a missing activity resource','a confusing room schedule'),
      'Audio Editor':('a noisy interview recording','a poorly matched voice level','a cut that changes a speaker\'s meaning','an incorrectly named export'),
      'Podcast Producer':('an unprepared guest interview','an unclear sponsor message','a missing episode credit','an overlong episode introduction'),
      'Music Rights Coordinator':('an incomplete credit sheet','an unclear sample permission','a conflicting contributor name','an unsigned usage request'),
      'Live Sound Technician':('a noisy stage monitor','an incomplete input list','a failed soundcheck handoff','a crowded vocal mix'),
      'Lighting Technician':('an unreadable lighting cue','a last-minute stage layout change','a distracting spotlight position','a missing rehearsal note'),
      'Production Coordinator':('a conflicting rehearsal schedule','an incomplete equipment list','a delayed location confirmation','an unclear crew handoff'),
      'Location Coordinator':('an uncertain filming permission','an inaccessible site entrance','a conflicting venue booking','a missing location contact'),
      'Brand Designer':('an unreadable small logo','an inconsistent colour specification','an unclear design brief','a missing usage guideline'),
      'Market Research Analyst':('a leading survey question','an unrepresentative sample','an unexplained market estimate','a conflicting response category'),
      'Customer Experience Analyst':('a recurring customer complaint','an unclear support handoff','a confusing return instruction','an overlooked feedback trend'),
      'Operations Coordinator':('a duplicated work order','an unclear shift handoff','a missing delivery confirmation','an inefficient weekly schedule'),
      'Quality Assurance Coordinator':('an incomplete inspection note','an inconsistent quality checklist','a repeated supplier defect','an unresolved corrective action'),
      'Recruitment Coordinator':('an unclear interview schedule','an inaccessible application form','an incomplete candidate update','a misleading role description'),
      'Training Coordinator':('an outdated training example','a rushed practical exercise','an unclear assessment criterion','a missing learner feedback form'),
      'Logistics Planner':('a conflicting delivery window','an inefficient route plan','an unclear shipment handoff','an incomplete inventory forecast'),
      'Digital Archivist':('an uncertain file provenance','a duplicate archive identifier','an incomplete preservation copy','an outdated catalogue link'),
      'Exhibition Coordinator':('an incomplete display label','a delayed artwork delivery','an unclear installation timetable','an inaccessible exhibition route'),
      'Reality TV Producer':('an edit that misrepresents a contestant','an unclear participant agreement','a rushed episode storyline','an unverified on-screen claim'),
      'Race Engineer':('an inconsistent telemetry reading','an unclear driver feedback note','a rushed setup comparison','an incomplete simulation report'),
      'Sports Physiotherapist':('an incomplete rehabilitation note','an athlete rushing their recovery','an unclear exercise handoff','a missed progress review'),
      'Luxury Asset Manager':('an unclear maintenance estimate','an incomplete collection valuation','a questionable luxury purchase claim','an overlooked ownership cost'),
      'Community Moderator':('an ambiguous rule violation','an escalating thread dispute','an incomplete appeal record','an inconsistent moderation decision'),
      'Independent Music Promoter':('an unrealistic release promise','an uncredited creator collaboration','an unsuitable playlist pitch','an unclear promotional budget')}
    effects=[(2,2,0,1,0,3),(1,1,1,1,0,2),(0,1,-1,0,0,1),(-2,-2,1,0,0,-3)]
    for career,problems in contexts.items():
        for k,problem in enumerate(problems):
            row=add('dumb-scenarios-career',**{'Index':next_id(),'Type':career,'Randomize Choices':'x',
              'Title':f'Work+: {career} - '+['Quality Check','Clear Communication','Taking Responsibility','Final Review'][k],
              'Body':f'While working as a {career.lower()}, you encounter {problem}. The next decision could affect how your work is judged.',
              'CTA':'How will you handle it?'})
            choices=[('Review the evidence and fix it','I reviewed the evidence and corrected '+problem+'.'),
              ('Discuss a practical solution','I discussed a practical solution to '+problem+'.'),
              ('Ask for a supervised review','I requested a supervised review of '+problem+'.'),
              ('Hide the problem','I hid '+problem+' instead of dealing with it.')]
            for i,((choice,log),impact) in enumerate(zip(choices,effects),1):
                row[f'Choice {i}']=choice;row[f'Narrative {i}']=log
                for f,v in zip(['Karma','Discipline','Happiness','Intelligence','Appearance','Job'],impact):row[f'{f} Impact {i}']=str(v)
    pranks=['covered a desk with removable paper stars','gave a stapler its own tiny name badge','left a paper crown on a chair',
      'relabelled a snack drawer as mission control','made a tiny cardboard office for a mug','left a fake meeting invitation for a houseplant',
      'added a paper moustache to a desk calendar','created a mock award for punctual tea breaks','left a toy microphone beside a keyboard',
      'made a miniature queue sign for a coffee cup','put a paper cape on a desk fan','left a tiny thank-you note from the printer',
      'gave a notebook a mock book-review sticker','made a paper red carpet leading to a desk','placed a cardboard VIP sign beside a chair',
      'left a tiny cardboard trophy beside a mouse']
    for s in pranks:add('coworker-pranks',**{'Inbound Scenario':f'<coworker> {s} near your workspace.',
      'Inbound Log Version':f'<coworker> {s} near my workspace.','Outbound Snippet':s+' near <coworker-possessive> workspace'})
    behaviors=['takes credit for a shared idea','interrupts your explanation during a meeting','forwards your unfinished notes without asking',
      'uses the shared workspace without tidying up','changes a deadline without telling you','keeps adding tasks after a handoff',
      'repeatedly forgets to include you in updates','dismisses a useful accessibility suggestion','books a meeting during your agreed break',
      'posts an unapproved team announcement','leaves vague comments on your completed work','skips the agreed review checklist',
      'borrows your stationery without returning it','talks loudly during a quiet work session','copies an old estimate into a new report',
      'complains about a process without reading the instructions']
    for s in behaviors:add('coworker-behavior-scenarios',**{'Scenario':f'<coworker> {s}.','Log Version':f'<coworker> {s}.'})

    # School clubs appear through the existing activities list, with the same rules.
    clubs=['School Podcast Club','Student Radio Workshop','Independent Music Club','Beatmaking Club','Sound Engineering Club',
      'Film Score Club','Student Documentary Club','Digital Magazine Club','Accessibility Design Club','Community Service Lab',
      'Motorsport Engineering Club','Sports Analytics Club','Recovery and Wellbeing Club','Personal Finance Club','Media Literacy Club',
      'Debate Research Club','Student Exhibition Club','Digital Archive Club','Creative Coding Club','Revision Partnership Club']
    clubbase=next(r for r in tables[name('school-activities')][1:] if r[1]=='Art Club')
    for i,s in enumerate(clubs):
        academic=i in (8,10,11,13,14,15,17,18,19)
        community=i in (9,12)
        clone('school-activities',clubbase,**{'Index':next_id(),'Activity':s,'Weekly Hours':'4',
          'Type':'Career Interest' if academic else 'Community' if community else 'Arts',
          'Nerd Activity':'x' if academic else '', 'Arts Activity':'' if academic or community else 'x',
          'Commonness':'3','Min Grades':'','Requires Tryouts':'','Track Performance':''})
    student_problems=[
      ('Revision Partner','A classmate asks to revise together before a difficult assessment.'),
      ('Practice Paper','You finish a practice paper and notice the same mistake in several answers.'),
      ('Group Project','Your group has lots of ideas but nobody has agreed who will do each task.'),
      ('Missed Lesson','You missed a lesson and the next assignment relies on its material.'),
      ('Club Showcase','Your club has been invited to present a small project at a school showcase.'),
      ('Course Choice','You are deciding which optional subject best fits your interests.'),
      ('Quiet Study','Your usual study area is too noisy to concentrate.'),
      ('Student Magazine','A student magazine asks you for a short contribution.'),
      ('Open Day','A visitor at the school open day asks what studying here is really like.'),
      ('Peer Feedback','A classmate offers thoughtful criticism of your presentation.'),
      ('Class Notes','A friend who was absent asks whether you can share your notes.'),
      ('Study Schedule','You have left several assignments until the same weekend.'),
      ('Teacher Questions','You understand most of a topic but one step still confuses you.'),
      ('Library Search','You find two sources that give different explanations for a homework topic.'),
      ('Club Budget','Your club has to choose between a small showcase and a more expensive project.'),
      ('School Podcast','A student podcast needs someone to prepare interview questions.'),
      ('Music Rehearsal','The school music group has not agreed how often to rehearse.'),
      ('Sports Review','Your school team wants to understand why the last match went poorly.'),
      ('Engineering Model','Your engineering club model fails during an early demonstration.'),
      ('Media Literacy','A surprising online story is being shared around your class.'),
      ('Portfolio Selection','You need to choose a few pieces that represent your strongest school work.'),
      ('Presentation Nerves','You are nervous about explaining your project in front of classmates.'),
      ('Volunteer Rota','Your school volunteering group has too many people on one shift.'),
      ('Feedback Meeting','Your teacher offers a short meeting to discuss your progress.')]
    for k,(title,body) in enumerate(student_problems):
        for phase in (0,1):
            row=add('dumb-scenarios-universal',**{'Index':next_id(),'Hero Min Age':'11','Hero Max Age':'25','Student':'x',
              'Randomize Choices':'x','Title':'School+: '+title+(' Follow-up' if phase else ''),
              'Body':body if not phase else 'After a week, you have another chance to improve how you handled this situation: '+body,
              'CTA':'What will you do?'})
            choices=[('Make a clear plan','learn'),('Ask for helpful feedback','speak'),('Take a short break first','rest'),('Put it off again','avoid')]
            if phase:choices=[('Review what worked','focus'),('Help someone else learn','care'),('Try a smaller first step','calm'),('Pretend it is finished','dishonest')]
            write_life_choices(row,choices,title.lower())
    adult_cases=[('Tax Records','You discover that some records for your annual tax return are disorganized.'),
      ('Tax Estimate','Your estimated tax bill is different from what you expected.'),
      ('Donation Receipt','You cannot find the receipt for a donation you want to include in your records.'),
      ('Luxury Running Costs','An impressive luxury purchase has higher running costs than you expected.'),
      ('Collection Insurance','You are reviewing the insurance records for an expensive collection.'),
      ('Maintenance Quote','A maintenance quote for a prized possession needs closer examination.'),
      ('Reality Show Casting','A fictional reality show invites you to submit a short casting video.'),
      ('Sports Community','A local sports group asks you to help organize a community session.'),
      ('Race Club Open Day','A local motorsport club invites you to an engineering open day.'),
      ('Independent Release Plan','A friend wants advice about promoting a self-released song.'),
      ('Creator Collaboration','A small creator asks whether you want to work on a community project.'),
      ('Work Boundaries','Your working week is leaving very little time for the things you enjoy.')]
    for title,body in adult_cases:
        row=add('dumb-scenarios-universal',**{'Index':next_id(),'Hero Min Age':'18','Randomize Choices':'x',
          'Title':'Life+: '+title,'Body':body,'CTA':'What will you do?'})
        write_life_choices(row,[('Check the details carefully','learn'),('Ask for practical advice','speak'),
          ('Set aside time to deal with it','focus'),('Ignore it for now','avoid')],title.lower())
    teacher_actions=['organized your lesson notes','prepared a thoughtful question about the lesson','returned borrowed classroom materials',
      'helped tidy the shared project area','checked a reference before quoting it','offered to help set up a school showcase',
      'thanked the teacher for useful feedback','prepared a concise revision summary','asked for advice about a course choice',
      'helped a classmate find the correct worksheet','brought an interesting library reference','volunteered to distribute project materials',
      'listened carefully during an explanation','prepared a clear project outline','checked that your presentation captions were readable',
      'offered to organize the club timetable','asked how to improve an unclear answer','returned a marked exercise promptly',
      'helped pack away demonstration equipment','shared a useful study resource with the class']
    for s in teacher_actions:add('school-teacher-suckups',**{'Feedback Scenario':f'You {s} for <teacher>.',
      'Log Version':f'I {s.replace("your ","my ")} for <teacher>.','Elementary School':'x','High School':'x','College':'x'})
    school_pranks=['left a paper crown beside a notebook','drew a tiny mascot on a removable sticky note','gave a pencil case a mock name badge',
      'left a fake award for excellent snack choices','placed a paper moustache on a worksheet folder','made a miniature sign for a water bottle',
      'left a cardboard microphone beside a desk','put a paper cape on a pencil holder','made a tiny cardboard trophy for a ruler',
      'left a mock weather forecast for the classroom','gave a notebook a humorous book-review sticker','made a paper VIP pass for a chair',
      'left a joke timetable for an imaginary class','placed a tiny cardboard stage beside a pen','left a paper fan-club badge for a calculator',
      'made a miniature red carpet for a school bag']
    for s in school_pranks:add('school-classmate-mess-scenarios',**{'Feedback Scenario':f'You {s} near <classmate-possessive> desk.',
      'Log Version':f'I {s} near <classmate-possessive> desk.','Hero Min Age':'11','Hero Max Age':'25','Classmate Gender':'both','Clean':'x'})
    trips=['a community recording studio','a public radio workshop','a local documentary archive','a small animation studio',
      'a community theatre sound booth','a regional motorsport engineering exhibition','a sports science exhibition',
      'a university accessibility laboratory','a public digital preservation centre','a community design workshop',
      'a local renewable energy exhibition','a student entrepreneurship showcase']
    tripbase=tables[name('backtoschool-field-trip-location')][1]
    for s in trips:clone('backtoschool-field-trip-location',tripbase,Location=s,**{'Hero Minimum Age':'11','Hero Maximum Age':'17'})
    for s in ['Studio Lights','Midnight Radio','Indie Release Party','Retro Arcade Prom','Paper Lantern Festival','School Showcase Celebration',
      'Film Score Night','Neon City Dance','Community Carnival','Vinyl and Velvet','Future Creators Ball','Starlight Rehearsal']:
        add('backtoschool-school-dance-theme',Theme=s)
    # Expensive asset features use existing costs and vehicle ownership mechanics.
    luxury={
      'car':['handcrafted acoustic cabin','bespoke panoramic interior','private collection display trim','custom touring luggage set',
        'commissioned artisan dashboard','premium wellness seating suite','bespoke grand touring package','signature coachwork detailing'],
      'aircraft':['private recording lounge','bespoke conference cabin','commissioned panoramic lounge','premium sleep suite',
        'custom concert-listening cabin','private art gallery interior','bespoke dining suite','signature collector cabin'],
      'watercraft':['independent artist performance deck','private recording lounge','bespoke observation salon','commissioned art gallery',
        'premium guest wellness suite','custom outdoor cinema deck','private conference salon','signature collector interior']}
    for kind,features in luxury.items():
        key=f'luxury-luxury-{kind}-special-feature';h=tables[name(key)][0]
        for i,s in enumerate(features):
            row=add(key,Feature=s,**{'Profile Color':'A commissioned luxury feature for your collection.',
              'Cost':str((i+2)*(1000000 if kind=='car' else 5000000)),'Commonness Score':'2'})
            if kind=='watercraft':
                for field in ['Sailing Yacht','Sailboat','Research Vessel','Cruise Ship','Submarine','Pirate Ship']:row[field]='x'
    return dict(content)

EFFECTS={'learn':(0,2,0,2,0),'speak':(1,1,0,1,0),'rest':(0,1,2,0,0),
  'avoid':(0,0,-1,0,0),'focus':(0,3,-1,1,0),'care':(2,1,1,0,0),
  'calm':(1,2,1,0,0),'dishonest':(-2,-2,0,0,0)}
def write_life_choices(row,choices,context):
    for i,(choice,effect) in enumerate(choices,1):
        row[f'Choice {i}']=choice;row[f'Narrative {i}']=f'I chose to {choice[0].lower()+choice[1:]} when dealing with {context}.'
        for f,v in zip(['Karma','Discipline','Happiness','Intelligence','Appearance'],EFFECTS[effect]):row[f'{f} Impact {i}']=str(v)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('tables');a=p.parse_args()
    content=author(json.loads(Path(a.tables).read_text()))
    (ROOT/'community_content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'new_records':sum(map(len,content.values())),'tables':{k:len(v) for k,v in content.items()}},indent=2))
