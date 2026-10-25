"""Original music expansion content for existing BitLife 3.25 CSV schemas."""
import json
from pathlib import Path

CONTENT = {}
career = []

def event(title, body, lead, choices, min_pop='', max_pop='', min_res='', role=''):
    assert len(choices) == 4
    row = {'Index': str(21099 + len(career)), 'Hero Min Age': '18',
           'Solo': 'x', 'Band': 'x', 'Title': title, 'Body': body,
           'CTA': 'How will you handle it?', 'Min Popularity': str(min_pop),
           'Max Popularity': str(max_pop), 'Min Respect': str(min_res), 'Role': role}
    for i, (choice, pop, respect) in enumerate(choices, 1):
        row[f'Choice {i}'] = choice
        row[f'Narrative {i}'] = f'{lead} I chose to {choice[0].lower() + choice[1:]}.'
        row[f'Popularity Impact {i}'] = str(pop)
        row[f'Respect Impact {i}'] = str(respect)
    career.append(row)

# Eight interviews. These belong to musician events, not generic job interviews.
event('The Person Behind the Hit', 'An interviewer asks whether success has changed how you treat the people who knew you before the music. Your manager signals that the segment is live.', 'When an interviewer asked how fame had changed me,', [('Thank the people who supported me',2,3),('Admit I am still learning',1,3),('Turn the answer into an album plug',2,-1),('Mock the question',-2,-3)])
event('The Uncomfortable Question', 'A presenter reads an old post of yours that fans find dismissive. You remember writing it in frustration, but the clip leaves out the context.', 'During an interview about an old post,', [('Explain the context and apologize',1,3),('Listen to why fans were hurt',0,3),('Blame the presenter',1,-3),('Refuse to discuss it',-1,-1)])
event('Who Wrote the Hook?', 'A host praises the hook in your music as if you wrote every part alone. A collaborator is watching the broadcast and has already messaged you.', 'When a host overlooked a collaborator,', [('Give my collaborator credit',1,4),('Describe how we worked together',2,3),('Accept all the praise',2,-4),('Change the subject',0,-1)])
event('Rival on the Sofa', 'You arrive for a relaxed interview and discover the other guest is an artist whose fans have been arguing with yours. The host asks who deserves the bigger career.', 'During a joint interview with a rival,', [('Praise our different strengths',1,3),('Suggest a friendly collaboration',3,2),('Make a playful joke about the rivalry',2,0),('Insult the other artist',3,-4)])
event('The Quiet Comeback', 'An interviewer asks why you stepped away from the spotlight. You are comfortable sharing some of your story, but not every private detail.', 'At a comeback interview,', [('Share what I am comfortable sharing',2,3),('Set a polite boundary',0,3),('Discuss what I learned while away',1,2),('Invent a dramatic explanation',3,-3)])
event('A Fan Gets the Microphone', 'A fan in the studio audience asks why your latest creative direction sounds different. They miss the older music but seem willing to listen.', 'When a fan questioned my creative direction,', [('Explain what inspired the change',1,3),('Thank them for sticking with me',2,2),('Promise never to change again',1,-1),('Tell them to stop listening',-3,-4)])
event('Off the Record?', 'After a radio interview ends, the host asks for gossip about another artist. A recording light remains on behind the desk.', 'When a host asked for gossip after an interview,', [('Keep the conversation respectful',0,3),('Ask whether we are still recording',1,2),('Offer a harmless studio anecdote',2,1),('Share a cruel rumor',3,-4)])
event('Your Own Questions', 'A youth radio station invites you to choose the subject of an interview. They can focus on the music, the business, or a headline about your personal life.', 'When a youth station let me shape an interview,', [('Discuss how I make music',1,3),('Explain what beginners should know',1,4),('Talk about the pressure of fame',2,2),('Use the time to attack critics',2,-3)])

