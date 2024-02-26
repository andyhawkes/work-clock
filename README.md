# Work clock

A simple word-based clock built for a Raspberry Pi Zero with the InkypHAT e-ink display.

## Inky pHAT

I bought a [black/white/red Inky pHAT from the Pi Hut](https://thepihut.com/products/inky-phat) - due to an issue with the first one they sent out not refreshing I had to get it replaced, but the customer service was excellent throughout.

I'm running mine on a [Raspberry Pi Zero 2 W](https://thepihut.com/products/raspberry-pi-zero-2) (also bought from the Pi Hut) - I've got several Pi Zero W's knocking about in various states of project use, but I fancied a new one! They didn't have [the ones with the fancy coloured headers pre-soldered](https://thepihut.com/products/raspberry-pi-zero-2?variant=41181426942147), so I had to solder my own in.

# Overview

Inspired by [Matt Webb's AI Poem clock](https://www.kickstarter.com/projects/genmon/poem-1-the-ai-poetry-clock) as well as this [very expensive wall clock](https://www.jurawatches.co.uk/products/qlocktwo-classic-creators-edition-rust-wall-clock-45cm-fcenrt) (and this [much less expensive one](https://amzn.to/3SPwldn)), I wanted a word-based clock for my office that would not show the exact time but would be deliberately more vague.

![It's half past nine](/images/half-past.jpg)
![It's twenty-five to ten](/images/25-to.jpg)
![Bang on 4 o'clock](/images/on-the-hour.jpg)

An e-paper display seemed ideal for this as it would only need to update relatively infrequently (every 5 minutes).

Because this was going to be sat on my desk, I only want / need it to show the time during by working hours (and to act as a prompt to tell me to stop working at the appropriate hour), so to reduce the number of [display refreshes*](#caveats) the script will write a status value to a text file (`work-clock-status.txt`) each time it runs, and will check the status next time it runs in order to see if it needs to update the display or not.

You will need to update the following value in your [`work-clock.py`](work-clock.py#L42) file:

```
status_file = "/path/to/your/script/work-clock-status.txt"
```

You will need to use the full path, as the clock will ultimately be run by a [cron job](#automation).

By default, the clock will only update between 09:00 and 17:00, Monday to Friday - this can be set via [arguments passed to the Python script](#arguments) or the defaults can be edited in [lines 34 to 39 of `work-clock.py`](work-clock.py#L34-L39).

Outside of those times it will display either:

![It's not work time now](/images/not-work-time.jpg)

or

![It's the weekend!](/images/weekend.jpg)


# Usage

The script should be run with Python 3.

```
python3 work-clock.py
```

## Arguments

There are optional parameters that can be passed in to make the configuration easier:

* `--timezone, -t` - a [timezone string](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) e.g. "Eurpoe/Prague" Default is `Europe/London`.
* `--rotation, -r` - a rotation value for the screen in degrees. On a Pi Zero 90 = USB's at the top, 270 = USBs at the bottom. Default is `90`.
* `--days, -d` - a comma-separated list of non working days. 0=Monday, 6 = Sunday. Default is `5,6`.
* `--start, -s` - the hour of the day when work starts. Default is `9`.
* `--end, -e` - the hour of the day when work finishes. Default is `17`.

For example:

```
python3 work-clock.py -t "Asia/Brunei" -r 270 -d "4,5" -s 10 -e 18
```

## Automation

Running the script via Python 3 will update the display once, so if you want to run it as an actual clock you will need to set up a `cron` job to run every 5 minutes.

This is pretty simple - just run `crontab -e` and enter the following:

```
*/5 * * * * python3 /path/to/your/script/work-clock.py
```

Obviously you will need to substitute the correct path to the file on your device.

# Caveats

I believe that the Inky pHAT e-paper display is rated for about 100,000 refresh cycles - this means that if the clock script refreshes the display 12 times an hour, 9 hours per day, 5 days a week, it will potentially burn out the display in around 185 weeks (three and a half years).

If it was running every 5 minutes without non-working / weekend days then it would burn it out in just under a year!

# Acknowledgements

Hat tip to the good people at Pimoroni for the [Inky Python library](https://github.com/pimoroni/inky) and their [excellent tutorial on getting started with the Inky pHAT](https://learn.pimoroni.com/article/getting-started-with-inky-phat).

# To do

* Consider making the start and end times more granular (i.e. down to the minute)