Rdio Quick Sync
=============

Rdio Quick Sync is an interactive command line utility for syncing albums from Rdio.

## Features
* Page through all your albums and select / deselect what you'd like synced to your mobile device.
* Filter based on a search string.
* Add all or clear all synced music with one command.
* Sort your albums by album name or artist name.
* See how many total albums you have synced to your mobile device.

## Important note
This is "BYO authkeys". You must follow the instructions at the top of rdio_consumer_credentials_EXAMPLE.py for this program to work.

## Example
	0. [ ] The Antlers - Familiars
	1. [ ] Allah-Las - Worship The Sun
	2. [ ] Laura Marling - Short Movie
	3. [ ] Flying Colors - Flying Colors
	4. [ ] Flying Colors - Mask Machine
	5. [ ] Trombone Shorty - Backatown
	6. [ ] The Dears - No Cities Left
	7. [ ] Andrew Bird - Things Are Really Great Here, Sort Of...
	8. [ ] The Bee Eaters - The Bee Eaters
	9. [x] Brittany Haas - Brittany Haas
	10. [x] Elephant Revival - These Changing Skies
	11. [x] The Deadly Gentlemen - Roll Me, Tumble Me
	12. [x] Laura Marling - Once I Was an Eagle
	13. [ ] Chick Corea - The Best Of Chick Corea
	14. [ ] Galactic - Ya-Ka-May
	15. [ ] Rudolf Serkin, London Symphony Orchestra, Claudio Abbado - Mozart: Piano Concertos Nos.23 & 24
	16. [x] Comanchero - The Undeserved
	17. [x] Lo-Fi Resistance - A Deep Breath
	18. [ ] Genesis - Calling All Stations
	19. [x] Clones of Clones - I Don't Need Your Love - Single
	20. [ ] The Kinks - Muswell Hillbillies
	21. [ ] Foo Fighters - Sonic Highways
	22. [ ] Pink Floyd - The Endless River
	23. [ ] The Budos Band - Burnt Offering
	24. [ ] Pink Floyd - A Saucerful Of Secrets [2011 - Remaster] (2011 Remastered Version)
	25. [ ] Snarky Puppy - We Like It Here
	26. [ ] Snarky Puppy - groundUP
	27. [ ] Stars - The North
	28. [ ] Ataxia - Automatic Writing
	29. [ ] Ataxia - The No.6
	30. [ ] The Flaming Lips - With A Little Help From My Fwends
	31. [ ] The Reign Of Kindo - Rhythm, Chord & Melody
	32. [ ] Beach House - Teen Dream
	33. [ ] Montreal Guitar Trio - Der Prinz
	34. [ ] Foo Fighters - Something From Nothing
	35. [ ] Enchant - The Great Divide
	36. [ ] Brand X - Unorthodox Behaviour
	37. [x] Genesis - Three Sides Live
	38. [ ] Genesis - We Can't Dance
	39. [ ] Genesis - Invisible Touch
	40. [ ] Phil Collins - Face Value
	41. [ ] Todd Terje - It's Album Time
	42. [ ] Slow Six - Tomorrow Becomes You
	43. [x] Bleachers - Strange Desire
	44. [ ] Weezer - Everything Will Be Alright In The End
	45. [ ] Collective Soul - Collective Soul [Deluxe Edition]
	46. [x] Collective Soul - Hints, Allegations & Things Left Unsaid
	47. [ ] Collective Soul - Dosage
	48. [ ] Collective Soul - Collective Soul
	49. [ ] Marco Benevento - Swift
	Showing 0-50 of 533. Albums Synced: 130.
	Toggle Album. Or ['(a)ll', '(c)lear', '(n)ext', '(p)rev', '(f)ilter', '(s)ort', 'sync'] --> 

## Commandline Options
	    usage: sync.py [-h] [--fetch_token] [--fake]
	    
	    Interactive command line interface for syncing music from Rdio.
	    
	    optional arguments:
	      -h, --help     show this help message and exit
	      --fetch_token  Fetch a fresh OAuth token. If not provided, will expect TOKEN
	          to be defined in rdio_consumer_credentials.py
	      --fake         Use a fake set of albums. (For testing only)
