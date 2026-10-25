"""Distinct four-choice age-up scenes; preserve native fixed-width CSV contract."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent
# Title, minimum age, maximum age, scene, four distinct decisions.
scenes=[
("Borrowed Spotlight",18,0,"Your friend's first concert is sold out, but they ask you to open the show with almost no notice.",["Play a short acoustic set","Share the slot with another newcomer","Ask for a proper rehearsal first","Cheer from the audience"]),
("Algorithm Detour",13,0,"An old joke becomes your most popular upload while your careful new work gets little attention.",["Make one thoughtful follow-up","Pin my favourite original project","Explain the joke's context","Take a week away from posting"]),
("The Uncredited Beat",16,0,"A popular creator uses a beat that sounds remarkably like your unfinished demo.",["Compare the recordings privately","Ask them for a credit","Invite them to collaborate properly","Release my original version"]),
("Backstage Pass",18,0,"A festival offers you backstage access in return for filming everyone you meet.",["Ask each artist before filming","Film only my own experience","Trade the pass for a normal ticket","Leave the camera at home"]),
("Fan-made Artwork",13,0,"A follower sends a beautiful design and hopes you will use it for your next release.",["Offer a paid commission","Ask permission and give clear credit","Feature it in a fan gallery","Thank them without using it"]),
("Master Tape",18,0,"You discover an early recording that captures a sound you can no longer reproduce.",["Restore the tape carefully","Release it as an archival demo","Sample it in a new composition","Keep it as a private memory"]),
("Two Encores",18,0,"The audience calls for another encore, but the venue staff are trying to close.",["Thank the crowd and finish","Ask permission for one short song","Meet fans quietly outside","Promise an extra song next time"]),
("The Group Chat",13,0,"Your project group keeps making decisions while one quieter member is offline.",["Summarise the decisions for everyone","Schedule a meeting that includes them","Ask them to lead the next session","Pause the project for a day"]),
("Robotics Reversal",8,22,"Your club's robot works perfectly until the judges arrive and it starts moving backwards.",["Check the wiring calmly","Explain what the prototype taught us","Ask a teammate to troubleshoot","Demonstrate the manual controls"]),
("School Radio",8,22,"The school radio host loses their voice just before an important announcement.",["Read the announcement myself","Record it with a friend","Ask a teacher to take over","Switch to a written bulletin"]),
("The Debate Final",10,22,"You are assigned a debate position you strongly disagree with.",["Research the strongest arguments","Ask to explain my reservations","Separate debate practice from belief","Request a different role"]),
("A Quiet Lunch",6,22,"A new student sits alone every lunch break and declines invitations to noisy tables.",["Offer a quieter place to sit","Ask what they enjoy doing","Invite them to a small club meeting","Respect their space and stay friendly"]),
("The Scholarship Essay",14,22,"A scholarship asks you to describe a failure, but you would rather write about your achievements.",["Describe what I learned honestly","Ask a teacher for feedback","Write about helping a team recover","Choose another scholarship"]),
("The Late Bus",6,22,"Your bus route changes and makes you late for the first class twice in one week.",["Discuss the route with school staff","Set up a shared ride with permission","Leave earlier with a backup plan","Ask to collect missed notes"]),
("An Unexpected Mentor",16,0,"A retired professional offers to review your work if you can explain what you want to improve.",["Bring one focused question","Prepare a portfolio review","Ask about their biggest mistake","Suggest a monthly mentoring session"]),
("Credit Where Due",18,0,"Your supervisor praises you for an idea that a coworker helped develop.",["Credit my coworker immediately","Explain how we divided the work","Invite them to present the next update","Thank the supervisor and follow up privately"]),
("The Pilot Episode",18,0,"Your workplace wants a pilot episode that attracts viewers without embarrassing its contestants.",["Show the cast's real strengths","Test the concept with a small audience","Let contestants review sensitive scenes","Pitch a different format"]),
("Deadline Domino",18,0,"Three clients move their deadlines to the same Friday afternoon.",["Renegotiate the order openly","Ask for temporary team support","Reduce the scope of each delivery","Complete the smallest project first"]),
("The Broken Handover",18,0,"A colleague leaves without documenting a system that your team now relies on.",["Map the system with the team","Ask the colleague one final question","Create a simple replacement process","Escalate the risk before changing anything"]),
("A Salary Conversation",18,0,"A recruiter asks for your salary expectations before explaining the responsibilities.",["Ask for the role's salary range","Discuss the full benefits package","Describe my relevant experience first","Decline to name a figure yet"]),
("The Promotion Panel",18,0,"Your team asks who should present its project at an executive review.",["Offer to present with the team","Nominate the strongest speaker","Build a shared demonstration","Take the questions while others present"]),
("Work Without Rest",18,0,"Your hobby has become a second job and every free evening now has a deadline.",["Limit bookings for a month","Raise prices and take fewer projects","Protect one evening every week","Take a proper break"]),
("The Wet Forecast",16,0,"Rain is forecast for a local race, but your team argues about preparing for it.",["Prepare a wet-weather setup","Practice both possible conditions","Ask the engineer to compare forecasts","Prioritise safe handling over speed"]),
("The Rival's Apology",16,0,"A sporting rival apologises for a harsh interview after losing an important event.",["Accept it in private","Invite them to train together","Ask for a public correction","Keep the relationship professional"]),
("A Sponsor's Logo",16,0,"A small sponsor offers support if you cover most of your equipment with its logo.",["Negotiate a smaller placement","Ask for a short trial agreement","Compare another sponsor's offer","Keep my current setup"]),
("The Team Bus",12,0,"A teammate misses the bus before an away tournament and calls you in a panic.",["Tell the coach immediately","Help arrange a safe alternative ride","Send them the event schedule","Offer to cover their warm-up duties"]),
("The Charity Trophy",16,0,"You win a charity tournament and the organiser asks whether to auction your trophy.",["Donate it to the auction","Offer a signed item instead","Keep it and make a cash donation","Let the team decide together"]),
("The New Coach",10,0,"A new coach changes a training routine that had been working well for you.",["Try it for a limited period","Ask what the new routine targets","Share my training records","Request a gradual transition"]),
("Luxury With a Purpose",25,0,"A developer pitches a private retreat, but you wonder how often you would actually use it.",["Compare annual upkeep first","Visit before making any decision","Consider a community venue instead","Rent a similar place for a weekend"]),
("The Island Inspection",25,0,"A luxury property brochure looks perfect, but its photographs avoid the landing dock.",["Arrange an independent inspection","Ask about access in bad weather","Request maintenance records","Move on to another property"]),
("An Art Auction",18,0,"You love a painting at auction but notice several bidders behaving suspiciously alike.",["Set a firm maximum price","Ask the auctioneer about provenance","Wait for a later sale","Leave without bidding"]),
("The Annual Invoice",18,0,"A luxury purchase has an annual maintenance bill far larger than you expected.",["Review the contract line by line","Get a competing maintenance quote","Reduce optional services","Consider selling the asset"]),
("Tax Folder",18,0,"Your accountant asks for records that are scattered across messages and old notebooks.",["Create a single organised folder","Reconstruct the missing invoices","Book a review before filing","Improve next year's record system"]),
("The Community Studio",18,0,"Young artists ask if your unused studio could host an affordable workshop.",["Offer a supervised workshop","Sponsor a qualified teacher","Arrange a one-day open session","Help them find a public venue"]),
("The Reality Reunion",18,0,"A reality show invites its former cast back and encourages everyone to revive old arguments.",["Focus on what changed since filming","Set clear interview boundaries","Bring a funny shared memory","Skip the reunion"]),
("A Bad Edit",18,0,"A short clip makes a kind conversation look confrontational.",["Share the full context calmly","Ask the editor for a correction","Talk privately with the other person","Wait before responding publicly"]),
("The Voting Twist",18,0,"A TV competition adds a viewer vote halfway through the season.",["Explain my work directly to viewers","Keep concentrating on the challenge","Support the cast fairly","Question the timing with producers"]),
("A Surprise Audition",18,0,"A casting director likes your online videos and invites you to audition tomorrow.",["Prepare a short original piece","Ask for the audition requirements","Invite a trusted friend to rehearse","Request a later audition slot"]),
("The Sponsor Script",18,0,"A sponsor writes a testimonial about a product you have barely tried.",["Test it before agreeing","Rewrite the script in my own words","Clearly state my limited experience","Decline the promotion"]),
("The Impersonator",13,0,"Someone creates an account using your name and starts contacting your followers.",["Warn followers through my own profile","Report the impersonation","Ask friends to share the real account","Document the messages before reporting"]),
("Too Many Notifications",13,0,"Your phone keeps interrupting meals, rehearsals and conversations.",["Schedule notification windows","Mute nonessential group chats","Keep the phone away during meals","Take a weekend offline"]),
("The Subscriber Promise",16,0,"You promised subscribers a weekly series but the quality has started slipping.",["Publish a realistic new schedule","Offer a pause or refund option","Invite a collaborator to help","Replace it with a shorter format"]),
("A Small Viral Moment",13,0,"A brief helpful tutorial unexpectedly reaches far beyond your usual audience.",["Make a clear follow-up guide","Thank the original community","Answer the most common questions","Return to my normal schedule"]),
("Lost in Translation",13,0,"An overseas fan misunderstands a joke in your latest caption.",["Explain the meaning kindly","Edit the caption for clarity","Ask a fluent speaker for advice","Use a simpler caption next time"]),
("The Family Archive",18,0,"You find boxes of photographs with names nobody in the family recognises.",["Interview older relatives","Digitise and label the collection","Arrange a family archive day","Contact a local history group"]),
("The Garden Plot",18,0,"Neighbours offer you a shared garden plot, but it needs more work than expected.",["Start with a small section","Share a maintenance rota","Ask an experienced gardener for help","Support the project with supplies"]),
("A Forgotten Promise",12,0,"A friend reminds you that you promised to help them move on the day of your rehearsal.",["Help before rehearsal","Find another helper with permission","Reschedule my rehearsal","Apologise and arrange a practical alternative"]),
("The Train Conversation",16,0,"A stranger recognises your work on a train and asks for advice about starting out.",["Share one realistic first step","Recommend a useful practice routine","Explain a mistake I made early on","Suggest a local beginner group"]),
("The Reunion Band",30,0,"Old bandmates want to play together again, but everyone has a different idea of success.",["Agree on a small first show","Hold a rehearsal without commitments","Write down shared expectations","Enjoy a social catch-up instead"]),
("A Second Career",35,0,"A friend suggests retraining for a career you have always found interesting.",["Attend an introductory course","Interview someone doing that job","Try a small volunteer project","Build a gradual transition plan"]),
("The Empty Calendar",60,0,"After retirement, the first week without work feels less relaxing than you expected.",["Join a community project","Set a gentle weekly routine","Explore an old creative interest","Spend time with friends"]),
("A Student's Letter",45,0,"Someone you once mentored writes to say your advice changed their career.",["Write a thoughtful reply","Ask about their current project","Offer to review their next step","Suggest they mentor someone too"]),
("The Legacy Session",60,0,"A local archive wants to record your memories of a changing music scene.",["Bring recordings and dates","Invite another witness","Focus on overlooked performers","Record a short personal account"]),
("A Different Pace",65,0,"Your friends plan an ambitious trip, but you would prefer a slower itinerary.",["Suggest longer stops","Join only part of the trip","Plan a separate relaxed route","Meet them at the destination"]),
("The Community Final",60,0,"Your local sports club asks you to present its youth championship awards.",["Learn each finalist's story","Invite a young coach to speak","Donate useful team equipment","Keep the ceremony focused on the players"]),
("The Old Notebook",55,0,"You discover a notebook of business ideas from a much younger version of yourself.",["Try one modest idea","Share it with an interested relative","Compare the ideas with today's needs","Keep it as a reminder of my journey"]),
("Sibling Collaboration",12,0,"Your sibling wants to contribute to a project but lacks confidence in their skills.",["Give them a manageable role","Practice together first","Ask what they would enjoy doing","Introduce them to a beginner workshop"]),
("The Borrowed Instrument",10,0,"A friend returns your instrument with a small scratch and looks embarrassed.",["Ask what happened calmly","Check whether it affects the sound","Agree on a repair plan together","Thank them for being honest"]),
("A City Noise",16,0,"Street repairs disrupt a recording session you planned for weeks.",["Record a different part today","Use the sound creatively","Book a quieter studio slot","Reschedule and notify collaborators"]),
("The Missing Credit",18,0,"A project wins an award, but the published team list leaves out its junior assistants.",["Ask for a corrected team list","Thank the assistants publicly","Include them in the next presentation","Write to the organiser privately"]),
]
header=json.loads((R/'table_schema.json').read_text())
rows=[]
for i,(title,minimum,maximum,body,choices) in enumerate(scenes):
 row={h:'' for h in header};row.update({'Index':str(950000+i),'Hero Min Age':str(minimum),'Hero Max Age':str(maximum) if maximum else '', 'Randomize Choices':'x','Title':'Community+: '+title,'Body':body,'CTA':'What will you do?'})
 for k,choice in enumerate(choices,1):
  row['Choice '+str(k)]=choice
  row['Narrative '+str(k)]='I decided to '+choice[0].lower()+choice[1:]+'.'
  impact=[(1,2,1,1,0),(1,1,2,1,0),(0,1,1,2,0),(0,0,1,0,0)][k-1]
  for key,val in zip(['Karma','Discipline','Happiness','Intelligence','Appearance'],impact):row[key+' Impact '+str(k)]=str(val)
 rows.append(row)
(R/'age_content.json').write_text(json.dumps({'a16_dumb-scenarios-universal-enc':rows},ensure_ascii=False,indent=2)+'\n')
print('Authored',len(rows),'age-up scenes with',len(rows)*4,'distinct scene decisions.')
