# PROGRESS -- Second Opinion

## CURRENT PHASE
Part 2 (Environment and Data Model) -- COMPLETE. All ten checkpoint lines of BIBLE part 2 section 10 are satisfied and evidenced below. Waiting for BIBLE part 3 (Phase A -- Building the Skeleton).

## NEXT STEP
HUMAN to confirm the placeholder on a phone, then start BIBLE part 3 (Phase A: geography from the 42 Tables of Contents, entity registry from the Indexes, the duplicate-book rule, page_offset detection, the Freeze).

## QUESTIONS FOR HUMAN

### Q1 (2026-10-10) -- ANSWERED: the human said YES. The symlink below was created; see DONE 2026-10-10 (site mounted and live).


**Finding from the inventory (Part 2 section 1.6).** The web root of
www.strulovitz.org is `~/strulovitz-website/exports/`, served by Caddy
(`site-caddy.service`) on 127.0.0.1:8081, reached through the Cloudflare
Tunnel (`site-tunnel.service`). Apache is NOT involved and stays untouched.
The `exports/` folder already uses a symlink for its versioning
(`current -> v2026-10-10-a`), so a symlink is an established pattern here.
`exports/` is gitignored build output of the strulovitz-website repository.

**Proposal (recommended): one symlink, nothing else.**

```
ln -s ~/second-opinion/site ~/strulovitz-website/exports/2nd-opinion
```

Why this is enough and is the least invasive option:
- Caddy follows symlinks by default; the Caddyfile needs NO change.
- The Cloudflare Tunnel needs NO change.
- No sudo, no service restart, no risk to Apache or to the three existing
  sites (:8081 strulovitz, :8082 learnime, :8083 peak together).
- Because `exports/` is gitignored, the symlink never enters the
  strulovitz-website git history, so the two repositories never nest.
- Removal is one `rm` if the human ever wants it gone.

**Alternative if the human prefers an explicit Caddy rule** (requires editing
`~/strulovitz-website/hosting/Caddyfile`, which IS a committed file, and
reloading site-caddy):

```
handle /2nd-opinion/* {
    root * /home/nir/second-opinion
    rewrite * /site{uri}
    file_server
}
```

**Awaiting the human's yes. Nothing has been changed on the web server.**

## BLOCKED
- (nothing)

## LATER, IF MONEY
- (nothing yet)

## ENVIRONMENT INVENTORY 2026-10-10

Raw output of the Part 2 section 1 inventory, run on the laptop BEFORE any install.

```
### 1.1 OS / HARDWARE
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
VERSION_ID="13"
Linux deb-server 6.12.94+deb13-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.12.94-1 (2026-06-20) x86_64 GNU/Linux
nproc: 24
               total        used        free      shared  buff/cache   available
Mem:            62Gi       5.3Gi        38Gi       734Mi        19Gi        56Gi
Swap:           61Gi          0B        61Gi
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda4       1.8T  1.2T  463G  73% /
name, memory.total [MiB]
NVIDIA GeForce RTX 5090 Laptop GPU, 24463 MiB

### 1.2 PYTHON
/usr/bin/python3
Python 3.13.5
pip 25.1.1 from /usr/lib/python3/dist-packages/pip (python 3.13)
venv OK
neo4j MISSING
networkx 3.6.1
matplotlib MISSING
numpy 2.3.5
scipy MISSING
PIL 12.0.0
requests 2.32.3

### 1.3 NEO4J
openjdk version "21.0.12.1" 2026-08-18
/etc/neo4j
LISTEN 0      50     [::ffff:127.0.0.1]:7474             *:*   
LISTEN 0      4096   [::ffff:127.0.0.1]:7687             *:*   

### 1.4 GIT / GITHUB
git version 2.47.3
strulovitz
nir.strulovitz@gmail.com
gh version 2.97.0 (2026-07-31)
github.com
  ✓ Logged in to github.com account strulovitz (keyring)
  - Active account: true
  - Git operations protocol: https

### 1.5 WEB SERVING
  apache2.service               loaded active running The Apache HTTP Server
/home/nir/.local/bin/caddy
/usr/bin/cloudflared
caddyfile: ~/strulovitz-website/hosting/Caddyfile

### 1.6 WEB ROOT
total 968
drwxrwxr-x  5 nir nir   4096 Oct 10 15:26 .
drwxrwxr-x 17 nir nir   4096 Sep 28 20:09 ..
-rw-rw-r--  1 nir nir  18218 Oct 10 15:26 about.html
-rw-rw-r--  1 nir nir  18237 Oct 10 15:26 about-page-flux-2-max.html
-rw-rw-r--  1 nir nir  18469 Oct 10 15:26 about-page-gemini-3-pro-image.html
-rw-rw-r--  1 nir nir  18266 Oct 10 15:26 about-page-gpt-image-2.html
-rw-rw-r--  1 nir nir  18527 Oct 10 15:26 about-page-grok-imagine-image-2.html
origin	https://github.com/strulovitz/strulovitz-website.git (fetch)
origin	https://github.com/strulovitz/strulovitz-website.git (push)

### 1.7 LOCAL MODEL SERVERS
LISTEN 0      4096            127.0.0.1:11434      0.0.0.0:*   
qwen3.8:27b 17.7 GB
```

