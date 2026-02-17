# blinkenlights

A clone of `towel.blinkenlights.nl` based on the July 2025 version from [asciimation.co.nz](https://www.asciimation.co.nz/).

You can access the raw [starwars.txt](starwars.txt)

The server includes some basic controls:

* `space` = pause
* `left`,`right` = skip 5 frames backward or forward
* `pg up`,`pg dn` = skip 20 frames backward or forward
* `q`,`Q` = quit

Note: Each frame has a different duration.

## Docker

Use the `starwars.dockerfile` if you want to host this yourself. It hosts it both via `telnet` and `ssh`.

* Build:
  * `docker build -t starwars-server .`
* Run:
  * `docker run -d -p 23:2323 -p 2222:22 starwars-server`
  * Maps host port 23 (Telnet) to container 2323, and host port 2222 (SSH) to container 22.
* Connect:
  * Telnet: `telnet localhost`
  * SSH: `ssh starwars@localhost -p 2222` (No password required)
