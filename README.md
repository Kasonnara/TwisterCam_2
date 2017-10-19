TwistCam
=====================

### Setup:

- install required python3 modules: <br>
  - `PyQt4` for main game application. <br>
  - `matplotlib` and `numpy` if you want to use silhouette_generator.  

> I recommend to make a python virtual env.

- Generate some silhouettes for the game. Cf silhouette_generator folder.

> TVn7 require `1080x720 i50` video format: for set your output 
you can use `xrandr` (hard, and I can't give you the exact command) 
or `lxrandr` which is a graphical interface for setuping this two 
parameters and placing your screen on the right.

> You can also use arandr  to make sure your output is virtually located 
on the right of your main screen but notice that arandr reset lxrandr 
configurations and vice versa.

> If you use multiple desktop, it's a good idea to tell the game window 
to be displayed on all desktops to avoid miss manipulations.

### Usage, Game:

- Set config file : `TwistCamConf.py`, default configuration is for 2 players, 
another configuration file is committed for 1 player (TwistCamConf(1player).py).

> If the game does not scale well on screen, it may be 'screen_id' value which 
define the index of the screen to use, which may change from a computer to another. 
If it doesn't solve then try changing '*_proportions' configs.

- Into your shell run `python3 Main_TwisterCam_2.py` 
(you can eventually add 'dev_mode_g', 'dev_mode_c' or 'dev_mode' as 
parameter to get debug information about respectively graphical 
components, core components or both).

- Then custom shell starts, help can give main commands, (some may be broken 
with recent changes), the most important is `play` which setup a new game.

- When in game mode, select the game window (should be automatic) which 
automatically move on the right screen (which should be TVn7 screen) and 
wait that TVn7 put the game on screen. As soon as TVn7 show the game, 
hit `p` key and the game starts. Then when a player match his shadow hit 
the corresponding keys defined in configuration file (default : 1->`a`, 
2->`space`, 3->`enter`, 4->`+`).

- When the game is finished enter `exit` in the game console to end 
the current game and eventually restart a new one with `play`.

> When the game is running, if necessary you can enter `stop` to 
stop the game immediately.

> At any moment hitting `esc` key will stop the whole application.

### Usage, Silhouette generator:

To generate manually a silhouette:

- open silhouette_generator/main_manuel.py
- set angle values as you wish.
- run `python3 silhouette_generator/main_manuel.py`
- follow printed instruction to validate the preview.

To generate automatically some silhouettes:

- run `python3 silhouette_generator/main_random.py`
- follow printed instruction to validate which generated images 
should be kept.

All output images are stored in 'silhouette_generator/generation_random/'

To use then in the main program copy them into 'ressources/silhouette_storage/ ' 
directory, then run the main program once to generate associated 
config files in 'ressources/pose_configs/ '. 

You can eventually customise these configuration files. 

### TODO

- [X] Implement graphical interface V2.

- [X] Add multi-player mode.

- [ ] Add color feedback animation for player.

- [ ] Add Intro and outro video clip.

- [ ] Patch end of game bugs.

- [ ] Patch graphical bugs.

- [ ] Patch validation bug.

- [ ] Add remote control (nc or what ever) instead of key hitting in 
game mode.

- [ ] Remove custom configurations system and custom shell system.

- [X] Add a default set of silhouettes.

- [ ] Add not random pose selection and on the fly pose selection.

- [ ] Add interactive poses.