# Eight label and release disputes.
event('The Safer Single', 'Your label wants a familiar sounding single. You prefer a riskier direction, and both sides have strong opinions about what listeners will enjoy.', 'During a disagreement over a single,', [('Explain my creative vision',1,3),('Suggest testing both versions',2,2),('Accept the label suggestion',2,0),('Humiliate the team in public',2,-4)])
event('Credits Before Clout', 'A draft of your release announcement leaves a session musician out of the credits. The label says correcting it will delay the announcement.', 'When a session musician was left out of the credits,', [('Correct the credits first',0,4),('Contact the musician personally',1,3),('Publish now and correct it later',2,-1),('Pretend I never noticed',1,-4)])
event('The Viral Shortcut', 'A marketing executive suggests turning a private argument into a promotional clip. It would attract attention, but the other person never agreed to be part of the campaign.', 'When my team proposed using a private argument for promotion,', [('Reject the idea',0,3),('Offer a staged fictional alternative',2,2),('Ask the other person for permission',1,2),('Upload the private clip',3,-4)])
event('Surprise Release Pressure', 'Your team wants to announce a surprise release tonight. You like the excitement, but a key piece of the creative work still needs attention.', 'When my team pushed for a surprise announcement,', [('Finish the work before announcing it',0,3),('Announce a realistic teaser date',2,2),('Release an honest work in progress',1,1),('Claim everything is finished',2,-3)])
event('The Image Meeting', 'Your label presents a new public image that looks nothing like you. They call it a reinvention; you worry it will make every interview feel like acting.', 'At a meeting about my public image,', [('Build the image around my own style',1,3),('Try a few ideas without promising anything',2,1),('Ask trusted fans for feedback',2,2),('Adopt an image I openly dislike',1,-2)])
event('A Sponsor With Strings', 'A sponsor likes your music but wants you to avoid discussing a cause you care about. The offer would also give your team a bigger promotional platform.', 'When a sponsor tried to limit what I could discuss,', [('Keep my principles',0,4),('Negotiate clear boundaries',2,2),('Decline without making a scene',0,2),('Attack everyone involved online',2,-3)])
event('The Leaked Demo', 'An unfinished demo appears online. Some fans love the raw version, while others mistake its rough mix for your finished work.', 'After an unfinished demo leaked,', [('Explain that it is unfinished',1,2),('Thank listeners and show the creative process',3,2),('Let the mystery build',2,-1),('Blame an innocent collaborator',1,-4)])
event('Promises on a Poster', 'A draft promotional poster calls your next project a guaranteed classic. Your team thinks the claim is bold; you think it puts words in the listeners mouths.', 'When a poster promised too much about my project,', [('Let the music speak for itself',1,3),('Use a line about the inspiration instead',2,2),('Keep the boast as a playful slogan',2,0),('Promise awards before the release',3,-2)])

# Eight album-era and creative decisions.
event('The Next Chapter', 'Fans want to know whether your next project continues your familiar sound or starts a new chapter. You have enough ideas for either direction.', 'When fans asked about my next creative chapter,', [('Blend familiar sounds with new ideas',2,2),('Explain the new direction honestly',1,3),('Celebrate the sound that brought me here',2,1),('Say the old fans do not matter',-3,-4)])
event('The Listening Room', 'At a small preview session, one listener politely says the most personal moment on your project feels unfinished. Everyone watches to see how you respond.', 'At a preview listening session,', [('Ask what did not connect',1,3),('Explain the intention and listen',1,2),('Try a different arrangement',2,2),('Remove the listener from the room',-2,-4)])
event('Deluxe or Distraction?', 'Your team proposes a deluxe edition. You can share meaningful extra material, but you also worry that adding everything will distract from the original project.', 'During a discussion about a deluxe edition,', [('Choose only the strongest extras',2,3),('Share creative notes alongside the music',1,3),('Keep the original project complete',0,2),('Market unfinished scraps as essential tracks',2,-3)])
event('A Visual Thread', 'Your creative team pitches a visual theme connecting the release artwork and performances. One concept is striking but has nothing to do with the music.', 'When my creative team pitched a visual theme,', [('Choose the theme that fits the songs',2,3),('Develop a new concept together',1,3),('Try the striking concept as an experiment',2,0),('Copy another artist entire visual identity',2,-4)])
event('The Missing Verse', 'A collaborator asks why an important verse was removed from a preview version. You had creative reasons, but forgot to explain them before the listening session.', 'When a collaborator questioned a missing verse,', [('Discuss the decision privately',1,3),('Listen to their revised version',2,2),('Apologize for the poor communication',0,3),('Make fun of their writing',-1,-4)])
event('The Anniversary Edition', 'A fan group wants you to revisit an older project for its anniversary. You are proud of it, though some choices no longer represent your present taste.', 'When fans asked me to revisit an older project,', [('Discuss what the project meant then',2,3),('Share a fresh interpretation',2,2),('Celebrate it without rewriting its history',1,3),('Call the people who love it outdated',-3,-4)])
event('Two Worlds, One Sound', 'An artist from a different genre proposes a collaboration. Your teams worry about confusing listeners, but the creative chemistry feels promising.', 'When an artist from another genre proposed a collaboration,', [('Explore the shared creative ideas',2,3),('Start with a small studio experiment',1,2),('Explain the crossover to fans',2,2),('Dismiss their whole genre',-2,-4)])
event('The Honest Liner Notes', 'Your team asks how much personal context to include in the project notes. Some stories involve people who have never chosen a public life.', 'While planning the project notes,', [('Focus on my own experiences',1,3),('Ask permission before naming people',1,4),('Keep the notes about the craft',0,2),('Reveal someone private story for attention',3,-4)])

