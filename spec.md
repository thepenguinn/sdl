---
title: Specification for sdl
---

# Overview

There will be two parts the sdl:

- One that **Interacts** with the **User**. (client side)
- One that **Interacts** with the **Telegram**. (daemon side)

Both of these communicates through sockets.

## Daemon Side

The backend code that actually downloads the songs. This will be running as a daemon.
When the client is starts, it will check for this daemon. If it finds it, it will connect
to the daemons, ( there will two threads running maintaining the connection, one to recv
and the other to send ) otherwise the client fork()s the daemon. The daemon will exit, when
there is no file to download, or when the client asks it to terminate.

As soon as the daemon initializes, it open a socket on localhost (with a port number) and waits
for the client to connect. If it fails after a timeout it will terminate itself.

The communication between the client and the daemon will be synchronous, and each other will
send an aknowledgement to the other after receiving a message.

### Thread Structure

There will be three threads:

- One that connects to Telegram and downloads the files
- One that will reads the urls to download.
- One that will sends download status to the client.

### Download Status

Downloading file name, Title, Artist, total size, downloaded size.

### Sending commands to daemon

sending urls, sending terminate signals


## Client side

Once the client was launched by the user, it will do these things.

- Checks for a running daemon.
- If it finds a running daemon, it will connect to it, and waits for user inf.
- Otherwise tries to generate a valid list of urls.
- If succeded to generate the links, it will launches the daemon, and connects to it.
- And sends the urls to the daemon, and waits for


,it will try to generate a valid link the queryed song,


### Message structure

#### Command

First byte will be the command, it's just one byte, there for only 256 commands
are possible, but thats plenty for our use case

#### Size of the payload

Next four bytes will be the size of the payload. 0x00 0x00 0x00 0x00 if the
there's no payload. It will be in little endian. Note that the size field
is manditory.

ie,


```
    0xXX 0x02 0x23 0x00 0x00 0xXX .. 0xXX
    ^    ^                 ^ ^          ^
    |    |                 | +----------+---- Payload
    |    +-----------------+----------------- Size of payload
    +---------------------------------------- Command

```

In this case the size of the of the payload is 0x00 0x00 0x23 0x02, ie,
0x00002302 in hex. Because the size is in the little endian. First byte
recieved after the command byte is the lower byte of the 32 bit size value.

### Protocol

### Commands

ask then, keep the list, daemon will notify every time it is doing something


add
drop
drop_cur
add_at









true if sdl.connect()
will launch the deamon and connects to it, if daemon is not running.
otherwise just connects to the daemon

check if the queu
the thread that draws the screen will have a lock,

lock = Lock()

draw_thread(lock)
lock.acquire()

draw the screen
...
...

input_thread(lock)
lock.release()


status_thread(lock)
lock.release()

main_thread


client
----
a thread to take user input
a thread to draw the screen
a thread to recv the status

the thread that takes the user input is the one that sends commands to the

daemon
----

daemon will have two threads, and the main thread (the command thread) will be
the one that responding the commands, the client can send commands and recieve
reply or data from the daemon.

The other thread will be the downloader thread. It will pop the links from a
shared queue and downloads it one by one. The log info will be written to a
file and be sended back to the client. And if the client got disconnected the
status info will be appended to a list. The this list can be queried via the
command thread (using the command socket).

Once the daemon is started the daemon setups the server, for recieving the
connections and listens for incomming connections. First of all the daemon
listens for an OK connection. After establishing a connection, the daemon
will send two bytes an 'OK'. And the client should read this two bytes, and
should disconnect instantly.

After this the daemon intializes for the actual connection. First connection
will be for the status socket. This connection will send the download status.
And the client should never write to this socket.

The second connection is for the command socket. This connection can be used
to control the daemon, querying data, etc.

The command connection will be managed by the main thread, and the status
connection will be managed by the download thread.

Working of the daemon
----

blah

status types
----

LOG
string

WARN
string

SEND
nothing

