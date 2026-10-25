"""Author 250 prison entries using only the existing eight table schemas."""
import json
from pathlib import Path

# Each event has four authored responses: (choice, behaviour effect, respect effect).
EVENTS = [
('The Spare Blanket', 'Your new cellmate is shivering after the evening temperature drops. You have a spare blanket, but the laundry delivery is several days away.', [('Offer the spare blanket',2,2),('Ask staff for another blanket',3,0),('Trade it for a favour',0,1),('Laugh at the shivering',-2,-2)]),
('Lights Out', 'Your cellmate keeps reading under a small approved lamp after lights out. You have an early work assignment and cannot sleep.', [('Agree on a reading deadline',2,2),('Ask for a quieter arrangement',2,1),('Complain to the officer',1,-1),('Start shouting across the wing',-3,-2)]),
('The Apology', 'An inmate who embarrassed you yesterday offers an apology in front of the same audience. Others wait to see whether you will accept it.', [('Accept without making a show',2,3),('Explain why it bothered you',2,2),('Keep your distance politely',1,0),('Demand a humiliating apology',-2,-2)]),
('Shared Shelf', 'Your cellmate says your books take up the entire shared shelf. A carefully stacked pile is already leaning over the edge.', [('Divide the shelf fairly',2,2),('Donate books you have finished',3,1),('Ask staff to clarify the rule',1,0),('Claim the whole shelf',-2,-2)]),
('The Missing Photograph', 'Your cellmate cannot find a family photograph and suspects you moved it. You remember seeing it behind the sink earlier.', [('Help look behind the sink',2,2),('Explain what you remember',1,1),('Wait for the accusation to cool',0,-1),('Turn the accusation into a feud',-3,-2)]),
('New Arrival', 'A new inmate arrives looking overwhelmed and asks where to collect bedding. A nearby group tells you to leave the newcomer to figure it out.', [('Explain the intake routine',2,2),('Point out the intake officer',2,1),('Offer help after your shift',1,1),('Join in the mockery',-2,-2)]),
('A Quiet Minute', 'Your cellmate returns from a difficult phone call and sits silently on the bunk. Other inmates want to know what happened.', [('Give your cellmate privacy',2,2),('Offer to listen privately',2,2),('Suggest speaking with support staff',3,1),('Repeat the news around the wing',-2,-3)]),
('Borrowed Pencil', 'An inmate asks to borrow your last pencil to finish a letter before collection. Your own letter is only half written.', [('Take turns using the pencil',2,2),('Ask the library for a spare',2,1),('Finish quickly and lend it',1,1),('Demand a ridiculous payment',-1,-2)]),
('The Cell Inspection', 'A routine inspection finds clutter in the space you share. Your cellmate insists every misplaced item belongs to you.', [('Sort your items and discuss the rest',3,1),('Ask for a shared cleaning schedule',2,2),('Let the officer assign responsibility',1,-1),('Blame your cellmate for everything',-2,-2)]),
('A Different Routine', 'Your cellmate wants quiet time while you prefer talking after dinner. Neither of you has another room to retreat to.', [('Agree on a daily quiet period',2,2),('Spend part of the evening reading',2,1),('Ask about a suitable reassignment',1,0),('Make noise to prove a point',-3,-2)]),
('The Lost Book', 'A borrowed library book has disappeared from your cell. The librarian says the next reader has been waiting all week.', [('Report it and help search',3,1),('Ask for time to retrace your steps',2,1),('Offer another approved book',1,1),('Accuse the next reader without evidence',-2,-2)]),
('Library Volunteer', 'The prison library needs help repairing worn book covers. The assignment would use some of your recreation time.', [('Volunteer for a regular shift',3,2),('Offer one afternoon a week',2,1),('Recommend someone with experience',1,1),('Mock the people who volunteer',-1,-2)]),
('The Waiting List', 'Two inmates argue over who signed up first for a popular novel. You are holding the sign-out sheet.', [('Check the recorded order',2,2),('Suggest a shared reading deadline',2,1),('Ask the librarian to decide',2,0),('Give it to whoever intimidates you',-1,-2)]),
('A Difficult Paragraph', 'An inmate quietly asks you to explain a paragraph in a course workbook. Others are nearby and the inmate seems embarrassed.', [('Explain it without drawing attention',3,2),('Offer to study together',3,2),('Suggest the education tutor',2,1),('Read the mistake aloud for laughs',-2,-3)]),
('The Study Group', 'A small study group invites you to help prepare for a literacy assessment. One member wants to turn the session into gossip.', [('Keep the group on the workbook',3,2),('Allow a short break before studying',2,2),('Study separately this time',1,0),('Spend the whole session spreading rumours',-2,-1)]),
('A Class Presentation', 'Your education instructor asks for volunteers to present a short book review. Your hands shake when you imagine speaking to the class.', [('Volunteer and prepare carefully',3,2),('Ask to present with a partner',2,2),('Request another assignment',1,0),('Heckle the first volunteer',-2,-2)]),
('The Wrong Page', 'The classroom receives workbooks with several pages missing. A few inmates accuse the instructor of doing it on purpose.', [('Show the missing pages calmly',2,2),('Share a complete copy while staff check',3,2),('Wait for replacement materials',1,0),('Encourage the accusation',-2,-2)]),
('Learning Something New', 'A classmate offers to teach you a few phrases in another language during approved study time. Someone nearby calls the idea pointless.', [('Practise the phrases respectfully',2,2),('Offer to teach a skill in return',2,2),('Listen for a few minutes',1,1),('Make fun of the classmate',-2,-2)]),
('The Finished Course', 'You complete a short education course and receive a certificate. Another inmate says achievements inside prison do not count.', [('Keep the certificate and your plans',3,2),('Thank the instructor',3,1),('Talk about the next course',2,2),('Throw the certificate away angrily',-2,-1)]),
('A Letter Draft', 'An inmate asks you to check a letter for unclear wording. The letter contains a painful family disagreement.', [('Help with wording without prying',2,2),('Suggest a calmer first draft',2,1),('Recommend the writing tutor',2,1),('Share the contents with others',-2,-3)]),
('Kitchen Shortage', 'The kitchen team is short of volunteers after two workers are reassigned. Your supervisor asks whether you can help with an approved extra shift.', [('Take the extra shift',3,2),('Offer part of the shift',2,1),('Explain a genuine scheduling conflict',1,0),('Encourage everyone to abandon the shift',-3,-2)]),
('The Unequal Rota', 'You notice the work rota assigns the least popular cleaning task to the same person every day. The supervisor asks for suggestions.', [('Suggest rotating the task fairly',3,2),('Offer to take one turn',3,2),('Ask how the rota was decided',2,1),('Insist the other person deserves it',-2,-2)]),
('Broken Equipment', 'A cleaning tool breaks during your shift. An inmate suggests leaving it for the next crew rather than reporting it.', [('Report the damage immediately',3,1),('Label it and tell the supervisor',3,2),('Ask for a safe replacement',2,1),('Hide it among the working tools',-3,-2)]),
('The New Worker', 'A new prison worker cannot remember the order of a routine task. The rest of the team is getting impatient.', [('Demonstrate the approved routine',3,2),('Ask the supervisor to help',2,1),('Suggest splitting the task',2,2),('Make the new worker the joke of the shift',-2,-3)]),
('Taking the Credit', 'A teammate tells the supervisor that a task you completed was entirely their work. You are asked what happened.', [('Explain each contribution calmly',2,2),('Ask the teammate to correct the account',2,2),('Let the work record speak for itself',1,1),('Start a shouting match',-3,-2)]),
('Late to Work', 'An unexpected headcount delays your arrival at a work assignment. The supervisor initially assumes you slept in.', [('Explain the headcount delay',2,1),('Ask the officer to confirm the delay',2,1),('Offer to finish the missed portion',3,2),('Insult the supervisor',-3,-2)]),
('The Quality Check', 'Your work crew discovers a mistake in a completed batch. Correcting it will take the last hour of the shift.', [('Help correct the mistake',3,2),('Suggest a second check for next time',3,1),('Ask the supervisor how to prioritise it',2,1),('Pretend you never noticed',-2,-2)]),
('An Extra Responsibility', 'A supervisor offers you responsibility for keeping the work-area checklist. Other inmates warn that it may make you unpopular.', [('Keep the checklist fairly',3,2),('Ask everyone to help design it',3,3),('Decline politely',0,0),('Use the role to settle grudges',-3,-3)]),
('The Exhausted Crew', 'Your crew is tired after a long assignment and begins snapping at one another. A short approved break is available.', [('Suggest taking the break together',2,2),('Offer to swap tasks for variety',2,2),('Ask the supervisor to review the workload',3,1),('Call everyone lazy',-2,-2)]),
('A Useful Suggestion', 'You spot a simpler way to organise approved laundry supplies. The supervisor invites you to explain it to the crew.', [('Explain it and invite feedback',3,2),('Try it with the supervisor watching',3,1),('Share the idea with an experienced worker',2,2),('Claim you are smarter than everyone',-1,-2)]),
('The Short Phone Call', 'Your family call is cut short because another inmate has an urgent approved call. You still have several things to say.', [('Arrange another call calmly',2,2),('Ask staff about the next available slot',2,1),('Write down what you wanted to say',2,1),('Yell at the other caller',-3,-2)]),
('A Missed Visit', 'Someone you expected to visit cannot make the journey. An inmate tells you the cancellation proves you have been forgotten.', [('Ask what happened before judging',2,2),('Send a reassuring letter',2,1),('Talk with support staff about the disappointment',3,1),('Send an angry accusation',-2,-1)]),
("A Child's Drawing", 'A visitor brings an approved drawing from a young family member. A nearby inmate makes a dismissive remark about it.', [('Keep the drawing with your letters',2,2),('Thank the visitor and ask about the artist',2,1),('Ignore the remark',1,1),('Turn the visit into an argument',-2,-2)]),
('The Difficult Update', 'A relative tells you that things at home have changed while you have been away. You feel left out of decisions you cannot control.', [('Listen before responding',2,2),('Ask what support you can still offer',3,2),('Request time to think',1,1),('Demand that every decision wait for you',-2,-2)]),
('The Honest Letter', 'You start a letter about a mistake you made, then wonder whether admitting it will damage an important relationship.', [('Take responsibility without excuses',3,2),('Rewrite it in clear respectful language',2,1),('Ask the writing tutor for help',2,1),('Blame the recipient instead',-2,-2)]),
('The Birthday Card', 'An approved birthday card arrives a week late. Someone jokes that even the mailroom forgot about you.', [('Appreciate that someone remembered',2,2),('Send a thank-you letter',2,1),('Ask staff about the delay politely',1,0),('Tear up the card in anger',-2,-1)]),
('A Promise to Keep', 'During a visit you are asked to make a promise about life after release. You want to offer reassurance without promising the impossible.', [('Make a realistic commitment',3,2),('Explain the steps you can control',3,2),('Ask to discuss the details later',1,1),('Promise anything to end the conversation',-2,-1)]),
('A Rumour from Home', 'Another inmate claims to know a worrying story about your family. You have no way to check it until your next approved call.', [('Wait to verify it with your family',2,2),('Write down a calm question for the call',2,1),('Talk to support staff about the worry',3,1),('Spread the story as a fact',-2,-2)]),
('The Visiting Room', 'Two visitors in the waiting area are arguing loudly. Your own visit is about to begin and you are tempted to get involved.', [('Let staff handle the argument',2,1),('Focus on your own visitor',2,2),('Ask whether the visit can start elsewhere',1,0),('Join the shouting',-3,-2)]),
('Starting Again', 'A relative offers to exchange regular letters, but says conversations must be respectful. You know rebuilding trust will take time.', [('Agree to the boundary',3,2),('Suggest a manageable writing schedule',2,2),('Ask what topics feel comfortable',2,1),('Demand forgiveness immediately',-2,-2)]),
('The Yard Queue', 'An inmate tries to move ahead of you in the queue for recreation equipment. Several people are watching your reaction.', [('Point out the queue calmly',2,2),('Suggest taking turns',2,2),('Let staff settle the order',2,-1),('Shove the queue into an argument',-3,-2)]),
('A Bad Call', 'During a casual yard game, two inmates disagree about the score. You saw the disputed play clearly.', [('Describe what you saw fairly',2,2),('Suggest replaying the point',2,2),('Step away from the argument',1,0),('Favour a friend despite what you saw',-1,-2)]),
('The New Team', 'You are asked to choose teams for a yard game. One inmate insists the newest arrival should always be picked last.', [('Choose teams fairly',2,3),('Rotate captains after each game',2,2),('Ask for volunteers first',1,1),('Exclude the newcomer for laughs',-2,-2)]),
('A Changed Yard Schedule', 'Recreation time is moved to a different slot. An inmate urges you to ignore the announcement and go out at the old time.', [('Follow the new schedule',3,0),('Ask staff for the reason',2,1),('Submit a polite request for review',2,2),('Ignore the announcement',-3,-1)]),
('The Empty Bench', 'An inmate who usually talks to you sits alone at the edge of the yard. Others insist there must be a dramatic reason.', [('Offer quiet company',2,2),('Ask whether space would help',2,2),('Leave an invitation to join you later',1,1),('Invent a story about the silence',-2,-2)]),
('The Borrowed Ball', 'A recreation ball goes missing after your group uses it. The next group blames everyone involved.', [('Help search the recreation area',2,2),('Explain where it was last seen',2,1),('Ask staff to check the sign-out record',2,0),('Blame an uninvolved inmate',-2,-2)]),
('An Unfair Joke', 'A group makes repeated jokes about an inmate struggling with a yard activity. The inmate tries to laugh along but looks upset.', [('Ask the group to ease off',2,3),('Invite the inmate to join your activity',2,2),('Check in privately afterward',2,1),('Add another joke',-2,-2)]),
('The Winning Streak', 'Your team wins several yard games in a row. A teammate wants to mock everyone who lost.', [('Celebrate without insulting anyone',2,2),('Congratulate the other team',2,3),('Suggest mixing the teams next time',2,2),('Join the taunting',-2,-2)]),
('A Different Game', 'A group proposes a new approved recreation activity, but nobody agrees on the rules. You are invited to help organise it.', [('Write down simple shared rules',2,2),('Try a short practice round',2,2),('Ask recreation staff for guidance',2,1),('Change the rules whenever you lose',-2,-3)]),
('The Weather Change', 'Recreation is moved indoors because of bad weather. A disappointed inmate begins taking it out on everyone nearby.', [('Suggest an indoor activity',2,2),('Give the inmate space to cool down',2,1),('Ask staff about the indoor schedule',1,0),('Start provoking the inmate',-3,-2)]),
('The Quiet Request', 'An officer asks your group to lower the noise during a routine announcement. One inmate urges everyone to talk over it.', [('Listen to the announcement',3,1),('Ask the group to wait a minute',2,2),('Move to a quieter permitted area',2,0),('Shout over the officer',-3,-2)]),
('A Misunderstanding', 'An officer mistakes a permitted item for something unauthorised. You have the approval slip in your belongings.', [('Show the approval slip calmly',3,1),('Ask another officer to confirm it',2,1),('Accept a temporary check of the item',2,0),('Refuse every request angrily',-3,-2)]),
('The Complaint Form', 'You want to complain about a recurring problem, but an inmate suggests filling the form with insults so staff will notice.', [('Describe the problem with dates',3,2),('Ask for help with clear wording',2,1),('Discuss it respectfully with staff first',2,1),('Fill the form with personal insults',-2,-2)]),
('A Fair Account', 'Staff ask what happened during an argument you witnessed. A friend asks you to leave out an important detail.', [('Give an accurate account',3,1),('Explain only what you personally saw',3,2),('Ask to speak privately',2,0),('Invent details to protect your friend',-3,-2)]),
('The New Officer', 'A new officer mixes up the recreation timetable. Other inmates encourage you to make the confusion as embarrassing as possible.', [('Point out the timetable politely',2,2),('Ask for the announcement to be clarified',2,1),('Wait for staff to correct it',1,0),('Turn the mistake into a public insult',-2,-2)]),
('The Delayed Request', 'An approved request has been waiting longer than expected. An officer says the responsible staff member is absent today.', [('Ask when you should check again',2,1),('Submit a brief written follow-up',3,1),('Wait until the next scheduled review',1,0),('Harass every officer about it',-3,-2)]),
('The Shared Responsibility', 'Staff remind your wing to clean a common area. One inmate argues that everyone should refuse because a few people caused the mess.', [('Help and suggest a fair rota',3,2),('Clean your own contribution',2,1),('Ask staff to assign tasks clearly',2,0),('Make the mess worse in protest',-3,-2)]),
('An Incorrect Record', 'A work attendance sheet incorrectly lists you as absent. You notice before the weekly review.', [('Ask for the record to be checked',3,1),('Show the completed work log',2,1),('Request a written correction',2,0),('Accuse the clerk of a conspiracy',-2,-2)]),
('The Long Wait', 'A routine count takes longer than usual. An inmate begins demanding that everyone refuse to cooperate.', [('Cooperate and wait for instructions',3,0),('Ask whether there is an update',2,1),('Help keep the nearby group calm',2,2),('Encourage a shouting contest',-3,-2)]),
('A Respectful Boundary', 'An officer jokes about a topic you find upsetting. You want to set a boundary without turning it into a confrontation.', [('Explain the concern calmly',2,2),('Request a private conversation',2,1),('Use the formal complaint process',3,0),('Respond with a personal threat',-4,-2)]),
('The Group Pressure', 'An inmate group says you must take sides in a disagreement you barely understand. They demand an answer immediately.', [('Decline to join an unknown dispute',2,2),('Ask to hear both accounts first',2,2),('Leave the conversation calmly',1,1),('Promise support without knowing the facts',-2,-2)]),
('Borrowed Reputation', 'An inmate claims you support an intimidating demand, even though you never agreed to it. The affected person asks whether it is true.', [('Correct the claim clearly',2,3),('Speak to both people privately',2,2),('Ask staff for help with the pressure',3,-1),('Let the false claim stand',-2,-2)]),
('The Escalating Rumour', 'A rumour turns a small disagreement into a serious feud. You know the original conversation was much less dramatic.', [('Explain the original conversation',2,2),('Ask people to stop repeating guesses',2,3),('Stay out of spreading the rumour',1,1),('Add a more dramatic detail',-3,-3)]),
('A Forced Favour', 'An inmate says you owe a favour because of help you never requested. The demand makes you uncomfortable.', [('Set a clear respectful boundary',2,2),('Explain that no agreement was made',2,1),('Seek staff support',3,-1),('Threaten a bigger favour in return',-3,-2)]),
('The Wrong Audience', 'A heated argument draws a growing audience. A friend urges you to give the crowd something to talk about.', [('Move away from the crowd',2,2),('Suggest discussing it later',2,2),('Ask staff to separate the group',3,-1),('Perform for the crowd',-3,-2)]),
('A Private Warning', 'An inmate warns that a harmless comment has been misunderstood. You have a chance to clarify it before the story spreads.', [('Clarify the comment directly',2,2),('Ask what was misunderstood',2,1),('Give everyone time to cool down',1,1),('Send an even harsher message',-3,-2)]),
('The Unwanted Invitation', 'A group invites you into an argument with another wing. You would rather stay focused on your own routine.', [('Decline without insulting anyone',2,2),('Suggest a peaceful alternative',3,2),('Ask staff for support if pressured',3,-1),('Join to impress the group',-3,-2)]),
('The Convenient Scapegoat', 'A group blames a quiet inmate for a broken shared item. Nobody has evidence, but the accusation is gaining momentum.', [('Ask what anyone actually witnessed',2,3),('Support checking the records',3,2),('Refuse to repeat the accusation',2,2),('Join the blame to fit in',-3,-3)]),
('An Old Grudge', 'An inmate wants you to revive a disagreement that had already settled down. The reason seems to be boredom.', [('Leave the settled disagreement alone',2,2),('Suggest a different activity',2,1),('Remind everyone what was agreed',2,2),('Restart the argument for entertainment',-3,-2)]),
('A Chance to De-escalate', 'Two inmates stop arguing long enough for you to speak. Both expect you to declare a winner.', [('Help them agree on the next step',3,3),('Ask each to explain one concern',2,2),('Suggest taking a break',2,2),('Insult both sides',-3,-3)]),
('The Release Checklist', 'A rehabilitation class asks you to list practical priorities for life after release. Others dismiss the exercise as pointless.', [('Write a realistic checklist',3,2),('Ask about housing and work support',3,1),('Focus on one achievable first step',2,2),('Refuse to consider any plan',-2,-1)]),
('Anger in the Workshop', 'A discussion in a rehabilitation workshop touches a sensitive subject. You feel yourself becoming defensive.', [('Pause before responding',3,2),('Explain your reaction without blaming others',3,2),('Ask for a short break',2,1),('Shout down the discussion',-3,-2)]),
('The Accountability Exercise', 'You are asked to describe a decision you regret without explaining it away. The room is unusually quiet.', [('Take responsibility for the decision',3,2),('Explain what you would do differently',3,2),('Ask for time to organise your thoughts',1,1),('Blame everyone except yourself',-2,-2)]),
('A Useful Habit', 'A support worker asks which daily habit has helped you cope constructively. You have been keeping a simple routine.', [('Describe the routine honestly',3,1),('Share a habit someone else could try',2,2),('Ask for ideas to improve it',2,1),('Pretend you never struggle',-1,-1)]),
('The Peer Mentor', 'You are invited to speak with a newcomer about adjusting to prison life. The session will be supervised.', [('Offer practical respectful encouragement',3,2),('Explain where support is available',3,2),('Decline if you feel unprepared',1,0),('Use the session to intimidate the newcomer',-3,-3)]),
('A Setback', 'You miss a personal goal after a difficult week. Another inmate tells you that one setback proves there is no point trying.', [('Review the setback and try again',3,2),('Ask for help adjusting the goal',3,1),('Choose a smaller next step',2,2),('Abandon every goal in anger',-2,-1)]),
('The Progress Review', 'A support worker asks what has changed since your last review. You are tempted to exaggerate your progress.', [('Give specific honest examples',3,2),('Discuss progress and remaining problems',3,2),('Ask how progress is being measured',2,1),('Invent achievements you cannot explain',-3,-2)]),
("Someone Else's Success", 'An inmate you know completes a programme you found difficult. Several people expect you to be jealous.', [('Congratulate the inmate',2,3),('Ask what helped them succeed',3,2),('Use it as motivation for your own goal',2,2),('Dismiss the achievement as luck',-2,-2)]),
('A Difficult Conversation', 'A supervised discussion asks how you would handle conflict after release. You realise your old approach often made things worse.', [('Describe a calmer alternative',3,2),('Practise asking for a pause',3,1),('Ask for feedback on your plan',2,2),('Insist that louder always wins',-2,-2)]),
('The Next Chapter', 'You are asked to write a short description of the person you want to become. Nobody will grade your spelling.', [('Write an honest achievable goal',3,2),('Include how you will treat other people',3,2),('Start with one positive habit',2,1),('Write only about settling old scores',-3,-2)]),
]