# Eight rivalries and fan community decisions.
event('Two Fandoms Collide', 'A disagreement between fan communities turns into a flood of hostile comments. Both sides claim they are defending their favorite artist.', 'When two fan communities began attacking each other,', [('Ask my fans to keep it respectful',1,4),('Celebrate both artists work',2,3),('Stay out of the argument',0,0),('Encourage the harassment',3,-4)])
event('The Shared Release Date', 'Another artist announces a release on the same date as yours. A blogger frames it as a feud even though neither artist has said anything hostile.', 'When a blogger turned a release date into a feud,', [('Wish the other artist well',1,3),('Explain that listeners can enjoy both',2,3),('Make a friendly chart prediction',2,0),('Accuse them of sabotaging me',3,-3)])
event('A Misquoted Lyric', 'A fan account claims a line in your music insults another artist. The interpretation is spreading faster than the context.', 'When a lyric was misinterpreted as an insult,', [('Explain the meaning without naming names',1,3),('Contact the other artist privately',0,3),('Let listeners interpret it freely',2,-1),('Invent a feud to promote the song',3,-4)])
event('The Invitation', 'An artist you have disagreed with invites you to a charity performance. Your team expects fans to treat every photo as evidence of a secret feud or friendship.', 'When a rival invited me to a charity performance,', [('Focus on the cause',1,4),('Accept and keep it professional',2,2),('Decline politely',0,1),('Publicly mock the invitation',2,-3)])
event('The Fan Moderator', 'A volunteer moderator tells you your fan community is becoming exhausting to manage. They love the music but are tired of settling arguments every day.', 'When a fan moderator said they felt overwhelmed,', [('Thank them and encourage a break',1,4),('Support clearer community rules',2,3),('Listen without making promises',0,2),('Demand that they work harder',-3,-4)])
event('The Fan Edit', 'A fan makes a thoughtful video connecting your older music with your newer work. A team member suggests reposting it without mentioning who made it.', 'When a fan made a thoughtful video about my work,', [('Credit the creator when sharing it',2,4),('Ask the creator before reposting it',1,3),('Leave them a kind comment',1,2),('Present the edit as my team work',2,-4)])
event('A Rival Gives Credit', 'An artist whose fans compete with yours says your work inspired them. A presenter asks whether you believe the compliment is sincere.', 'When a rival said my work inspired them,', [('Accept the compliment graciously',2,3),('Share what I admire about their work',2,3),('Say I appreciate it without speculating',1,2),('Accuse them of chasing attention',2,-3)])
event('The Chart Screenshot', 'A screenshot appears to show your music ahead of a rival, but the dates do not match. Fans ask you to repost it as proof that you won.', 'When fans sent me a misleading chart screenshot,', [('Check the dates before sharing',1,3),('Thank fans without comparing artists',2,2),('Explain why the comparison is misleading',0,4),('Post it with a victory caption',3,-3)])

# Eight comebacks and boundaries, without claiming unimplemented persistent flags.
event('Back in the Room', 'You return to a studio where you once had a disappointing session. The team asks whether you want to revisit the old idea or start fresh.', 'When I returned to a studio after a disappointing session,', [('Build on what I learned',1,3),('Start fresh with clear expectations',2,2),('Discuss the unfinished idea together',1,2),('Blame everyone for the old session',-1,-3)])
event('The Second Chance Clip', 'A short rehearsal clip earns warm comments after a stretch of criticism. Your team wants to turn the moment into a declaration that every critic was wrong.', 'When a rehearsal clip received a warm response,', [('Thank people for listening again',2,3),('Let the progress speak for itself',1,3),('Share what improved in my preparation',1,2),('Attack every critic by name',3,-4)])
event('A Small Stage Again', 'A local venue invites you to perform in an intimate setting. It is less glamorous than the image your team has been promoting, but the audience cares about the music.', 'When a local venue invited me to an intimate performance,', [('Treat the audience like a headline crowd',2,4),('Build a stripped back set',1,3),('Talk honestly about my journey',2,2),('Complain about the venue size',-2,-4)])
event('The Apology Draft', 'Your publicist drafts a polished apology for a recent public disagreement. It sounds impressive, but it barely acknowledges what actually hurt people.', 'When I reviewed a draft apology,', [('Rewrite it in my own words',1,4),('Acknowledge the specific harm',0,4),('Ask a trusted person for feedback',1,2),('Post it without reading carefully',2,-2)])
event('The Old Team Member', 'A former collaborator reaches out after hearing your new work. Your last project ended awkwardly, but they want to talk about what went wrong.', 'When a former collaborator asked to talk,', [('Hear them out privately',1,3),('Acknowledge my part in the disagreement',0,4),('Set clear limits for the conversation',0,2),('Post their message for entertainment',2,-4)])
event('A Healthier Schedule', 'Your team suggests packing every free day with promotional appearances. You worry that constant exhaustion will make it harder to deliver your best work.', 'During a discussion about my promotional schedule,', [('Set realistic limits',0,3),('Choose fewer meaningful appearances',1,3),('Discuss support with my team',1,2),('Pretend I can handle everything',2,-2)])
event('The New Listener', 'A young listener tells you this is the first project of yours they have heard. Your longtime fans insist they must study your whole catalogue before commenting.', 'When longtime fans challenged a new listener,', [('Welcome the new listener',2,3),('Suggest an easy starting point',1,3),('Encourage everyone to share favorites',2,2),('Agree that newcomers should stay silent',-2,-4)])
event('No More Perfect Image', 'An interviewer asks whether your comeback means you are finally a perfect role model. The question leaves little room for ordinary mistakes or growth.', 'When an interviewer called me a perfect role model,', [('Say growth is an ongoing process',1,4),('Discuss the lessons I can share',2,3),('Keep the answer focused on music',1,1),('Declare that I never make mistakes',2,-3)])

