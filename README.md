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
- `DBLINGO_JWT`: your Duolingo JWT token (take it from the `token` field in the Network tab [here](https://github.com/KartikTalwar/Duolingo/issues/128#issuecomment-1437293650))
- `NEXTCLOUD_LINK`: the link to the Nextcloud path to save the data