STATUS
{ "current": bytes,
  "total": bytes  }

FAILED
nothing

SUCCESS
nothing



only two threads

first start this one
a thread that down loads the telegram files

then on main thread listen for the commands
a thread that responds to the commands

what should daemon do on startup ?
----









sdl.connect == True

SDL
everything is taken care from inside of SDL class

current download_list

and download thread will pop each link one by one and downloads it

the zeroth in the download_list will be the current one downloading

structure of the download_list

query download_list
query url_list


url_list
{
url
got_info ; if -1 haven't got it, else will be the index from track_info_list
}
add to the url list

remove from the url list

ill send url links
that goes to the url_list

url_list will be poped from the zeroth index and used to

types: None, album, tracks, playlist

None if got nothing

url_list this thing is a link list
[
    {
        url,type
    },
    {
        url,type
    }
]

info_list

[
    {
        type: "album",
        tracks: [
            {track},
            {track},
            {track}
        ]
    },
    {
        type: "track",
        tracks: [
            {track}
        ]
    },
    {
        type: "playlist",
        tracks: [
            {track},
            {track},
            {track},
            {track},
            {track},
            {track}
        ]
    }
]

track ???

message > an object
id > number ? or string
file_name > string
track_name > string
artist_name > string
total_bytes > number
downloaded_bytes > number

reads from the url list and

this should be in the download thread
pops the each of the url link and queries for the track(s)
then we just pop each one

info_list --> [{type: "album", tracks: [{track}, {track}, {track}]}, {type: "track", tracks: [{track}]}, ]

current download
{
    url
    type: album, track, playlist
    remove from the url list
}

when we remove or add something, we will lock the download_lock
then we send or modify the url list

[
    {
        file_name
        file_id
        artist_name
        track_name
        album_name ... maybe?
        downloaded_bytes
        total_bytes
    }, {}...
]

you can query for download list etc


sdl.add














downloading
-----------

two parts

- downloading the file
- converting the urls from url_list to file_list

both of these have to happen asynchronusly

main task will be downloading the files
ofcourse there will be locks

what locks
you may ask
well i don't know

ok

if there is nothing in the file_list main task will wait for the query task
to fill the file_list and if theres nothing in the url_list, then the thread
will wait for the command thread to fill the url_list

daemon side
-----------

btw the daemon will store the entire url_list and the file_list, even if the
daemon is requested to delete the url. if the daemon is requestd to delete the
url, it will marked as discarded, this is useful when the user is a jerk like
me who can't properly decide anything for the sake of their life, and wants to
undo the deletion.

user wants to add a new url or a new song or a new album or a new playlist

add command
can add a list of urls to for downloading -> this is a list of (url, url_type)

```python
url_list = [
    [url <string>, url_type <enum>, query_time <number> or <None>],
    [url <string>, url_type <enum>, query_time <number> or <None>],
    [url <string>, url_type <enum>, query_time <number> or <None>]
]
```
the daemon only recieves this thing

the daemon will store this as a list of "link" ie, a query_list

```python
query = {
    query_time: <number> or <None>,
    url: <string>,
    url_type: <enum>,
    # True if we queried the info and generated the link_info
    got_info: <boolean>
    discarded: <boolean>
}
```

after querying the info, the daemon will create a "info_list"

```python
info_list = {
    url_type: <enum>,
    tracks: [
        track,
        track
    ],
    discarded: <boolean>
    # maybe something else...
}
```

and the track_info will be:

```python
track = {
    message: <Telethon object>,
    file_name: <string>,
    file_id: <string> or <number>,
    artist_name: <string>,
    track_name: <string>,
    album_name: <string>, # maybe..? most likely not now
    downloaded_bytes: <number>,
    total_bytes: <number>,
    duration: <number>, # in seconds
    discarded: <boolean> # we can discard each of the tracks seperately
}
```

commands


```python
command = {
    command: <enum>,
    payload: <list> or <something>,
    # specifics to the command
}
```


