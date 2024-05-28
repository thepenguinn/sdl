#!/bin/python

from telethon import TelegramClient, events, tl

from googlesearch import search
from pyfzf.pyfzf import FzfPrompt

import subprocess
import asyncio
import configparser
import re
import sys
import os

Config_Dir = "${HOME}/.config/sdl"

Api_Id = None
Api_Hash = None

Music_Dir = None

def Logger(msg, level = "LOG"):
    print(msg)

class SpotQuery:

    _re_pat = None
    _fzf = None

    def __init__ (self, query):
        if SpotQuery._re_pat is None:
            SpotQuery._re_pat = re.compile("^(https://open\.spotify\.com/(.+)/.{22})(\?)?(.*)$")
        if SpotQuery._fzf is None:
            SpotQuery._fzf = FzfPrompt()
        self.query = query
        self.query_results = None

    def _get_index (self, line):
        end = 0
        for i in range(len(line) - 1):
            if line[i] == " ":
                end = i
                break

        return int(line[0:end])

    def query_spotify_links (self, query = None):

        if query:
            self.query = query

        self.query_results = []

        for res in search("spotify " + self.query, advanced = True, num_results = 10):
            mat = self._re_pat.match(res.url)

            if mat is not None:
                groups = mat.groups()
                if groups[1] == "album" or groups[1] == "track" and groups[2] is None:
                    if groups[1] == "album":
                        res_type = "Album"
                    else:
                        res_type = "Track"

                    self.query_results.append({
                        "url": groups[0],
                        "type": res_type,
                        "title": res.title,
                        "description": res.description
                    })

        return self.query_results

    def prompt_user (self):

        if not self.query_results:
            self.query_spotify_links(self.query)

        fzf_list = []
        idx = 0

        for res in self.query_results:
            fzf_list.append(str(idx) + " " + res["type"] + ": " + res["title"])
            idx = idx + 1

        sel = self._fzf.prompt(fzf_list, "--with-nth 2..")

        if not sel:
            return None

        sel_idx = self._get_index(sel[0])

        self.selected_query_result = self.query_results[sel_idx]

        return self.selected_query_result

    def gen_result (self):

        if not self.query_results:
            self.query_spotify_links(self.query)

        return self.prompt_user()

    def get_url (self, result = None):
        if result is None:
            result = self.selected_query_result
        return result["url"]

    def get_type (self, result = None):
        if result is None:
            result = self.selected_query_result
        return result["type"]

    def get_title (self, result = None):
        if result is None:
            result = self.selected_query_result
        return result["title"]

    def get_description (self, result = None):
        if result is None:
            result = self.selected_query_result
        return result["description"]


# qry = SpotQuery("wild love jonathan")
#
# print(qry.get_title())
# print(qry.get_type())
# print(qry.get_description())
# print(qry.get_url())



# client = TelegramClient('anon', api_id, api_hash)

# The first parameter is the .session file name (absolute paths allowed)
# with TelegramClient('anon', api_id, api_hash) as client:
#     client.loop.run_until_complete(client.send_message('deezload2bot', 'Hello its mejdjdjj'))