PAROLE = [
('What would you do first to arrange stable housing after release?', 'contact an approved housing service', 'ask a trusted relative about agreed temporary accommodation', 'check my options before making a promise', 'assume someone will solve it for me', 'move wherever I can cause trouble', 'refuse to make a housing plan'),
('How would you prepare for finding lawful work after release?', 'prepare a realistic job search and use employment support', 'update my work history with help from an adviser', 'ask which employers may consider my experience', 'wait for an effortless job to appear', 'plan to return to illegal income', 'say work is beneath me'),
('How would you respond if someone offered you a chance to repeat an old offence?', 'refuse and contact a trusted support person', 'leave the situation and review my safety plan', 'take time away before responding', 'say it depends on whether anyone notices', 'accept the offer immediately', 'blame others for making the offer'),
('What would you do if anger started affecting a disagreement after release?', 'pause and use the coping skills I have practised', 'ask to continue the discussion when everyone is calmer', 'seek help if I cannot calm down', 'expect the other person to calm me down', 'use threats to get my way', 'insist that losing my temper is unavoidable'),
('How would you rebuild trust with someone affected by your actions?', 'take responsibility and respect their boundaries', 'make consistent commitments I can actually keep', 'ask what contact they feel comfortable with', 'expect trust to return immediately', 'demand forgiveness', 'say their feelings are not my problem'),
('How would you manage your appointments and reporting requirements?', 'keep a written schedule and confirm the requirements', 'set reminders and ask for help with transport', 'contact the responsible officer when something is unclear', 'rely on remembering everything without checking', 'ignore appointments I dislike', 'assume the rules do not apply to me'),
('What would you do if transport problems threatened an important appointment?', 'contact the office early and ask about approved options', 'plan an alternative route with my support worker', 'explain the problem as soon as I know about it', 'wait until after the appointment to mention it', 'skip it and hope nobody notices', 'claim transport is always someone else’s responsibility'),
('How would you make a realistic budget after release?', 'list essential costs and seek help with a manageable budget', 'prioritise housing food and appointments', 'ask an adviser to review the numbers with me', 'spend first and worry later', 'use illegal income to cover every shortfall', 'refuse to discuss money responsibly'),
('What would you do if a family member wanted less contact than you hoped?', 'respect the boundary and work on rebuilding trust', 'ask what contact would feel comfortable', 'talk with a support worker about the disappointment', 'keep calling until they give in', 'punish them for setting a boundary', 'say I am entitled to their attention'),
('How would you handle a mistake in your release paperwork?', 'ask the responsible officer to check it before acting', 'bring the relevant documents to an appointment', 'request clarification in writing', 'assume the mistake gives me permission to do anything', 'use it as an excuse to ignore every condition', 'hide it and blame staff later'),
('How would you respond to a disagreement with a supervisor at a new job?', 'describe the issue calmly and use the proper workplace process', 'ask for a private conversation about expectations', 'seek advice before reacting', 'walk out without discussing the problem', 'threaten the supervisor', 'sabotage the work to prove a point'),
('What would you do if you felt overwhelmed by the first week after release?', 'contact my support worker and review priorities', 'break the week into manageable tasks', 'ask trusted people for specific help', 'pretend everything is fine until I miss commitments', 'return to harmful old habits immediately', 'blame everyone else and reject assistance'),
('How would you put what you learned in education into practice?', 'use my skills in a realistic training or work plan', 'ask about a suitable next course', 'practise the skills regularly', 'assume the certificate means no more effort is needed', 'mock the idea of continuing education', 'say learning was only a way to impress this board'),
('What would you do if you received unwanted pressure from an old acquaintance?', 'set a boundary and use my support plan', 'limit contact and ask for advice', 'leave the conversation before agreeing to anything', 'agree just to avoid an awkward moment', 'join in whatever they demand', 'claim I have no responsibility for my choices'),
('How would you show that you understand the effect of your actions on others?', 'explain the harm honestly without making excuses', 'describe what responsibility means in my daily choices', 'listen to feedback even when it is uncomfortable', 'focus only on how inconvenient the sentence was for me', 'say nobody else matters', 'claim that everyone deserved what happened'),
('What would you do if a planned living arrangement fell through?', 'contact housing support promptly and discuss lawful alternatives', 'review approved temporary options with my support worker', 'keep the responsible officer informed while I make a new plan', 'hide the change until someone asks', 'give up every release condition', 'say planning is pointless'),
('How would you handle social pressure to prove yourself after release?', 'make choices based on my goals rather than the audience', 'walk away from pressure and contact a trusted person', 'take time to consider the consequences', 'do whatever wins attention fastest', 'start a conflict to look powerful', 'say respect requires ignoring every rule'),
('What would you do when a personal goal takes longer than expected?', 'review the plan and keep working with realistic support', 'set a smaller measurable next step', 'ask what needs to change in my approach', 'drop the goal after one difficult day', 'take a harmful shortcut', 'blame anyone who has already succeeded'),
('How would you keep a disagreement from becoming a confrontation?', 'listen and ask for a pause before emotions escalate', 'use respectful language and clear boundaries', 'seek mediation when appropriate', 'try to embarrass the other person', 'threaten consequences until they agree', 'insist that every disagreement needs a winner'),
('What would you do if you did not understand one of your release conditions?', 'ask for clarification before making a decision', 'request a written explanation from the responsible officer', 'review it with an authorised support worker', 'guess and hope my interpretation is right', 'ignore the condition', 'decide that unclear rules never count'),
('How would you respond if someone questioned whether you had changed?', 'accept that trust takes time and show consistent behaviour', 'explain specific changes without demanding belief', 'continue following my plan even without praise', 'argue until they accept my version', 'threaten anyone who doubts me', 'say I only need to look changed for this hearing'),
('How would you maintain a constructive daily routine after release?', 'plan time for work appointments rest and support', 'use a simple schedule and review it regularly', 'start with a manageable routine and build on it', 'leave every day entirely to chance', 'avoid all responsibilities', 'say routines are only for other people'),
('What would you do if you needed professional support after release?', 'ask an appropriate service for help and attend agreed appointments', 'discuss a referral with my support worker', 'find out which services are available locally', 'wait for the problem to disappear without checking', 'refuse every form of help on principle', 'mock people who use support services'),
('How would you handle a promise that you realised you could not keep?', 'explain early and agree on a realistic alternative', 'take responsibility and discuss what I can actually do', 'ask for help reviewing the commitment', 'keep making the same promise without a plan', 'blame the other person for believing me', 'deny that I made any commitment'),
('What would you do to keep a setback from undoing your progress?', 'acknowledge it promptly and use my support plan', 'review what went wrong and take a safe next step', 'ask for help before the situation grows', 'hide everything until it becomes a crisis', 'use the setback as an excuse to repeat harmful behaviour', 'say one mistake means nothing matters anymore'),
]

