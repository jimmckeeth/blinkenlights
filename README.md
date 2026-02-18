# Star Wars Blinkenlights

I was sad to see that `towel.blinkenlights.nl` was offline. It is based on the animation from [asciimation.co.nz](https://www.asciimation.co.nz/), which launched in July 1997. I believe the telnet version launched shortly after that. I don't know if they are related at all. For a while `towel.blinkenlights.nl` said if you accessed it via IPv6 you got full color, but it turns out that was only a gag.

> *Don't panic, just remember your towel.*

I've created a clone of `towel.blinkenlights.nl` based on the July 2025 version from [asciimation.co.nz](https://www.asciimation.co.nz/). You can access the raw [starwars.txt](starwars.txt) directly if you rather, or launch a Telnet and/or SSH server.

The Telnet server includes some basic controls:

* `space` = pause
* `left`,`right` = skip 5 frames backward or forward
* `pg up`,`pg dn` = skip 20 frames backward or forward
* `q`,`Q` = quit

*Note*: Each frame has a different duration.

## Server

You can run a local Telnet server via Python

```bash
python3 starwars-server.py
```

It defaults to port 2323, but that can be changed with the `--port` parameter. Use `--log` for verbose details, and if you want to remove the Telent specific control characters use `--raw` parameter (useful if you are redirecting it via SSH).

then connect

```bash
telnet localhost 2323
```

## Docker Server

Use the `Dockerfile` if you want to host this yourself via `telnet` and `ssh` (but there are no controls in SSH)

* **Build**: `docker build -t starwars-server .`
* **Run**: `docker run --name starwars-server -d -p 23:2323 -p 2222:2222 starwars-server`
  * Maps host port `23` (Telnet) to container port `2323`
  * and host port `2222` to container port `2222`
* **Connect**:
  * Telnet: `telnet localhost`
  * SSH: `ssh starwars@localhost -p 2222` (No password required)
* **Stop**: `docker rm -f starwars-server`

I have a small instance running in the cloud until it gets overloaded and goes down: `telnet 141.148.135.224` or `ssh starwars@141.148.135.224 -p 2222`

---

## Details on the files in the repo

* [`asciimation-dump.js`](asciimation-dump.js) will dump and decompress the ASCII animation from [asciimation.co.nz](https://www.asciimation.co.nz/)
* [`convert-asciimation.py`](convert-asciimation.py) converts the raw `starwars.txt` into `starwars.jsonl` for the server.
* [`debug.sh`](debug.sh) simple bash script that loops through rebuilding and launching the container for debugging.
* [`Dockerfile`](Dockerfile) the container file for creating a server instance
* [`entrypoint.sh`](entrypoint.sh) used by the `Dockerfile` as the _entrypoint_
* [`LICENSE`](LICENSE) GPLv3
* `README.md` _you are here_
* [`run.sh`](run.sh) script that combines build and run of the container
* [`sshd_config`](sshd_config) use by the `Dockerfile` to configure SSH (currently unused)
* `starwars.jsonl` the JSON Lines version of the Star Wars ASCII animation
* [`starwars-server.py`](starwars-server.py) python telnet server - reads and displays `starwars.jsonl`
* [`starwars.txt`](starwars.txt) the raw Star Wars ASCII animation

---

Inspired by [puxplaying's starshell](https://github.com/puxplaying/starshell). Visit [asciimation.co.nz](https://www.asciimation.co.nz/) to see the original and other projects.

