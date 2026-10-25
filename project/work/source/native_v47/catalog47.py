"""Persisted social threads: bounded history, simulated NPCs and reply choices."""
HISTORY = 24
COMMENTS = 18
OWNER = 'comments47'
PREFIX = 'scenario.activitiesV18.comments47_'
PLATFORMS = ['Discord','Reddit','Facebook','Instagram','TikTok','Twitter','YouTube','Twitch','OnlyFans','SoundCloud']
LAUNCH = [2015,2005,2004,2010,2016,2006,2005,2011,2016,2007]
USERNAMES = ['OrbitOwl','PixelNomad','MidnightMaple','SunnySideUp','QuietComet','VelvetFox','RiverEcho','PaperKite','BlueLantern','CedarSky','CosmicToast','SilverFern','AmberAtlas','CloudSketch','MossAndMoon','NeonOtter','LittleSatellite','CopperRobin','WildflowerWave','MarbleMoth','PeachPlanet','NorthStarling','LemonCircuit','IndigoInk']
REACTIONS = [
 ['This made my day.','Glad you shared this!','I was wondering when you would post again.','What happened next?','I see it a little differently, but I get your point.','More updates like this, please.'],
 ['Great photo!','The lighting looks so good here.','This belongs in a photo album.','Where did you take this?','I would have framed this a bit differently.','Love seeing these moments.'],
 ['That was a great play!','What settings are you using?','I need to try this in my next game.','Can you explain that strategy?','I would have taken a different route there.','Part two when?'],
 ['This sounds amazing.','The melody is stuck in my head now.','Please share the full version.','How long did this take to make?','I liked the earlier version too.','Adding this to my playlist.'],
 ['That explanation finally made it click.','Saving this for later.','Could you show another example?','This is actually useful.','Can you share where you learned this?','A follow-up tutorial would be great.'],
 ['That looks delicious!','Recipe, please!','I am trying this at the weekend.','What would you substitute for the main ingredient?','I would add a little more seasoning.','Now I am hungry.'],
 ['Interesting perspective.','What made you think about this?','I agree with part of what you said.','There is another side to this too.','Could you share a source or example?','Thanks for explaining your view.'],
 ['Proud of the progress you are making.','Good luck with everything!','I can relate to this so much.','How did it go in the end?','Take a break when you need one.','Keep us updated.'],
 ['Consistency is paying off!','What does your routine look like?','That is a solid effort.','How long have you been training?','Rest days matter too.','This motivated me to get moving.'],
 ['The detail in this is so good.','I love seeing the process.','How did you come up with the idea?','Would you show the next stage?','I would try a different colour next time.','You should keep making these.'],
 ['Glad I caught this stream.','The chat was fun today.','When are you going live again?','Could you cover this next time?','I joined late. Is there a replay?','Thanks for spending time with the community.'],
]
TOPICS = {
 1:['selfie','family photo','travel photo','story','fashion','Beauty','haul'],
 2:['gaming','BitLife','League of Legends','Minecraft','Pokemon','Fortnite','Call of Duty','World of Warcraft','Dead by Daylight','Among Us','date simulation'],
 3:['studio tour','song breakdown','beat challenge','mix comparison','songwriting diary','acoustic session','production tutorial','release countdown','collaboration preview'],
 4:['educational','how-to','tutorial','revision tips','fact check'],
 5:['food photo','Cooking','cooking budget'],
 6:['blog','political','poll','social justice','product review','reality TV recap'],
 7:['study vlog','school project','club showcase','career diary','budget diary','motivational','motivational quote'],
 8:['fitness','fitness progress','sports analysis','race analysis'],
 9:['dance','challenge','skit','portfolio review','desk setup','behind the scenes','digital art timelapse','community spotlight'],
 10:['livestream','Just chatting','quiet livestream','charity livestream','fan questions','ASMR','sensual ASMR'],
}
REPLIES = ['Thanks for the support!','Here is a little more context about my post.','I see your point, even though I disagree.']
FOLLOWUPS = ['Of course! Keep the updates coming.','Thanks for explaining. That helps.','Fair enough. Thanks for hearing me out.']
def scene(n):return PREFIX+str(n).zfill(3)
def key(slot,comment,field):return f'P{slot}C{comment}{field}'
def fnv(s):
 n=2166136261
 for c in s:n=((n^ord(c))*16777619)&0xffffffff
 return n
