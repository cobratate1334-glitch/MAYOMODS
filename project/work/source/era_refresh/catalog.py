"""Curated supplied art and game retail dates. IDs and owned items stay stable."""
from connected_life.era_catalog import ERAS as PREVIOUS_ERAS

ERAS=[(1800,'1800 · A new century','1800'),(1820,'1820 · Steam age','1820'),
 (1840,'1840 · Industry and change','1840'),(1860,'1860 · Railways and reform','1860'),
 (1880,'1880 · Electric age','1880')]+PREVIOUS_ERAS

# Boundaries select a curated shop, rather than exposing every later object.
# Symbols refer to individual PNGs, never guessed positions on a sheet.
EPOCHS=[(1800,'1800s','1900s/one_room_schoolhouse','school/old_chalkboard','1920s/fountain_pen','1900s/western_fiddle','school/event_pictures/1900s_frontier_school.png'),
 (1900,'Early 1900s','1900s/one_room_schoolhouse','school/old_chalkboard','1920s/fountain_pen','1920s/film_camera','school/event_pictures/1900s_frontier_school.png'),
 (1920,'1920s','school/library_shelves','school/classroom_desk','1920s/fountain_pen','1920s/film_camera','school/event_pictures/1920s_school_library.png'),
 (1940,'1940s','school/old_chalkboard','school/classroom_desk','1940s/family_letter','1940s/home_garden_tools','school/event_pictures/1940s_school_garden.png'),
 (1960,'1960s','school/classroom_whiteboard','school/classroom_desk','school/pop_quiz','1960s/backyard_telescope','school/event_pictures/1960s_school_dance.png'),
 (1980,'1980s','1980s/home_computer','school/classroom_whiteboard','1980s/pocket_calculator','1980s/floppy_disks','school/event_pictures/1980s_computer_lab.png'),
 (2000,'2000s','2000s/suburban_school','school/classroom_whiteboard','2000s/desktop_pc','2000s/compact_digital_camera','school/event_pictures/2000s_school_trip.png'),
 (2010,'2010s','2010s/tablet_computer','school/study_planner','2010s/tablet_computer','2010s/action_camera','school/event_pictures/2010s_group_project.png'),
 (2020,'2020s','2020s/video_call_laptop','school/study_planner','2020s/video_call_laptop','2020s/hd_webcam','school/event_pictures/2020s_online_lesson.png'),
 (2026,'2026','school/robotics_club','school/study_planner','2026/folding_keyboard','school/robotics_club','school/event_pictures/2026_robotics_fair.png')]

# key, label, first year, last shop year, cost, minimum age, image, use text
ITEMS=[
 ('lamp','Oil lamp',1800,1909,6,12,'1900s/oil_lantern','You read by lamplight. You finish a chapter and unwind.'),
 ('watch','Pocket watch',1800,1929,25,12,'1900s/pocket_watch','You practise keeping time. You arrive early for your plans.'),
 ('fiddle','Fiddle',1800,1909,30,8,'1900s/western_fiddle','You learn a tune. Someone at home asks to hear it again.'),
 ('telegraph','Telegraph set',1844,1929,120,16,'1900s/telegraph_machine','You practise a short message. A friend replies to your note.'),
 ('writer','Typewriter',1874,1989,100,12,'1920s/typewriter','You type a letter. You feel proud of the finished page.'),
 ('gramophone','Gramophone',1895,1949,75,12,'1920s/gramophone','You play a record. The room fills with music.'),
 ('film','Film camera',1900,1969,55,12,'1920s/film_camera','You take a few family pictures. You keep the prints in an album.'),
 ('phone','Desk telephone',1900,1949,90,16,'1920s/candlestick_phone','You call a friend. It is good to hear their voice.'),
 ('radio','Table radio',1920,1959,75,10,'1940s/valve_radio','You tune in to a broadcast. Music and news fill the evening.'),
 ('rotary','Rotary telephone',1930,1989,85,16,'1940s/rotary_phone','You ring a relative. You catch up on family news.'),
 ('box_camera','Box camera',1930,1959,30,10,'1940s/box_camera','You photograph a family outing. You look forward to the prints.'),
 ('tv','Television',1955,1989,250,12,'1960s/box_television','You watch a programme with your family. You talk about it afterwards.'),
 ('transistor','Transistor radio',1954,1979,40,10,'1960s/transistor_radio','You listen outdoors. Your favourite song comes on.'),
 ('records','Record player',1960,1989,85,10,'1960s/record_player','You put on a record and relax.'),
 ('cassette','Cassette player',1979,1999,65,10,'1980s/cassette_player','You make a mix tape for a friend. They like your choices.'),
 ('computer','Home computer',1981,1999,1300,12,'1980s/home_computer','You write a small programme. It finally works.'),
 ('brick','Mobile phone',1983,1999,600,16,'1980s/brick_phone','You make a call while away from home.'),
 ('flip','Flip phone',1996,2009,150,13,'2000s/flip_phone','You text a friend and arrange to meet.'),
 ('mp3','MP3 player',1998,2009,90,10,'2000s/mp3_player','You load a playlist and go for a walk.'),
 ('handheld','Handheld console',2001,2009,120,8,'2000s/handheld_console','You beat a tricky level and tell a friend.'),
 ('smartphone','Smartphone',2007,2019,699,13,'2010s/touchscreen_phone','You take photos and call a friend. Online activities keep their own year limits.'),
 ('tablet','Tablet',2010,2019,350,12,'2010s/tablet_computer','You sketch an idea and learn something new.'),
 ('camera','Action camera',2013,2019,200,13,'2010s/action_camera','You film an outing and save the highlights.'),
 ('laptop','Video-call laptop',2020,2025,850,12,'2020s/video_call_laptop','You join a call with a relative. You enjoy catching up.'),
 ('earbuds','Wireless earbuds',2020,2025,120,12,'2020s/wireless_earbuds','You listen to your favourite album on a walk.'),
 ('console','Portable console',2020,2025,300,8,'2020s/portable_game_console','You play a game and unwind.'),
 ('folding','Folding phone',2026,3999,950,13,'2026/folding_phone','You photograph an outing and share the pictures with a friend.'),
 ('projector','Portable projector',2026,3999,350,12,'2026/portable_projector','You host a film night. Everyone stays for the ending.'),
 ('maker','Small 3D printer',2026,3999,450,16,'2026/small_3d_printer','You print a small model. You are pleased with how it turns out.')]

def path(key):return 'native1118/'+key
def epoch(year):return next(row for row in reversed(EPOCHS)if year>=row[0]) if year>=1800 else EPOCHS[0]