## INSTALLS 2026-10-10

```
$ sudo apt install -y openjdk-21-jre-headless
  openjdk version "21.0.12.1" 2026-08-18
  OpenJDK Runtime Environment (build 21.0.12.1+1-1-deb13u1-Debian)
  OpenJDK 64-Bit Server VM (build 21.0.12.1+1-1-deb13u1-Debian, mixed mode, sharing)

$ (added Neo4j official apt repo, per neo4j.com/docs/operations-manual/current/installation/linux/debian/)
$ sudo apt-get install -y neo4j=1:2026.09.0
  2026.09.0
  Cypher-Shell 2026.09.0

$ sudo neo4j-admin dbms set-initial-password <PASSWORD>   # password chosen by the human, never recorded here
$ sudo systemctl enable neo4j && sudo systemctl start neo4j
$ systemctl is-active neo4j
  active
$ cypher-shell -u neo4j -p <PASSWORD> "RETURN 1 AS ok;"
  ok
  1

$ cd ~/second-opinion && python3 -m venv .venv
$ .venv/bin/pip install neo4j networkx matplotlib numpy scipy pillow requests
  all imports OK
$ .venv/bin/pip freeze > kitchen/requirements.txt   # 20 packages
```

## DECISIONS BY HUMAN

- 2026-10-10: The human confirmed all seven Part 1 section 10 defaults, including "the Indexes are the source of the entity registry", and the names second-opinion (repo) / 2nd-opinion (URL).
- 2026-10-10: The human chose the Neo4j password himself and authorised its use. It is written ONLY into kitchen/.env (gitignored). It appears in no committed file and not in this ledger.
- 2026-10-10: The 42 PDFs were MOVED from ~/Downloads/books to ~/second-opinion/kitchen/books/ (no copies; the folder was emptied).
- 2026-10-10: Tier decision in force until end of October 2026: free models only for repetitive work; the MANAGER tier stays with Space Bunny.
- 2026-10-10: Three file pairs are byte-identical in size and are almost certainly duplicate books (Goodman & Gilman, Brenner & Rector, Bailey & Love). NOTHING was deleted. Part 3 applies the duplicate-book rule and the human makes the final choice.

## DONE (newest first, each with evidence)

### 2026-10-10 -- First commit pushed, and the site is LIVE (Part 2 sections 8 and 9)

The human approved the symlink proposal. Nothing in Caddy, in the Cloudflare
Tunnel or in Apache was modified.

```
$ ln -s ~/second-opinion/site ~/strulovitz-website/exports/2nd-opinion
$ ls -la ~/strulovitz-website/exports/2nd-opinion
2nd-opinion -> /home/nir/second-opinion/site

$ curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/2nd-opinion/
200
$ curl -s -o /dev/null -w "%{http_code}" https://www.strulovitz.org/2nd-opinion/
200
$ curl -s https://www.strulovitz.org/2nd-opinion/ | grep <title>
<title>Second Opinion - under construction</title>
```

The disclaimer of Law 12 is present once, at the bottom of index.html only.

Commit and push (Part 2 section 9):

```
$ git log --oneline | head -1
9658b85 Part 2: environment, layout, Neo4j schema, placeholder site
$ git status --short      # clean tree
```

Exactly 18 files were sent, the largest PROGRESS.md at 11,282 bytes. No file
over 40 MB. Verified before the push: `kitchen/.env` (the password),
`kitchen/books/` (the 13 GB of PDFs), `kitchen/pages/`, `kitchen/transcripts/`,
`kitchen/extractions/` and `.venv/` are all ignored, so none of them left the
laptop.


### 2026-10-10 -- Neo4j schema applied and helpers proven (Part 2 section 6)

kitchen/schema.cypher was extracted straight out of BIBLE/part-02-environment-and-data-model.md (lines 445-467), so it is word-for-word the schema the BIBLE fixed. Applied once with `cypher-shell -f`. No statement errored.