# These are additional candidates in the existing scored answer pool, not a new
# hearing engine. Eighteen answers per question matches the original table's
# smallest populated answer count and avoids introducing empty option holes.
PAROLE_EXTRA = [
('I would explain a concrete plan rather than promise perfection',4),
('I would check the requirements with my support worker first',4),
('I would write down the steps and review them regularly',4),
('I would ask for help early if the plan stopped working',5),
('I would be honest about what I can and cannot manage',4),
('I would start with a realistic step I can actually follow',4),
('I would think about how my choices affect other people',5),
('I would discuss it calmly with the appropriate person',4),
('I would try to do better but have not made a clear plan yet',3),
('I would decide later without preparing anything',2),
('I would tell this board whatever it wants to hear',1),
('I would expect everyone else to deal with it',1),
]

INBOUND = [
('An inmate named <name> insists you give up your seat even though several other seats are empty.', 'An inmate tried to pressure me into giving up my seat.', '',''),
('An inmate named <name> interrupts your conversation and demands that everyone listen only to them.', 'An inmate tried to take over my conversation.', '',''),
('An inmate named <name> tells you that newcomers are not allowed to use the table you chose.', 'An inmate challenged where I was allowed to sit.', '',''),
('An inmate named <name> mocks an approved drawing you received from home and waits for an audience to laugh.', 'An inmate mocked a drawing I received from home.', '',''),
('An inmate named <name> says your quiet routine makes you an easy target and demands a reaction.', 'An inmate tried to provoke me about my quiet routine.', '',''),
('An inmate named <name> claims you promised a favour you do not remember agreeing to.', 'An inmate claimed I owed an unwanted favour.', '',''),
('An inmate named <name> loudly blames you for a missing shared item without offering any evidence.', 'An inmate blamed me for a missing item without evidence.', '',''),
('An inmate named <name> demands that you stop speaking to an inmate they dislike.', 'An inmate tried to control who I spoke to.', '',''),
('An inmate named <name> makes fun of your attempts to finish a course workbook.', 'An inmate mocked my education work.', '',''),
('An inmate named <name> pressures you to take sides in an argument that does not involve you.', 'An inmate pressured me to join an unrelated argument.', '',''),
('An inmate named <name> repeatedly talks over you when you try to explain a misunderstanding.', 'An inmate refused to let me explain a misunderstanding.', '',''),
('An inmate named <name> tells the group that your family letters are a source of amusement.', 'An inmate tried to embarrass me about my family letters.', '',''),
('An inmate named <name> threatens to make your work shift miserable unless you do their assigned task.', 'An inmate threatened me over a work assignment.', 'x',''),
('An inmate named <name> demands your next turn with the recreation equipment.', 'An inmate pressured me to surrender my recreation turn.', '',''),
('An inmate named <name> ridicules you for apologising after a disagreement.', 'An inmate mocked my attempt to apologise.', '',''),
('An inmate named <name> says they will spread a rumour unless you agree with their version of an argument.', 'An inmate threatened to spread a rumour about me.', 'x',''),
('An inmate named <name> accuses you of trying to impress staff because you volunteered in the library.', 'An inmate criticised my library volunteering.', '',''),
('An inmate named <name> orders you to leave an approved study group so their friend can take your place.', 'An inmate demanded my place in a study group.', '',''),
('An inmate named <name> jeers at a certificate you earned and tries to get others to join in.', 'An inmate jeered at my education certificate.', '',''),
('An inmate named <name> says you must publicly embarrass a newcomer to prove you belong.', 'An inmate pressured me to humiliate a newcomer.', '','x'),
]

