# Last Siege

## Info
Last Siege is a side-scrolling shooter in the style of the classic 80s and 90s arcade machine shooters. This project was entirely written in PyGame, a game engine designed for Python 3.x.

## Controls
- W or Up Arrow - Jump
- A or Left Arrow - Walk Left
- D or Right Arrow - Walk Right
- F - Fire
- Q - Throw Grenade
- V - Switch firing modes (Alters between Semi [1 bullet], Burst [3 bullets] or Automatic [Constant])

## Latest Update
- Added heavy optimisations
- Added day-night cycles to levels
- Added 2 new levels
- Added new tiles
- Added a dedicated controls menu so they are easier to find
- Changed individual ammo and grenade blitting to just numbers. This improves performance and a better indicator of ammo count when the player gets a lot of ammo
- Enemy AI does not work if they are off screen
- Dead enemies now disappear when they go off screen
- Gravity Physics and screen-blitting is performed with seperate threads.

## Latest Hotfix
- Fixed bug where player's current health becomes the new maximum health on level change
- Fixed bug where health, ammo and grenades would not transition over into new levels
- Fixed a bug where player could get double health from health-box
- Fixed a bug where player could get double health on level change
- Added a testing framework for testing purposes only
    - _Currently only has a debugging tool, but will be updated in the future with more options_

## User Feedback
### User Feedback 1
#### Suggestions
* No navigation between the achievements menu and the main menu
* Controls are not well ergonoically designed.
    * Interaction Controls clash with Movement Controls
    * Consider designing controls around two hands instead of one
* 'How to Play' description is not noticable without being made aware of it from someone else
* Escape button should not close the program
#### Developer Response
* Navigation between achievements menu and main menu is now possible
* Controls have been restructured
* A Controls menu button will be added
* Escape functionality has been deprecated

