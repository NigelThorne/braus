## NOTES: -- Hi Nigel here... 

I change this awesome tool to make it match my needs.. 
My use case it that I have multiple Chrome profiles, one for work and one for home. 
When clicking links, in slack for example, I keep getting the wrong browser opening. 

I have therefore added the following abilities: 
* Allow you to pick a specific chrome profile you want to open the link in. (in linux only .. sorry)
* Open in that browser just once, or always automatically from now on.

I also added an odd idea
* If you edit the config (~/.brausrc) and add "redirect=www.somedomain.com" to a domain... then it will launch the redirected domain instead of the one you clicked.  I'm not sure if this will be useful. 



------------


## Braus
A small application to select a browser every time you click a link anywhere. This is especially useful if you have multiple browsers or profiles, and you want to be able to open certain links in certain browsers. Very useful for web developers, but also for a lot of other people.

````
## This is unmaintained for now, since I don't have time from other life stuff. 
## Please feel free to fork and publish under a different name.
````


GNU/Linux alternative to apps such as Choosy/Browserchooser


A package is available for Archlinux [in the AUR](https://aur.archlinux.org/packages/braus-git/)

If you wish to package the app for your distro, please open an issue and we'll work on it together.

#### Build instructions
````
meson build --prefix=/usr
cd build
ninja
ninja install

````

When you run braus for the first time, it will ask you whether you want to set it as your default browser. Ideally you should make it default to actually get the benefit of an app like this.

---------------

© 2020 Kavya Gokul

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