OUTBOUND = [
('You tell <name> that you will decide who is allowed to sit at a shared table.', 'I tried to control who could sit at a shared table.', 'x',''),
('You demand that <name> give up the next turn with recreation equipment.', 'I demanded another inmate’s recreation turn.', '','x'),
('You mock <name> for asking for help with a course workbook.', 'I mocked an inmate for seeking help with education.', 'x',''),
('You tell <name> that finishing a rehabilitation programme is nothing to be proud of.', 'I dismissed an inmate’s rehabilitation achievement.', 'x',''),
('You pressure <name> to take your side in a disagreement they did not witness.', 'I pressured an inmate to support my account of a disagreement.', 'x',''),
('You demand that <name> do your cleaning assignment in addition to their own.', 'I demanded that an inmate take my cleaning assignment.', '','x'),
('You interrupt <name> and announce that their family letters are boring everyone.', 'I tried to embarrass an inmate about family letters.', 'x',''),
('You tell <name> that you will spread an embarrassing rumour unless they agree with you.', 'I threatened to spread a rumour about an inmate.', 'x',''),
('You insist that <name> apologise publicly for disagreeing with you in a yard game.', 'I demanded a public apology over a yard game.', '','x'),
('You accuse <name> of taking a missing shared item even though you have no evidence.', 'I accused an inmate of taking an item without evidence.', 'x',''),
('You demand that <name> leave an approved study group so your friend can take the place.', 'I demanded an inmate’s place in a study group.', '','x'),
('You mock <name> for trying to keep a calm daily routine.', 'I mocked an inmate’s calm routine.', 'x',''),
('You tell <name> that your preferences should decide the whole cell’s cleaning schedule.', 'I tried to dictate a shared cleaning schedule.', '','x'),
('You pressure <name> to stop speaking to an inmate you dislike.', 'I pressured an inmate to stop speaking to someone.', 'x',''),
('You call <name> weak for walking away from an argument.', 'I mocked an inmate for leaving an argument.', 'x',''),
('You demand that <name> stop using a shared shelf even though your belongings already fill most of it.', 'I demanded more than my share of shelf space.', '','x'),
('You tell <name> that you will make every shift difficult unless they accept your version of a dispute.', 'I threatened an inmate over a workplace dispute.', 'x',''),
('You jeer at <name> for volunteering to help a newcomer find approved support.', 'I jeered at an inmate for helping a newcomer.', 'x',''),
('You insist that <name> surrender an approved magazine because you want it more.', 'I demanded another inmate’s approved magazine.', '','x'),
('You encourage the group to laugh when <name> speaks about a realistic release plan.', 'I encouraged others to ridicule an inmate’s release plan.', 'x',''),
]