there are certain times when the daemon doesn't allow to /lli


append
insert
discard
move
swap
switch

discarded list
or a skipped list
add to this as we skip things
then at last we will

or a done list

track
    track 1
    track 2
album
    track 1
    track 3
    track 4


client side
-----------

there will be a "link" list, but this "link" will have an extra
field, the "query" field.


```python
link = {
    query_time: <number>,
    url: <string>,
    url_type: <enum>,
    # True if we queried the info and generated the link_info
    got_info: <boolean>
    discarded: <boolean>
    query: <query>
}
```

```python
query = {
    query_time: <number>,
    query: <string>,
    responses = [
            {
            url: <string>,
            url_type: <enum>,
            title: <string>
        },
    ]
    selected = <number> # the index
}
```

this query field will be cached once the reponses are created and everytime
a new selection is made. The file name will the query_time

the url

query_task fills the file_list
file_list



commands
--------

add: list of urls


















client threads
--------------

thread to take user input    input_thread
thread to recv the status   status_thread

input_thread will be the main thread

input_thread and status_thread will control the draw_thread

There is a draw_lock, both the threads can draw the screen and inorder
for a thread to draw, it must acquire the draw_lock.

how ???

Locks !!!

data_lock for data
whenever the data is changed by the input_thread or the status_thread
and these threads call the draw_thread after the change







































































setup the server
wait for the client to connect
then once it connects
daemon should send an 'OK' to the client, client should recv this msg
and after this client will disconnect from the daemon,
then client can send start the normal procedure
the daemon will wait for two connection
send 'OK' and client should send send



















# Client and Daemon Architecture

The Client and Daemon will be

## Client Architecture

The client will have two threads (minimum of two if we are not doing any kind
of fancy animations). The threads will be:

- Input Thread
- Status Thread

### Input Thread

This thread will be the one


### Status Thread

### Data

- U

## Daemon Architecture

The Daemon will have tow threads. The threads will be:

- Download Thread
- Command Thread

### Download Thread


### Command Thread

### Data

- QueryTree: Long living
- QueryList: Not long living
- DownloadTree: Long living # this is the info_list
- DownloadList: Not long living

#### Note

Long living: Nothing will be removed from the object, once been added.
Not long living: The list will act as a queue, the 0th item will be popped off after use.

QueryTree and DownloadTree are basically python List
QueryList and DownloadList are MovableList

MovableList: They are basically List with the a method to move a block inside the list.
Can move a block up and down with the move method.

```python
class MovableList (List):
    def move (start:int, end:int, offset:int) -> None:
        '''
        start:int  -> start of the block that wants to be moved.
        end:int    -> end of the block that wants to be moved, inclusive.
        offset:int -> offset from the start, the block will be moved to that offset, with
                      start at that point.

        +---+---+---+---+---+--- offset
        0   1   2   3   4   5
        v   v   v   v   v   v
        +---+---+---+---+---+
        | 2 | 3 | 6 | 9 | 3 |
        +---+---+---+---+---+
          ^   ^   ^   ^   ^
          0   1   2   3   4
          +---+---+---+---+----- index

        move(0, 1, 4) will cause:

        +---+---+---+---+---+--- offset
        0   1   2   3   4   5
        v   v   v   v   v   v
        +---+---+---+---+---+
        | 6 | 9 | 2 | 3 | 3 |
        +---+---+---+---+---+
          ^   ^   ^   ^   ^
          0   1   2   3   4
          +---+---+---+---+----- index

        move(3, 3, 0) will cause:

        +---+---+---+---+---+--- offset
        0   1   2   3   4   5
        v   v   v   v   v   v
        +---+---+---+---+---+
        | 3 | 6 | 9 | 2 | 3 |
        +---+---+---+---+---+
          ^   ^   ^   ^   ^
          0   1   2   3   4
          +---+---+---+---+----- index

        if start, end, offset has any other values than above, will raise an IndexError

        '''
        return
```
