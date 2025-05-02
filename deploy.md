# Deployment Guide

[![Deploy](https://github.com/patrsc/maplinedraw/actions/workflows/deploy.yml/badge.svg)](https://github.com/patrsc/maplinedraw/actions/workflows/deploy.yml)

maplinedraw.com web site

## Prerequisites

### Domains

The domain `maplinedraw.com` was registered. DNSSEC is **enabled**. DNS entries are:

```
host1.maplinedraw.com     A       109.230.224.9
host1.maplinedraw.com     AAAA    ???
host1.maplinedraw.com     CAA     0 issue "letsencrypt.org"

maplinedraw.com           A       109.230.224.9
maplinedraw.com           AAAA    ???
maplinedraw.com           CAA     0 issue "letsencrypt.org"

www.maplinedraw.com       CNAME   host1.maplinedraw.com.
```

### Server Setup

A virtual server is set up:

* OS: Ubuntu 24.04 LTS
  * Install using default settings
  * Your name: `user` (verify keyboard layout)
  * Server name: `host1`
  * Username: `user`
  * Password: generate randomly (use KeePass autotype)
  * Install OpenSSH Server (default settings)

* Reverse DNS entries (set up by customer service):
  ```
  109.230.224.9                        host1.maplinedraw.com.
  ???    host1.maplinedraw.com.
  ```

* SSH access with a public key is set up. The SSH config `~/.ssh/config` is:

  ```
  Host maplinedraw.com
    User user
    IdentityFile ~/.ssh/id_rsa
  ```

### Server Configuration

* Login to server:

   ```
   ssh maplinedraw.com
   ```
* Disable sudo password prompt by runnging `sudo visudo` and add at end of file:
  ```
  user ALL=(ALL) NOPASSWD: ALL
  ```
* Verify IP addresses:
  ```
  sudo apt install -y net-tools
  ifconfig
  ```
* Disable SSH password authentication on the server by setting in `/etc/ssh/sshd_config`:
  ```
  PasswordAuthentication no
  KbdInteractiveAuthentication no
  ```
  and commenting the line in `/etc/ssh/sshd_config.d/50-cloud-init.conf`:
  ```
  #PasswordAuthentication yes
  ```
  and restart with `sudo systemctl restart ssh`, then verify on the client that the following fails:
  ```
  ssh -o PubkeyAuthentication=no maplinedraw.com
  ```
* Install Docker including Docker Compose: [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/) using the apt repository

### Repository Access

[Add a depoly key](https://github.com/patrsc/maplinedraw/settings/keys) for this repository in GitHub:
* Run the following command on the server to create a SSH key pair (without passphrase)
  ```
  ssh-keygen -t ed25519 -C "maplinedraw.com"
  ```
* Copy the output of `cat ~/.ssh/id_ed25519.pub` as the key to GitHub (use title **maplinedraw.com** and read-only option)

## Install

Log in to server and clone repository:

```
git clone git@github.com:patrsc/maplinedraw.git
```

Change directory:

```
cd maplinedraw
```

Set up volume:

```
sudo bash scripts/init.sh
```

Put your email address to the `.env` file:

```
echo "CERTBOT_EMAIL=your-email-here@example.com" > .env
```

Run containers to obtain certificates:

```
sudo docker compose up
```

The site https://maplinedraw.com should now be available with HTTPS.

Exit the container with: CTRL + C

Cleanup the containers:

```
sudo docker compose down
```

## Run

Log in to server and go to directory:

```
cd maplinedraw
```

Start containers:

```
bash scripts/build.sh
```

Stop containers:

```
sudo docker compose down
```

## Setup Github Action

On your local machine, generate an SSH keypair:

```
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/id_ed25519_github_actions -P ""
```

View private key and copy it to a safe place:

```
cat ~/.ssh/id_ed25519_github_actions
```

View public key and copy it to a safe place:
```
cat ~/.ssh/id_ed25519_github_actions.pub
```

Install public key on server:
```
cat .ssh/id_ed25519_github_actions.pub | ssh maplinedraw.com "cat>> ~/.ssh/authorized_keys"
```

Delete keys from local machine:
```
rm ~/.ssh/id_ed25519_github_actions*
```

Add the the following [repository secrets](https://github.com/patrsc/maplinedraw/settings/secrets/actions):
* `SSH_PRIVATE_KEY`: paste the private key
* `SSH_KNOWN_HOSTS`: paste the output of `ssh-keyscan -t ed25519 maplinedraw.com 2>/dev/null`

Refer to the file [deploy.yml](.github/workflows/deploy.yml) for the action contents.