LETTERS = [
('All','described a quiet evening they wished you could have shared','',''),
('All','asked which book you were reading this week','',''),
('All','shared a small achievement from their everyday life','',''),
('All','said they kept a photograph ready for your next approved visit','',''),
('All','encouraged you to finish the course you had mentioned','',''),
('All','asked what kind of encouragement would help you most','',''),
('All','described the weather and the familiar streets near home','',''),
('All','said they were proud of the effort you were putting into a better routine','',''),
('All','asked you to tell them one thing you had learned recently','',''),
('All','shared a funny memory without pretending everything was easy','',''),
('All','explained why they had missed the last visit and hoped to arrange another','',''),
('All','said a younger relative had asked when they could send you a drawing','',''),
('All','described a family meal and said your usual seat made them think of you','',''),
('All','encouraged you to make realistic plans one step at a time','',''),
('All','asked whether your latest library book had lived up to its description','',''),
('All','said they had saved your last letter and read it more than once','',''),
('All','asked which approved items would be useful rather than impressive','',''),
('All','said they wanted your next conversation to focus on listening as well as talking','',''),
('All','shared a change at home and invited you to ask questions about it','',''),
('All','encouraged you to ask for support when a difficult week felt overwhelming','',''),
('All','said they could not promise an easy future but wanted you to keep trying','',''),
('All','asked you to write about a constructive goal for the next month','',''),
('All','described an ordinary moment that reminded them of a happier memory','',''),
('All','said they appreciated the respectful tone of your most recent letter','',''),
('Lover','said they wanted to rebuild trust through consistent honest conversations','50',''),
('Lover','described a simple outing they hoped you could share after release','50',''),
('Lover','asked you to respect the pace at which they felt comfortable reconnecting','30',''),
('Lover','said that meaningful promises mattered more than grand declarations','40',''),
('Lover','explained that they needed space but still wanted to communicate respectfully','','40'),
('Lover','asked you to listen to their worries without treating them as accusations','30',''),
]

