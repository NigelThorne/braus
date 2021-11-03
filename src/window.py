# window.py
#
# Copyright 2020 Kavya Gokul
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gio, GLib, Pango, Gdk, GdkPixbuf
import sys
import configparser
import os
import glob
import json
from urllib.parse import urlparse

class BrausWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'BrausWindow'

    def __init__(self, app):
        super().__init__(title="Braus", application=app)
        

        self.thisapp = app
        self.loadConfig(None)
        try:
            self.url = sys.argv[1]
            print("Url %s" % self.url)
            self.rememberChoice = self.get_setting_value(self.url, 'keepasking', 'false').lower() != 'true'
        except IndexError:
            print("No url provided")
            self.rememberChoice = True

        # Set it to open in center
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        # Set to not be resizable
        self.set_resizable(False)

        settings = Gtk.Settings.get_default()
        settings.set_property('gtk-application-prefer-dark-theme', True)

        # Putting some css in a string
        css = b"""
        * {
        }
        decoration {
            border: 1px solid rgba(0,0,0,0.8);
            box-shadow: none;
            outline: none;
        }
        window.background.csd {
            background: none;
            background-color: rgba(20,20,20,0.95);
            border: none;
        }
        #headerbar {
            background: none;
            background-color: rgba(20,20,20,0.95);
            box-shadow: none;
            border: none;
            padding: 5px 10px 0;
            border-bottom: 1px solid rgba(0,0,0,0.5);
        }
        #headerbar entry {
            background: rgba(0,0,0,0.4);
            color: #ffffff;
            font-size: 0.6em;
            border-radius: 10px;
            border: 1px solid rgba(0,0,0, 0.4);
            outline: none;
            margin:10px 0;
        }
        #headerbar entry:focus {
            border: 1px solid rgba(255,255,255, 0.4);
            outline: none;
            box-shadow: none;
        }

        button decoration {
            border-radius: initial;
            border: initial;
        }

        #mainbox {
            background: none;
            padding: 10px;
        }

        #mainbox button {
            background: none;
            border: 1px solid rgba(255,255,255, 0.4);
            padding: 18px 12px;
            font-size: 0.6rem;
        }
        #mainbox button:hover {
            background-color: rgba(255,255,255,0.1);
        }

        #browsericon {
            margin-bottom: 6px;
        }
        """
        # Applying the custom css to the app
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        #Create headerbar and add to window as titlebar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.set_name("headerbar")
        hb.props.title = ""
        self.set_titlebar(hb)

        Gtk.StyleContext.add_class(hb.get_style_context(), Gtk.STYLE_CLASS_FLAT)

        # Create a entry, put the url argument in the entry, and add to headerbar
        entry = Gtk.Entry()
        entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "system-search-symbolic")
        try:
            entry.set_text(sys.argv[1])
            print("Url %s" % sys.argv[1])
        except IndexError:
            print("No url provided")

        entry.set_width_chars(35)
        hb.add(entry)

        # Create an options button
        optionsbutton = Gtk.MenuButton.new()
        try:
            optionsbutton.add(Gtk.Image.new_from_icon_name('settings-symbolic', Gtk.IconSize.LARGE_TOOLBAR))
        except:
            optionsbutton.add(Gtk.Image.new_from_icon_name('preferences-system', Gtk.IconSize.LARGE_TOOLBAR))
        hb.pack_end(optionsbutton)

        optionsmenu = Gtk.Menu.new()
        optionsmenu.set_name("optionsmenu")
        optionsbutton.set_popup(optionsmenu)

        aboutmenuitem = Gtk.MenuItem.new()
        aboutmenuitem.set_label("About")
        aboutmenuitem.connect("activate", app.on_about)
        optionsmenu.append(aboutmenuitem)

        quitmenuitem = Gtk.MenuItem.new()
        quitmenuitem.set_label("Quit")
        quitmenuitem.connect("activate", self.quitApp, app)
        optionsmenu.append(quitmenuitem)

        optionsmenu.show_all()

        # outerbox
        outerbox = Gtk.Box()
        outerbox.set_orientation(Gtk.Orientation.VERTICAL)

        self.add(outerbox)

        # create a horizontal box to hold browser buttons
        hbox = Gtk.Box()
        hbox.set_name("mainbox")
        hbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        hbox.set_spacing(10)
        hbox.set_homogeneous(True)

        outerbox.add(hbox)
        outerbox.add(self.add_alwaysbar())

                
        if (app.settings.get_boolean("ask-default") != False) and (self.is_default_already() == False) :
            infobar = self.add_infobar(app)
            outerbox.add(infobar)

        # Get all apps which are registered as browsers
        browsers = Gio.AppInfo.get_all_for_type(app.content_types[1])

        # The Gio.AppInfo.launch_uris method takes a list object, so let's make a list and put our url in there
        url = entry.get_text()

        # Loop over the apps in the list of browsers
        for browser in browsers:

            # Remove Braus from the list of browsers
            if self.is_braus(browser) :
                continue

            #put the current one in the loop, in a dict
            display_name = browser.get_display_name()

            # Add our button to the horizontal box we made earlier
            self.add_launcher(url, browser, display_name, hbox)
            if( self.is_chrome(browser) ):
                for (name, profile) in self.list_chrome_profiles():
                    self.add_launcher(url, browser, name, hbox, profile)

    def add_alwaysbar(self):
        alwaysbar = Gtk.Box()
        alwaysbar.set_orientation(Gtk.Orientation.HORIZONTAL)
        alwaysbar.set_spacing(10)

        #alwaysbar.set_show_close_button(True)
        # alwaysbar.connect("response", self.on_infobar_response, app)

        alwaysLabel = Gtk.Label("---")
        self.set_remember_choice(None, self.rememberChoice, alwaysLabel)

        # content = alwaysbar.get_content_area()
        alwaysbar.add(alwaysLabel)

        onceButton = Gtk.Button.new_with_label(_("Once"))
        onceButton.connect("clicked", self.set_remember_choice, False, alwaysLabel)
        alwaysbar.add(onceButton)
        
        alwaysButton = Gtk.Button.new_with_label(_("Always"))
        alwaysButton.connect("clicked", self.set_remember_choice, True, alwaysLabel)
        alwaysbar.add(alwaysButton)

        return alwaysbar

    def set_remember_choice(self, button, value, label):
        if(value == True):
            label.set_label("Remember this answer. ")
        else:
            label.set_label("Ask again next time.  ")
        self.rememberChoice = value

    def add_infobar(self, app):
        # Create an infobar to help the user set Braus as default
        infobar = Gtk.InfoBar()
        infobar.set_message_type(Gtk.MessageType.QUESTION)
        infobar.set_show_close_button(True)
        infobar.connect("response", self.on_infobar_response, app)

        infolabel = Gtk.Label("Set Braus as your default browser")
        content = infobar.get_content_area()
        content.add(infolabel)

        infobuttonnever = Gtk.Button.new_with_label(_("Never ask again"))
        Gtk.StyleContext.add_class(infobuttonnever.get_style_context(), Gtk.STYLE_CLASS_FLAT)
        
        infobar.add_action_widget(infobuttonnever, Gtk.ResponseType.REJECT)
        infobar.add_button (_("Set as Default"), Gtk.ResponseType.ACCEPT)
        return infobar

    def mapped_url(self, url):
        domain = urlparse(url).netloc
        setting = self._getValue(domain)
        if(setting != None ):
            redirect = setting.get("redirect", None) 
            if(redirect != None):
                return url.replace(domain, redirect)
        return url

    def is_saved_action(self, url, browser, profile):
        setting = self.get_setting(url)
        if(setting == None): 
            return False
        if(setting.get('keepasking', '').lower() == 'true'):
            return False    
        return setting.get('profile',None) == profile and \
                setting['browserId'] == browser.get_id()

    def get_setting_value(self, url, key, default):
        domain = urlparse(url).netloc
        setting = self._getValue(domain)
        if(setting is None): return default
        return setting.get(key, default)


    def get_setting(self, url):
        domain = urlparse(url).netloc
        return self._getValue(domain)


    # linux only
    def list_chrome_profiles(self):
        profiles= list(map(
            self.read_chrome_preference, 
            glob.glob(
                os.path.join(
                    os.path.expanduser("~"),".config","google-chrome", "*", "Preferences"))))
        print(profiles)
        return profiles

    def chrome_profile_image_filename(self, profile):
        if (profile == None):
            return None
        found = glob.glob(os.path.join(os.path.expanduser("~"),
            ".config","google-chrome", profile , "Accounts", "Avatar Images", "*"))
        return (found or [None])[0]

    def read_chrome_preference(self, file):
        prefs = json.load(open(file,))
        return (prefs['profile']['name'], file.split("/")[-2])

    def is_chrome(self, browser):
        return browser.get_display_name() == "Google Chrome"

    def add_launcher(self, url, browser, display_name, hbox, profile=None):
        if(self.is_saved_action(url,browser,profile)):
            self.launch_browser(None, browser, url, profile)

        icon = self.get_icon(browser, profile)
        label= Gtk.Label.new(display_name)
        label.set_max_width_chars(10)
        label.set_width_chars(10)
        label.set_line_wrap(True)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_justify(Gtk.Justification.LEFT)

        #Every button has a vertical Gtk.Box inside
        vbox = Gtk.Box()
        vbox.set_orientation(Gtk.Orientation.VERTICAL)
        vbox.set_spacing(0)

        vbox.pack_start(icon,True, True, 0)
        vbox.pack_start(label,True, True, 0)

        button = Gtk.Button()

        button.add(vbox)

        hbox.pack_end(button, True, True, 0)
        #Connect the click signal, passing on all relevant data(browser and url)
        button.connect("clicked", self.update_config_and_launch, browser, url, profile)
        return button

    @property
    def app_id(self):
        return Gio.Application.get_application_id(self.thisapp) + '.desktop'

    def is_braus(self, browser):
        return self.app_id == browser.get_id() 

    def is_default_already(self):
        default = Gio.AppInfo.get_default_for_type(self.thisapp.content_types[1], True)
        print(str(default))
        return self.is_braus(default)

    def get_icon(self, browser, profile):

        #Get the icon and label, and put them in a button
        try:
            icon = Gtk.Image.new_from_gicon(browser.get_icon(), Gtk.IconSize.DIALOG)
        except:
            icon = Gtk.Image.new_from_icon_name('applications-internet', Gtk.IconSize.DIALOG)

        file = self.chrome_profile_image_filename(profile)
        if(file != None): 
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=file, 
                width=48, 
                height=48, 
                preserve_aspect_ratio=True)
            print("Image file: %s" % file)
            icon = Gtk.Image.new_from_pixbuf(pixbuf)

        icon.set_name("browsericon")
        return icon

    def update_config_and_launch(self, button, browser, url, profile):
        if(self.rememberChoice == True):
            self._updateConfig(url, browser, profile)
        else:
            self._updateConfigToKeepAsking(url)
        self.launch_browser(button, browser, url, profile)

    # Function to actually launch the browser
    def launch_browser(self, button, browser, url, profile):
        uris = [self.mapped_url(url)]
        if(profile != None):
            uris.append("--profile-directory="+profile)

        if(self.is_chrome(browser)):
            uris.append("--disable-infobars")
            
        browser.launch_uris(uris)
        print("Opening " + browser.get_display_name())
        self.quitApp(self,self.thisapp)

    # Quit app action
    def quitApp(self, *args):
        app = args[1]
        print("Bye…")
        app.quit()

    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        about_dialog.present()

    def on_infobar_response(self, infobar, response_id, app):
        infobar.hide()
        appinfo = Gio.DesktopAppInfo.new(self.app_id)

        if response_id == Gtk.ResponseType.ACCEPT:
            #set as default
            try:
                #loop through content types, and set Braus as default for those
                for content_type in app.content_types:
                    appinfo.set_as_default_for_type(content_type)

            except GLib.Error:
                print("error")
        
        elif response_id == Gtk.ResponseType.REJECT:
            #don't ask again
            app.settings.set_boolean("ask-default", False)

    def getConfigFile(self):
        try:
            from gi.repository import GLib
            configdirs = [GLib.get_user_config_dir()] + GLib.get_system_config_dirs()
            for configdir in configdirs:
                config = os.path.join(configdir, 'braus', 'braus.ini')
                print("Looking for configuration file %s" % config)
                if os.path.exists(config):
                    break
            assert(os.path.exists(config))
        except:
            try:
                config = os.path.join(os.environ['XDG_CONFIG_HOME'], 'braus', 'braus.ini');
                print("Looking for configuration file %s" % config)
                assert(os.path.exists(config));
            except:
                try:
                    config = os.path.join(os.environ['HOME'], '.config', 'braus', 'braus.ini')
                    print("Looking for configuration file %s" % config)
                    assert(os.path.exists(config));
                except:
                    try:
                        config = os.path.join(os.environ['HOME'], '.brausrc')
                        print("Looking for configuration file %s" % config)
                        assert(os.path.exists(config))
                    except:
                        config = 'braus.ini'
                        print("Looking for configuration file %s" % config)

        if os.access(config, os.R_OK):
            print("Using configuration file %s" % config)
        else:
            return None
            ##raise Exception('Configuration file doesn\'t exist or is not readable')

        return config

    def default_config_file(self):
        return os.path.join(os.environ['HOME'], '.brausrc')

    def loadConfig(self, config):
        if config is None:
            config = self.getConfigFile()
            print(f"Loading Config: {config}")
        
        self.config = configparser.ConfigParser()
        if(config is not None):
            self.config.read([config])

    def _getValue(self, url, default=None):
        if self.config is None:
            raise Exception('Configuration has not been loaded.')
        try:
            return self.config[url]
        except configparser.Error:
            return default
        except KeyError:
            return default


    def _updateConfigToKeepAsking(self, url):
        file = self.getConfigFile()
        self.loadConfig(file)

        domain = urlparse(url).netloc
        
        if( not self.config.has_section(domain)):
            self.config.add_section(domain)

        self.config.set(domain, "keepasking", "true")

        with open(file or self.default_config_file(), 'w') as configfile:
            self.config.write(configfile)

    def _updateConfig(self, url, browser, profile):
        file = self.getConfigFile()
        self.loadConfig(file)

        domain = urlparse(url).netloc
        
        if( not self.config.has_section(domain)):
            self.config.add_section(domain)

        if( self.config.has_option(domain, 'keepasking')):
            self.config.remove_option(domain,'keepasking')

        self.config.set(domain, "browserId", browser.get_id())
        if(profile != None): 
            self.config.set(domain, "profile", profile)

        with open(file or self.default_config_file(), 'w') as configfile:
            self.config.write(configfile)