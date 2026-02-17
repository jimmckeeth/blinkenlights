# Star Wars Blinkenlights

I was sad to see that `towel.blinkenlights.nl` was offline. It is based on the animation from [asciimation.co.nz](https://www.asciimation.co.nz/), which launched in July 1997. I believe the telnet version launched shortly after that. I don't know if they are related at all. For a while `towel.blinkenlights.nl` said you you accessed it via IPv6 you got full color, but it turns out that was a gag, as the IPv6 version was the same.

> *Don't panic, just remember you towel.*

I've created a clone of `towel.blinkenlights.nl` based on the July 2025 version from [asciimation.co.nz](https://www.asciimation.co.nz/). You can access the raw [starwars.txt](starwars.txt) directly if you rather, or launch a `telnet`~~and `ssh`~~ server via docker.

The telnet server includes some basic controls:

* `space` = pause
* `left`,`right` = skip 5 frames backward or forward
* `pg up`,`pg dn` = skip 20 frames backward or forward
* `q`,`Q` = quit

*Note*: Each frame has a different duration.

## Docker server

Use the `Dockerfile` if you want to host this yourself via `telnet` (it technically supports `ssh` too, but there are no controls, so I disabled it for now).

* **Build**:
  * `docker build -t starwars-server .`
* **Run**:
  * `docker run --name starwars-server -d -p 23:2323 starwars-server`
  * Maps host port `23` (Telnet) to container port `2323`.
* **Connect**:
  * Telnet: `telnet localhost`
  * ~~SSH: `ssh starwars@localhost -p 23456` (No password required)~~
* **Stop**:
  * `docker rm -f starwars-server`

---

Inspired by [puxplaying's starshell](https://github.com/puxplaying/starshell). Visit [asciimation.co.nz](https://www.asciimation.co.nz/) to see the original and other projects.