# name, plural, some-article, lover-only, confiscation score
GIFTS = [
('annotated paperback novel','','','',1),('small approved sketchbook','','','',1),
('collection of family recipes','','','',1),('book of beginner drawing exercises','','','',1),
('printed photograph of a familiar street','','','',1),('handwritten poem about home','','','',1),
('approved pack of coloured pencils','','','',2),('blank writing journal','','','',1),
('packet of stationery','','','',1),('collection of crossword puzzles','','','',1),
('book of short local histories','','','',1),('printed family calendar','','','',1),
('pair of warm approved socks','','','',2),('book of language exercises','','','',1),
('bundle of encouraging postcards','x','x','',1),('collection of approved magazine clippings','','','',2),
('paper bookmark with a supportive message','','','',1),('printed copy of a favourite family photograph','','','',1),
('book of easy mental arithmetic exercises','','','',1),('approved packet of tea bags','','','',2),
('set of blank greeting cards','x','x','',1),('packet of approved drawing paper','','','',1),
('letter describing a shared happy memory','','','x',1),('handwritten anniversary poem','','','x',1),
('small book of poetry with personal notes','','','x',1),('book of nature photographs','','','',1),
('collection of word-search puzzles','','','',1),('approved notebook for study goals','','','',1),
]

JOBS = [
('library shelf organiser','organising the library shelves','$3','4'),
('book repair assistant','repairing approved library books','$3','3'),
('education materials assistant','sorting education materials','$3','4'),
('classroom setup assistant','preparing rooms for prison classes','$2','3'),
('laundry stock checker','checking approved laundry supplies','$3','4'),
('bedding inventory assistant','counting clean bedding supplies','$3','3'),
('meal tray sorter','sorting clean meal trays','$2','4'),
('kitchen inventory assistant','checking approved kitchen stock','$3','3'),
('recreation equipment assistant','organising recreation equipment','$3','3'),
('recreation room cleaner','cleaning approved recreation rooms','$2','4'),
('visitor room setup assistant','setting up the visiting room','$3','3'),
('approved stationery packer','packing approved stationery supplies','$3','3'),
('workshop checklist clerk','recording approved workshop checklists','$4','2'),
('garden seedling assistant','tending approved garden seedlings','$3','3'),
('compost area assistant','maintaining the approved compost area','$2','2'),
('linen folding assistant','folding clean linen','$2','4'),
('course workbook packer','packing course workbooks','$3','3'),
('library returns clerk','checking returned library books','$4','2'),
('cleaning supply organiser','organising approved cleaning supplies','$3','4'),
('programme room attendant','preparing rooms for supervised programmes','$3','3'),
('approved craft stock assistant','sorting approved craft materials','$3','2'),
('noticeboard assistant','updating approved prison noticeboards','$3','2'),
]