# Eight show and touring encounters. Stat effects only, not a new tour engine.
event('The Rain Check', 'Rain delays an outdoor performance. Some fans have traveled a long way, and your team is waiting for the venue to confirm what is safe.', 'When rain delayed an outdoor performance,', [('Keep fans informed while awaiting clearance',1,3),('Thank the crew and audience for patience',2,2),('Share a lighthearted backstage message',2,1),('Pressure the crew to ignore safety concerns',2,-4)])
event('The Missing Monitor', 'A monitor problem makes rehearsal frustrating. The crew is working on it, but a bystander starts recording your reaction.', 'During a monitor problem at rehearsal,', [('Work patiently with the crew',1,3),('Ask for a practical backup plan',1,2),('Laugh about the awkward rehearsal',2,1),('Yell at the nearest technician',2,-4)])
event('The Deep Cut Request', 'A crowd chants for an older favorite you had not planned to perform. You know the song, but your current set has a carefully rehearsed flow.', 'When a crowd requested an older favorite,', [('Acknowledge the request warmly',1,2),('Try a brief spontaneous version',3,2),('Explain why it is absent tonight',0,2),('Mock their taste',-3,-4)])
event('The Support Act', 'Your support act delivers a strong performance, and fans begin praising them online. Someone on your team suggests keeping their name off the recap.', 'After my support act earned enthusiastic praise,', [('Celebrate their performance',2,4),('Thank them publicly',1,3),('Share the spotlight in the recap',2,3),('Remove their credit',1,-4)])
event('The Accessibility Request', 'A fan asks whether your event announcements can include clearer accessibility information. Your team has never considered how hard it is to find those details.', 'When a fan asked for clearer accessibility information,', [('Raise the request with the venue',1,4),('Help the team communicate clearly',2,3),('Thank the fan for explaining',0,2),('Dismiss the request as inconvenient',-3,-4)])
event('The Quiet Audience', 'An audience listens quietly during a personal performance. Your team worries about the energy, but several listeners appear deeply moved.', 'When an audience listened quietly to my performance,', [('Respect the mood of the room',1,3),('Invite a gentle singalong',2,2),('Explain why the piece matters to me',1,3),('Insult the crowd for being quiet',-3,-4)])
event('The Backstage Promise', 'Someone on your team promises a fan a backstage meeting without checking with you. The fan is excited, but your schedule is already tight.', 'When my team made a backstage promise without checking,', [('Find a respectful solution',1,3),('Ask the team to explain honestly',0,3),('Offer a brief greeting if possible',2,2),('Blame the fan for believing it',-3,-4)])
event('A Crew Member Gets Applause', 'A technician quietly solves a difficult problem moments before your performance. The crowd has no idea who made the show possible.', 'After a technician saved a difficult performance,', [('Thank the crew onstage',2,4),('Give the technician personal credit',1,4),('Mention the team in my recap',2,3),('Claim I solved everything myself',2,-4)])

# Eight awards and recognition encounters, using existing choices and stats.
event('The Acceptance Speech Draft', 'Your team suggests an acceptance speech centered entirely on your personal brilliance. You have a short time to speak and a long list of people who helped.', 'When I prepared an acceptance speech,', [('Thank collaborators and supporters',2,4),('Tell a short story about the work',2,3),('Encourage the next generation',1,3),('Spend the speech mocking rivals',3,-4)],min_pop=50)
event('A Nomination, Not a Verdict', 'Fans are upset about an award nomination you did not receive. A reporter asks whether the omission means the whole industry is against you.', 'When a reporter questioned an award omission,', [('Celebrate the nominated artists',1,3),('Focus on the listeners who connect with my work',2,3),('Admit disappointment without attacking anyone',1,2),('Call every nominee undeserving',3,-4)],min_pop=40)
event('The Presenter Mispronounces It', 'At a public ceremony, a presenter mispronounces your name. They look embarrassed when they notice the mistake.', 'When a presenter mispronounced my name,', [('Correct it kindly',1,3),('Make a friendly joke',2,2),('Move on without a scene',0,2),('Humiliate the presenter',2,-4)],min_pop=40)
event('The Tribute Request', 'Organizers invite you to participate in a tribute to a respected musician. They ask whether you want to perform faithfully or reinterpret the work.', 'When organizers invited me to a musician tribute,', [('Honor the original spirit',1,3),('Explain a thoughtful reinterpretation',2,3),('Share a personal memory',2,2),('Make the whole segment about myself',3,-3)],min_pop=40)
event('The Camera Finds You', 'During another artist acceptance speech, a camera turns toward you. A fan account is already waiting to interpret every expression.', 'When a camera found me during another artist speech,', [('Applaud their achievement',1,3),('Smile and listen attentively',1,2),('Keep a neutral expression',0,0),('Make an obvious dismissive gesture',2,-3)],min_pop=50)
event('A Shared Honor', 'An event organizer introduces your work as a solo achievement even though a collaborator helped shape its most celebrated moments.', 'When an organizer overlooked a collaborator contribution,', [('Invite the collaborator into the moment',2,4),('Explain the shared creative process',1,4),('Thank them in my remarks',1,3),('Let the misleading introduction stand',2,-3)],min_pop=40)
event('The Red Carpet Question', 'On a red carpet, a reporter asks you to rank everyone else music from best to worst. You would rather discuss your own creative work.', 'When a red carpet reporter asked me to rank other artists,', [('Discuss the work I admire',2,3),('Set a friendly boundary',0,3),('Turn the question into a playful nonanswer',2,1),('Give a cruel ranking',3,-4)],min_pop=50)
event('The Next Generation', 'A beginner tells you that seeing your career recognized made their dream feel possible. A nearby reporter asks what advice you would give them.', 'When a beginner asked for advice at a public event,', [('Encourage practice and patience',1,4),('Explain that every path looks different',1,3),('Share one honest lesson',2,3),('Promise instant fame if they copy me',2,-3)],min_pop=40)
CONTENT['a16_dumb-scenarios-music-enc'] = career