class SpotDownload:

    client = None

    def __init__ (self, session, api_id, api_hash):
        if SpotDownload.client == None:
            SpotDownload.client = TelegramClient(session, api_id, api_hash)
        self._last_dl_status = None
        self._last_album_track_count = 0
        self._last_album_title = ""
        self._last_album_artist = ""
        self._last_album_dl_count = 0
        self._one_photo_recieved = False
        self._one_track_recieved = False
        self._last_dl_files = None

    def _set_last_album_info(self, msg_text):

        lend = 0
        lstart = 0

        while msg_text[lend] != "\n":
            lend += 1

        self._last_album_title = msg_text[9:lend]

        lend += 1
        lstart = lend

        while msg_text[lend] != "\n":
            lend += 1

        self._last_album_artist = msg_text[lstart+10:lend]

        lend += 1
        lstart = lend
        while msg_text[lend] != "\n":
            lend += 1
        lend += 1
        lstart = lend

        self._last_album_track_count = int(msg_text[lstart+16:])

    def _curate_files (self):

        if len(self._last_dl_files) < 1:
            Logger("It seems like no files have been downloaded.", "WARN")
            return

        lrccmd = ["glrclib", "--verbose", "--files"]
        termuxcmd = ["termux-media-scan"]

        subprocess.run(lrccmd + self._last_dl_files)
        subprocess.run(termuxcmd + self._last_dl_files)

    def _prog_callback(self, current, total):
        # erases the line and moves to the first column
        print("", end = "\r")
        print('Downloaded', "%05.2f"%(current / 1000000) + "MB",
              'out of', "%05.2f"%(total / 1000000) + "MB" +
              ":% 6.2f%%"%(current / total * 100), end = "")

    async def _download_audio (self, msg):

        file = Music_Dir + "/" + msg.file.name
        if not os.path.isfile(file):
            self._last_dl_files.append(file)
            Logger("Downloading to " + file)
            await msg.download_media(file, progress_callback = self._prog_callback)
            print("")
        else:
            Logger("File exists, skipping the download", "WARN")


        # print("name: ", msg.file.name)
        # print("ext: ", msg.file.ext)
        # print("mime_type: ", msg.file.mime_type)
        # print("width: ", msg.file.width)
        # print("height: ", msg.file.height)
        # print("size: ", msg.file.size)
        # print("duration: ", msg.file.duration)
        # print("title: ", msg.file.title)
        # print("performer: ", msg.file.performer)

    async def _album_dl_handler (self, event):
        await event.mark_read()
        if event.message.message == "Invalid link ;)":
            Logger("Link was Invalid. Disconnecting...")
            self._last_dl_status = "Failed"
            await self.client.disconnect()

        if event.audio:
            await self._download_audio(event)
            self._last_album_dl_count += 1
            if self._last_album_track_count == self._last_album_dl_count and self._one_photo_recieved:
                Logger("Downloaded all the tracks. Disconnecting...")
                self._last_dl_status = "Success"
                await self.client.disconnect()
            return
        elif event.photo and self._last_album_track_count > 0:
            self._one_photo_recieved = True
            Logger("Recived one message with a photo")
            return

        if event.message.message == "Downloading…":
            Logger("Recived one message with a Downloading…")
            return

        if event.buttons:
            # This must be the first msg if the url is a proper one
            self._set_last_album_info(event.message.message)
            Logger("Message has buttons")
            for row in event.buttons:
                for btn in row:
                    if btn.text == "GET ALL ⬇️":
                        Logger("Clicking GET ALL button")
                        await btn.click()
        else:
            Logger("Message has no buttons", "WARN")

    async def _track_dl_handler (self, event):
        await event.mark_read()
        if event.message.message == "Track not found." or event.message.message == "Invalid link ;)":
            if event.message.message == "Track not found.":
                Logger("Track no found. Disconnecting...", "WARN")
            else:
                Logger("Link was Invalid. Disconnecting...", "WARN")
            self._last_dl_status = "Failed"
            await self.client.disconnect()

        if event.audio:
            Logger("Recived one message with an audio")
            self._one_track_recieved = True
            await self._download_audio(event)

        if event.photo:
            Logger("Recived one message with a photo")
            self._one_photo_recieved = True

        if self._one_photo_recieved and self._one_track_recieved:
            Logger("Recieved the track and the photo. Disconnecting...")
            self._last_dl_status = "Success"
            await self.client.disconnect()


    async def _download (self, link_list):

        for link in link_list:
            # TODO: playlist
            link_url = link[0]  # should be a spotify url to a track or an album
            link_type = link[1] # should be Track or Album

            if not self.client.is_connected():
                Logger("Connecting to Telegram...")
                await self.client.connect()
                Logger("Connected to Telegram")

            Logger("Sending the url to deezload2bot")
            await self.client.send_message(
                "deezload2bot", link_url
            )
            if link_type == "Album":
                Logger("Dettaching track download handler...")
                self.client.remove_event_handler(
                    self._track_dl_handler
                )
                Logger("Attaching album download handler...")
                self.client.add_event_handler(
                    self._album_dl_handler,
                    events.NewMessage(chats = [ 'deezload2bot' ], incoming = True)
                )
                self._last_album_track_count = 0
                self._last_album_title = ""
                self._last_album_artist = ""
                self._last_album_dl_count = 0
            else:
                Logger("Dettaching album download handler...")
                self.client.remove_event_handler(
                    self._album_dl_handler
                )
                Logger("Attaching track download handler...")
                self.client.add_event_handler(
                    self._track_dl_handler,
                    events.NewMessage(chats = [ 'deezload2bot' ], incoming = True)
                )
                self._one_track_recieved = False

            self._last_dl_status = None
            self._last_dl_files = []
            self._one_photo_recieved = False

            Logger("Waiting for the reply from deezload2bot...")
            await self.client.run_until_disconnected()
            if self._last_dl_status == "Success":
                Logger("Succeded downloading the file(s)")
                self._curate_files()
            elif self._last_dl_status == "Failed":
                Logger("Failed downloading the file(s)", "WARN")
            else:
                Logger("_last_dl_status should be either Success or Failed", "WARN")
                Logger("Current value: " + self._last_dl_status, "WARN")


    def download (self, link_list):

        self.client.start()
        self.client.loop.run_until_complete(self._download(link_list))


Config_Dir = os.path.expandvars(Config_Dir)

config_file = Config_Dir + "/config.ini"
if not os.path.isfile(config_file):
    print("Config file is not present: " + config_file)
    print("Inorder to sdl to work, you need the Telegram Api Id and Hash")
    print("Exiting...")
    exit()

config = configparser.ConfigParser()
config.read(config_file)

Music_Dir = os.path.expandvars(config["download"]["Dir"])

if not os.path.isdir(Music_Dir):
    print("Directory doesn't exists: " + Music_Dir)
    print("Please make sure you have specified the right directory to download files.")
    print("Exiting...")
    exit()

Api_Id = int(config["telegram.api"]["Id"])
Api_Hash = config["telegram.api"]["Hash"]

# TODO: download directly from links
# pat = re.compile("^(https://open\.spotify\.com/(.+)/.{22})(\?)?(.*)$")

query = ""

if len(sys.argv) > 1:

    query = sys.argv[1]

    for arg in sys.argv[2:]:
        query = query + " " + arg
else:
    print("Query: ", end = "")
    query = input()

if query == "":
    Logger("No query, exiting...")
    exit()

squery = SpotQuery(query)

if squery.gen_result() is None:
    Logger("No selections were generated, exiting...")
    exit()

sdl = SpotDownload(Config_Dir + "/anon", Api_Id, Api_Hash)
sdl.download([(squery.get_url(), squery.get_type())])