NICKNAMES = ['Paperback','Second Draft','Tin Whistle','Margin Note','Yardlight','Calendar Kid','Lunch Bell',
 'Quiet Corner','Early Shift','Night Reader','Spare Pencil','Dust Jacket','Fresh Page','Steady Hands',
 'Rain Check','Soft Step','Work Ledger','Top Shelf','Blue Bookmark','Long Letter','Last Chapter',
 'Common Room','Small Hours','Neat Fold','Yard Captain','Tea Break','Blank Slate','Clear Head',
 'Rota Keeper','Soft Spoken','Course Credit','Garden Row','Next Page','Study Hall','Paper Trail',
 'Clean Sweep','Morning Count','Back Cover','Steady Pace','Book Return','First Draft','Worn Spine']

def unique_candidates(candidates, existing, count, key):
    used={x.casefold() for x in existing}; result=[]
    for candidate in candidates:
        value=key(candidate).casefold()
        if value in used:continue
        used.add(value);result.append(candidate)
        if len(result)==count:return result
    raise ValueError('Not enough unique content candidates')

def author(original_path, output_path):
    original_path=Path(original_path)
    if original_path.suffix.lower()=='.apk':
        import zipfile
        import UnityPy
        from build_prison_expansion import BUNDLE, BASELINE_SHA256, EXPECTED_COUNTS, decode, records, sha_file
        assert sha_file(original_path)==BASELINE_SHA256,'Unsupported authoring baseline'
        with zipfile.ZipFile(original_path) as z:env=UnityPy.load(z.read(BUNDLE))
        originals={}
        for obj in env.objects:
            if obj.type.name!='TextAsset':continue
            asset=obj.read()
            if asset.m_Name in EXPECTED_COUNTS:
                assert asset.m_Name not in originals
                originals[asset.m_Name]=records(decode(asset.m_Script))
        assert set(originals)==set(EXPECTED_COUNTS)
    else:
        originals=json.loads(original_path.read_text())
    def values(name, column):
        rows=originals[name];i=rows[0].index(column);return [r[i] for r in rows[1:]]
    prefix='a16_'; content={}
    event_name=prefix+'dumb-scenarios-prison-enc'
    first=max(int(v) for v in values(event_name,'Index'))+1
    assert len(EVENTS)==80
    events=[]
    for index,(title,body,choices) in enumerate(EVENTS):
        row={'Index':str(first+index),'Hero Min Age':'18','Randomize Choices':'x',
             'Title':'Prison+: '+title,'Body':body,'CTA':'What will you do?'}
        for i,(choice,behaviour,respect) in enumerate(choices,1):
            row[f'Choice {i}']=choice
            row[f'Narrative {i}']=f'During {title.lower()}, I chose to {choice[0].lower()+choice[1:]}.'
            row[f'Behavior Impact {i}']=str(behaviour);row[f'Respect Impact {i}']=str(respect)
        events.append(row)
    content[event_name]=events
    parole=[]
    for question,*answers in PAROLE:
        row={'Commonness':'4','Question':question,'CTA':'How will you respond?'}
        choices=list(zip(answers,[5,4,3,2,1,1]))+PAROLE_EXTRA
        assert len(choices)==18
        for i,(answer,score) in enumerate(choices,1):row[f'Choice {i}']=answer;row[f'Choice {i} Score']=str(score)
        parole.append(row)
    content[prefix+'prison-parole-questions-enc']=parole
    content[prefix+'prison-bully-inbound-scenarios-enc']=[{'Scenario':s,'Log Version':log,'Bully Action':b,'Hero Action':h} for s,log,b,h in INBOUND]
    content[prefix+'prison-bully-outbound-scenarios-enc']=[{'Scenario':s,'Log Version':log,'Will Do':d,'Will Let':l} for s,log,d,l in OUTBOUND]
    content[prefix+'prison-letters-enc']=[{'Audience':a,'Topic':topic,'Min Relationship Strength':lo,'Max Relationship Strength':hi} for a,topic,lo,hi in LETTERS]
    gifts=unique_candidates(GIFTS,values(prefix+'prison-gifts-enc','Name'),25,lambda x:x[0])
    content[prefix+'prison-gifts-enc']=[{'Name':name,'Is Plural':plural,'Use Some Article':some,'From Lover Only':lover,'Confiscate Score':str(score)} for name,plural,some,lover,score in gifts]
    jobs=unique_candidates(JOBS,values(prefix+'prison-jobs-enc','Job'),20,lambda x:x[0])
    content[prefix+'prison-jobs-enc']=[{'Job':job,'Description':description,'Daily Rate':rate,'Commonness Score':common} for job,description,rate,common in jobs]
    nicknames=unique_candidates(NICKNAMES,values(prefix+'prison-nicknames-enc','Nickname'),30,lambda x:x)
    content[prefix+'prison-nicknames-enc']=[{'Nickname':name,'Gender':'both'} for name in nicknames]
    assert [len(content[k]) for k in content]==[80,25,20,20,30,25,20,30]
    assert sum(map(len,content.values()))==250
    Path(output_path).write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:len(v) for k,v in content.items()},indent=2))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('original_tables');p.add_argument('--out',default=str(Path(__file__).with_name('prison_content.json')))
    a=p.parse_args();author(a.original_tables,a.out)