producer=[]
def production(title,body,choices):
    row={'Hero Min Age':'18','Title':title,'Body':body,'CTA':'What will you do?'}
    for i,(choice,impact) in enumerate(choices,1):
        row[f'Choice {i}']=choice
        row[f'Narrative {i}']=f'During a studio decision about {title.lower()}, I chose to {choice[0].lower()+choice[1:]}.'
        row[f'Reputation Impact {i}']=str(impact)
    producer.append(row)
production('The Honest Credits','A session player notices their contribution is absent from the working credits. <artist> wants the release announcement out today.', [('Correct the credits',3),('Discuss the omission privately',2),('Promise a later correction',-1),('Ignore the contribution',-3)])
production('One More Take','<artist> wants another take even though the current recording is strong. You suspect fatigue is making every detail feel like a disaster.', [('Take a listening break',3),('Compare the takes calmly',2),('Record a short alternative',1),('Mock the concern',-3)])
production('The Reference Track','Your team brings a reference that sounds so close to another artist that the session is drifting toward imitation.', [('Discuss what makes the reference work',3),('Develop a distinct arrangement',3),('Ask for different references',2),('Copy every detail',-3)])
production('The Empty Credit','Someone who did not participate in a session asks for a prominent production credit because they introduced you to <artist>.', [('Keep the credits accurate',3),('Thank them separately',2),('Discuss an honest acknowledgment',2),('Give them a false production credit',-3)])
production('Room for a New Voice','A new engineer offers a useful idea but senior staff keep interrupting. <artist> is waiting to hear the options.', [('Give the engineer time to explain',3),('Test the idea fairly',3),('Discuss it after the session',1),('Join the dismissive jokes',-3)])
production('The Rush Mix','A deadline is approaching and <artist> hears a small but distracting problem. Fixing it needs focused work, not a public argument.', [('Check the issue carefully',3),('Discuss a realistic revision',2),('Explain the tradeoff honestly',1),('Pretend the issue is imaginary',-3)])
production('A Private Demo','A team member proposes sharing an intimate unfinished demo to build buzz. <artist> has not approved sharing it.', [('Ask the artist first',3),('Suggest an approved alternative',2),('Keep the demo private',3),('Share it without asking',-3)])
production('Too Many Opinions','Everyone in the room has a different suggestion, and <artist> is losing confidence in the song.', [('Return to the intended feeling',3),('Listen to one change at a time',2),('Take a short break',2),('Tell the artist to stop caring',-3)])
production('The Unexpected Genre','<artist> proposes a sound outside their familiar style. The team calls it a mistake before hearing a complete idea.', [('Explore the idea with an open mind',3),('Make a small creative experiment',2),('Discuss the audience expectations',1),('Reject the genre as worthless',-3)])
production('A Fair Listening Test','Two mixes divide the team. One is louder, while the other makes the vocal and arrangement easier to understand.', [('Compare them at equal volume',3),('Ask what serves the song',3),('Let the artist explain their preference',2),('Choose only the loudest mix',-2)])
production('The Studio Visitor','A visitor films a session with <artist>. The clip includes an unfinished piece and a private conversation.', [('Ask them to stop recording',3),('Discuss clear recording boundaries',2),('Offer an approved photo instead',2),('Encourage them to post everything',-3)])
production('Making Space','<artist> says the session pace feels overwhelming. A team member suggests that asking for a break shows weakness.', [('Support a reasonable break',3),('Reset the session expectations',2),('Ask what would help',2),('Agree that breaks are weakness',-3)])
production('The Melody Dispute','Two contributors both believe they created the strongest melody. <artist> wants you to settle the argument without hearing them out.', [('Hear both accounts',3),('Review the session notes together',3),('Suggest a fair discussion',2),('Credit whoever complains loudest',-3)])
production('A Changed Brief','After everyone agreed on a direction, a representative asks for a completely different mood. <artist> seems frustrated by the moving target.', [('Clarify the new creative brief',3),('Discuss the change with the artist',2),('Explain what can reasonably change',2),('Promise impossible revisions',-3)])
production('The Quiet Suggestion','<artist> quietly suggests removing an element you are proud of. They think the song breathes better without it.', [('Listen to the simpler version',3),('Discuss the emotional purpose',2),('Compare both versions',2),('Treat the suggestion as an insult',-3)])
production('The Fan Favorite Demo','A rough demo earns attention online. <artist> worries that a polished version will erase the quality people liked.', [('Identify what listeners connected with',3),('Preserve the meaningful imperfections',2),('Discuss the final direction honestly',2),('Dismiss every listener opinion',-3)])
production('A Better Introduction','A promising beginner arrives nervous and unsure what a professional session involves. <artist> wants the room to feel welcoming.', [('Explain the session calmly',3),('Give them a manageable first task',2),('Encourage questions',2),('Make them the target of a joke',-3)])
production('Listening Beyond the Numbers','A team member wants every creative decision based on what attracted attention last month. <artist> has an idea that does not fit that formula.', [('Balance insight with creative judgment',3),('Test the fresh idea',2),('Discuss what the artist wants to express',3),('Demand they imitate the last trend',-3)])
production('The Forgotten Session Player','An instrumental part transforms the session. The team praises your production but never mentions who played it.', [('Name the session player',3),('Explain their contribution',3),('Thank the entire team accurately',2),('Take all the credit',-3)])
production('Room to Disagree','<artist> dislikes a sound choice you love. The disagreement becomes tense, but neither of you has explained the reason for your preference.', [('Explain and listen',3),('Try a third option',2),('Let the artist compare both',2),('Make it a personal argument',-3)])
production('The Release Note','A release note claims you produced every part alone, even though several people helped build the recording.', [('Rewrite it accurately',3),('List the collaborators',3),('Ask the team to correct it',2),('Keep the exaggerated claim',-3)])
production('The Rehearsal Recording','<artist> brings a rehearsal recording with a compelling atmosphere but uneven sound. They ask whether the feeling is worth preserving.', [('Identify the strongest moments',3),('Build a thoughtful new version',2),('Discuss the technical limits',2),('Call the rehearsal worthless',-3)])
production('A Warm Return','A former collaborator returns after an awkward session years ago. <artist> asks whether the tension will affect today work.', [('Set clear shared expectations',3),('Discuss the past privately',2),('Focus on respectful collaboration',2),('Bring up old grievances in front of everyone',-3)])
production('The Last Listen','Before handing over a mix, <artist> asks for one uninterrupted listen. Your phone keeps filling with promotional requests.', [('Give the music my full attention',3),('Silence the phone briefly',2),('Schedule a focused review',2),('Pretend to listen while scrolling',-3)])
CONTENT['a16_music-producer-dumb-scenario-enc']=producer

