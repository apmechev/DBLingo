# DBLingo

Back up and monitor your Duolingo progress

Run inside the src/ directory as

```bash
python -m dblingo.dblingo
```

or if you have just installed, run

```bash
just run
```

## Configuration

You need to have the following environment variables set:

- `DBLINGO_USER`: your Duolingo username
- `DBLINGO_JWT`: your Duolingo JWT token (see below) (Also this may break the Duolingo TOS, so use at your own risk)
- `NEXTCLOUD_LINK`: the link to the Nextcloud path to save the data

### JWT token

You can programmatically get the JWT token by running the command below. This command requires your username and password, and also a browser that is supported by Selenium. 

```bash
just get-token
```