```
$ SHOW CONSTRAINTS YIELD name, labelsOrTypes, properties
"book_id_unique",       ["Book"],      ["book_id"]
"entity_slug_unique",   ["Entity"],    ["slug"]
"meta_key_unique",      ["Meta"],      ["key"]
"territory_id_unique",  ["Territory"], ["territory_id"]

$ MATCH (m:Meta) RETURN m.key, m.value ORDER BY m.key
"freeze_date", ""
"schema_version", "2"
"skeleton_frozen", "false"

$ SHOW INDEXES YIELD name, type, labelsOrTypes   ->  12 rows
  the 4 constraint indexes, the 5 named range indexes (territory_level_idx,
  territory_book_idx, entity_group_idx, entity_name_idx,
  quarantine_term_idx), entity_fulltext (FULLTEXT) and 2 automatic LOOKUP
  indexes. Exactly what the BIBLE expects.

$ python kitchen/db.py
[{'ok': 1}]

$ python -c "from slug import slug; print(slug('diseases-and-conditions', 'Sjögren's Disease'))"
diseases-and-conditions-sjogrens-disease
```

Both tests printed exactly the values the BIBLE predicted.

Secret safety proof -- kitchen/.env holds the real password and can never be committed:

```
$ git check-ignore -v kitchen/.env
.gitignore:4:kitchen/.env	kitchen/.env
$ git add -An --dry-run      # kitchen/.env is NOT in the list
```

```
$ cd ~/second-opinion && mkdir -p kitchen/pages kitchen/transcripts kitchen/extractions kitchen/logs data/registry data/export site/viewer site/pages site/assets site/data
$ git add -An --dry-run      # exactly what git would commit
  add '.gitignore'
  add 'AGENTS.md'
  add 'PROGRESS.md'
  add 'data/export/.gitkeep'
  add 'data/registry/.gitkeep'
  add 'kitchen/requirements.txt'
  add 'site/assets/.gitkeep'
  add 'site/data/.gitkeep'
  add 'site/pages/.gitkeep'
  add 'site/viewer/.gitkeep'

```

Proof the 13 GB of books and the password can never reach GitHub:

```
$ git check-ignore -v kitchen/books/ .venv/
.gitignore:5:kitchen/books/	kitchen/books/
.gitignore:1:.venv/	.venv/
```


The fixed tree of BIBLE part 2 section 4 was created. Here is exactly what git would commit, and what it refuses to commit:

### 2026-10-10 -- Repository layout and .gitignore (Part 2 section 4)

```
$ cd ~/second-opinion && mkdir -p kitchen/pages kitchen/transcripts kitchen/extractions kitchen/logs data/registry data/export site/viewer site/pages site/assets site/data
$ git add -An --dry-run      # exactly what git would commit
  add '.gitignore'
  add 'AGENTS.md'
  add 'PROGRESS.md'
  add 'data/export/.gitkeep'
  add 'data/registry/.gitkeep'
  add 'kitchen/requirements.txt'
  add 'site/assets/.gitkeep'
  add 'site/data/.gitkeep'
  add 'site/pages/.gitkeep'
  add 'site/viewer/.gitkeep'

```

Proof the 13 GB of books and the password can never reach GitHub:

```
$ git check-ignore -v kitchen/books/ .venv/
.gitignore:5:kitchen/books/	kitchen/books/
.gitignore:1:.venv/	.venv/
```

### 2026-10-10 -- AGENTS.md (Part 2 section 5.1)

The Fifteen Laws, the Glossary and the Manager model routing were copied straight out of BIBLE/part-01-charter-and-world-model.md with sed (lines 93-183, 429-471, 512-539), so they are word-for-word identical to the BIBLE, followed by the required closing paragraph.

```
$ wc -l AGENTS.md
  172 AGENTS.md
```

### 2026-10-10 -- Books received (the blocker from 2026-10-10 is resolved)

```
$ ls ~/second-opinion/kitchen/books | wc -l
  42
$ du -sh ~/second-opinion/kitchen/books
  13G
```

### 2026-10-10 -- Environment inventory (Part 2 section 1)

See the ENVIRONMENT INVENTORY 2026-10-10 block above. Key findings: Java, Neo4j and the Python neo4j/matplotlib/scipy libraries were MISSING; git, gh, Python 3.13, networkx, numpy, PIL, requests were present; the free READER model qwen3.8:27b (17.7 GB) was ALREADY downloaded in Ollama on 127.0.0.1:11434; the web root is ~/strulovitz-website/exports served by Caddy on port 8081 through the Cloudflare Tunnel.

### 2026-10-10 -- Neo4j installed and running (Part 2 section 2.2)

See the INSTALLS 2026-10-10 block above: `RETURN 1 AS ok` returned 1, and the database listens on 127.0.0.1:7474 and 127.0.0.1:7687 only, so it is NOT reachable from the internet.

### 2026-10-10 -- Python virtual environment (Part 2 section 2.3)

`.venv` created inside the repo; `all imports OK`; kitchen/requirements.txt written with 20 pinned packages.

### 2026-10-10 -- Environment inventory (Part 2 section 1) and the blocker

The 42 textbooks were NOT on this laptop. The human copied them from the Windows PC and they now sit in kitchen/books/ (gitignored).