fans=[]
def fan(scene,feedback,log,positive=True,minpop='',maxpop=''):
    fans.append({'Positive':'x' if positive else '', 'Negative':'' if positive else 'x',
      'Scenario':scene,'Feedback Snippet':feedback,'Log Version Snippet':log,
      'Hero Min Age':'18','Solo':'x','Band':'x','Min Popularity':str(minpop),'Max Popularity':str(maxpop)})
fan('A listener tells you your music kept them company during a difficult move. They ask which part of creating it meant the most to you.','said your music helped during a difficult move','said my music helped during a difficult move')
fan('A fan shows you a scrapbook of ticket stubs and handwritten memories from your performances. They do not ask for anything in return.','shared memories from your performances','shared memories from my performances')
fan('A listener says they only discovered you recently and asks which older project you would recommend first.','asked where to start with your older work','asked where to start with my older work')
fan('A fan thanks you for mentioning the session musicians in a public appearance. They say their sibling is learning an instrument.','thanked you for crediting session musicians','thanked me for crediting session musicians')
fan('A listener says your change in creative direction surprised them, but they enjoyed hearing the work grow.','said your creative growth surprised them in a good way','said my creative growth surprised them in a good way')
fan('A fan brings a carefully made drawing inspired by your music and asks whether you would like to see it.','offered a drawing inspired by your music','offered a drawing inspired by my music')
fan('A fan recognizes you but politely asks whether this is a convenient time to say hello.','asked respectfully before approaching you','asked respectfully before approaching me')
fan('A listener tells you they brought a friend to your performance and both left discussing different favorite moments.','shared a favorite memory from your performance','shared a favorite memory from my performance')
fan('A fan says your comeback gave them confidence to try a creative hobby again. They ask what helped you persist.','said your comeback encouraged them to try again','said my comeback encouraged them to try again')
fan('A fan explains that a quiet passage in your work became their favorite after several listens.','praised a quiet passage in your work','praised a quiet passage in my work')
fan('A listener asks about a collaborator after noticing their name in the credits. They are curious about how the work came together.','asked thoughtfully about a credited collaborator','asked thoughtfully about a credited collaborator')
fan('A fan tells you they appreciate seeing a support act get public recognition in your performance recap.','appreciated your support act getting recognition','appreciated my support act getting recognition')
fan('A listener complains that your newer direction no longer sounds like the work they first loved. They interrupt whenever you try to answer.','complained aggressively about your newer direction','complained aggressively about my newer direction',False)
fan('A fan demands private details about someone mentioned in your music and says you owe them the full story.','demanded private details about your personal life','demanded private details about my personal life',False)
fan('Someone loudly compares you with another artist and tries to provoke a hostile reaction for a recording.','tried to record you insulting another artist','tried to record me insulting another artist',False)
fan('A listener insists that everyone who likes your new work is a fake fan. They want you to repeat the claim.','tried to make you insult newer listeners','tried to make me insult newer listeners',False)
fan('A fan accuses you of ignoring them because you did not answer a message sent minutes ago.','demanded an immediate reply to a message','demanded an immediate reply to a message',False)
fan('Someone asks you to repost a misleading chart comparison and calls you disloyal when you question its dates.','pressured you to share a misleading chart comparison','pressured me to share a misleading chart comparison',False)
fan('A fan complains that you thanked too many collaborators instead of presenting yourself as the only creative force.','criticized you for sharing credit with collaborators','criticized me for sharing credit with collaborators',False)
fan('A listener follows you into a private conversation and insists on filming even after being asked to wait.','ignored your request for a private conversation','ignored my request for a private conversation',False)
fan('Someone demands you take a side in an argument between two fan communities and insults you for suggesting kindness.','demanded you take a side in a fan argument','demanded I take a side in a fan argument',False)
fan('A fan says a sincere interview answer sounded too ordinary and demands a more dramatic personal story.','demanded a more dramatic personal story from you','demanded a more dramatic personal story from me',False)
fan('A listener says they heard only a short clip of your work but refuses to consider that the full piece might sound different.','judged your work from a short clip alone','judged my work from a short clip alone',False)
fan('Someone mistakes you for another artist and becomes hostile when you gently correct them.','became hostile after mistaking you for another artist','became hostile after mistaking me for another artist',False)
CONTENT['a16_music-fan-interaction-scenarios-enc']=fans

comments=[
('says the small details get better on every listen.','praised the details that emerge with each listen'),
('says the melody stayed with <him/her> all day.','said the melody stayed with <him/her> all day'),
('asks who played the instrument in the quiet section.','asked about a musician in the quiet section'),
('praises the way the arrangement gives the vocal room to breathe.','praised the space around the vocal'),
('says <he/she> came for a short clip and stayed for the whole track.','said a short clip led <him/her> to the full track'),
('wants to know what inspired the sound.','asked about the inspiration for the sound'),
('says the ending makes <him/her> want to replay it.','praised the ending'),
('says the hook works without needing a huge production.','praised the understated hook'),
('says the atmosphere feels like a late night journey home.','praised the late night atmosphere'),
('notices a new detail in the background and asks about it.','noticed a detail in the background'),
('says <he/she> introduced a friend to the track.','said <he/she> shared the track with a friend'),
('says the emotion feels sincere rather than forced.','praised the sincere emotion'),
('asks whether there is a stripped back version.','asked for a stripped back version'),
('says <he/she> appreciates seeing the collaborators credited.','praised the collaborator credits'),
('says the rhythm makes an ordinary walk feel like a music video.','praised the rhythm'),
('says your recent creative growth is becoming easier to hear.','praised my recent creative growth'),
('says the intro takes too long to reach the strongest part.','criticized the length of the intro'),
('says the vocal is harder to understand than <he/she> expected.','said the vocal was hard to understand'),
('likes the idea but thinks the arrangement is overcrowded.','thought the arrangement was overcrowded'),
('says the ending arrives before the idea has room to develop.','thought the ending arrived too soon'),
('says the hook is memorable but the verses need more contrast.','wanted more contrast in the verses'),
('says the track sounds stronger through headphones than a phone speaker.','compared the headphone and phone speaker sound'),
('wants a little more space between the busiest sections.','wanted more space between the busiest sections'),
('says the track feels promising but not quite finished.','thought the track still needed finishing'),
('says the change in style caught <him/her> off guard.','was surprised by the change in style'),
('prefers your earlier work but wants to hear what comes next.','preferred my earlier work but remained curious'),
('says the loudest part loses some of the quieter emotion.','preferred the quieter emotional moments'),
('says <he/she> cannot decide between the demo feeling and the polished sound.','compared the demo feeling and polished sound'),
('asks why the most interesting instrument disappears so early.','asked about an instrument disappearing early'),
('says the idea would suit a live performance.','thought the track would suit a live performance'),
('thinks the cover creates a different expectation from the music.','compared the cover with the music'),
('says the track deserves a second listen before judging it.','encouraged a second listen before judging the track')]
CONTENT['a16_music-soundcloud-comment-enc']=[{'String':f'<he/she> {s}','Log Version':log} for s,log in comments]

CONTENT['a16_music-album-rejections-enc']=[{'Reason':s,'Solo':'x','Band':'x'} for s in [
 'They said the project needs a clearer creative direction.',
 'They said the strongest ideas are buried too far into the project.',
 'They said the proposed release feels rushed.',
 'They said the extra material does not justify another edition.',
 'They said the visual concept promises a sound the music does not deliver.',
 'They said the track order needs more thought.',
 'They said the project needs a stronger opening.',
 'They said the material would work better as a focused shorter release.',
 'They said the arrangements do not leave enough room for your strengths.',
 'They said the creative brief keeps changing.',
 'They said the project sounds more like a collection of experiments than a finished statement.',
 'They said the closing section does not resolve the ideas introduced earlier.'
]]
CONTENT['a16_music-band-breaks-up-scenarios-enc']=[{'Reason':s} for s in [
 'The members could not agree on the next creative direction.',
 'An argument over accurate credits damaged the trust between members.',
 'The group kept accepting commitments it could not realistically keep.',
 'Private disagreements kept becoming public arguments.',
 'One member wanted every decision to follow the latest trend.',
 'The members disagreed about how much of their private lives should become promotion.',
 'The rehearsal schedule stopped working for everyone.',
 'The members could not agree on how to share the spotlight.',
 'A promising collaboration exposed disagreements that had been ignored for years.',
 'The group realized its members wanted very different futures.',
 'An unresolved argument from the last project returned during rehearsals.',
 'The members felt they could no longer give the work their full attention.'
]]
CONTENT['a16_music-band-kicks-out-scenarios-enc']=[{'Reason':s} for s in [
 'They said you kept sharing unfinished work without asking the other members.',
 'They said you took credit for ideas the group developed together.',
 'They said your public comments made private disagreements worse.',
 'They said you interrupted every discussion about the next creative direction.',
 'They said you treated the support crew disrespectfully.',
 'They said you kept promising appearances before checking with the band.',
 'They said you dismissed every suggestion that was not your own.',
 'They said you turned rehearsal feedback into personal arguments.',
 'They said you expected the other members to protect an image they disliked.',
 'They said they could not trust you to keep private conversations private.',
 'They said you refused to share the spotlight.',
 'They said your priorities no longer matched the group direction.'
]]
practices=[
('You rehearsed a quieter arrangement to hear which elements mattered most.','I rehearsed a quieter arrangement to identify its strongest elements.'),
('You recorded a practice take and listened for rushed moments.','I listened to a practice take for rushed moments.'),
('You practiced moving smoothly between sections.','I practiced smoother transitions between sections.'),
('You compared an energetic interpretation with a more restrained one.','I compared energetic and restrained interpretations.'),
('You rehearsed without distractions and focused on the feeling of each phrase.','I rehearsed without distractions and focused on phrasing.'),
('You worked on delivering the opening with more confidence.','I worked on a more confident opening.'),
('You practiced keeping the same emotional focus through the ending.','I practiced keeping emotional focus through the ending.'),
('You listened back with a collaborator and discussed one useful improvement.','I reviewed a practice take with a collaborator.'),
('You rehearsed a familiar piece at a slower pace to notice weak spots.','I rehearsed a familiar piece slowly to find weak spots.'),
('You practiced recovering calmly after a small mistake.','I practiced recovering calmly from a mistake.'),
('You rehearsed how to introduce a piece without overexplaining it.','I practiced a clear introduction to a piece.'),
('You tested how the same piece felt in an intimate performance.','I tested a piece in a more intimate style.')]
CONTENT['a16_music-practice-scenarios-enc']=[{'Scenario':s,'Log Version':l} for s,l in practices]
CONTENT['a16_music-producer-artist-leave-string-enc']=[{'String':s,'Commonness Score':'3'} for s in [
 '<he/she> wants a team that understands the new direction of <his/her> music.',
 '<he/she> feels the sessions no longer leave room for <his/her> own ideas.',
 '<he/she> wants to explore a different creative partnership.',
 '<he/she> says the communication during sessions has become frustrating.',
 '<he/she> wants a working schedule that better fits <his/her> life.',
 '<he/she> says private disagreements have damaged the trust in the room.',
 '<he/she> feels the team is more interested in trends than the music.',
 '<he/she> wants a fresh start without turning the departure into a public feud.',
 '<he/she> thinks another producer would better suit <his/her> next project.',
 '<he/she> says <he/she> needs time to decide what kind of artist to become.',
 '<he/she> is disappointed by how a contributor credit was handled.',
 '<he/she> wants to rediscover the excitement <he/she> felt when starting out.'
]]

if __name__ == '__main__':
    target = Path(__file__).parent / 'music_content.json'
    target.write_text(json.dumps(CONTENT, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({name:len(rows) for name,rows in CONTENT.items()},indent=2))
