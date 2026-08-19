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

## Installation

```bash
just install
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

## Output

DBLingo exports the following JSONL files to the `data/` directory and
uploads them to the configured Nextcloud link:

| File | Contents |
| --- | --- |
| `duolingo_calendar.jsonl` | Study sessions, augmented with skill data. One line per session, each with `datetime`, `improvement`, `event_type`, `skill_id` plus `DatetimeLocal` and `DateLocal`. Existing lines are enriched in place when new data is available. |
| `duolingo_xp_summaries.jsonl` | Daily XP summaries (XP gained, sessions, streak flags), one line per day. |
| `duolingo_league.jsonl` | Current league info (tier, position, score, contest dates), one line per contest. |
| `duolingo_daily_quests.jsonl` | Daily quest progress, one line per day. |
| `duolingo_monthly_challenge.jsonl` | Monthly challenge progress and earned badges, one line per challenge. |
| `duolingo_friends_quest.jsonl` | Current friends quest progress, one line per quest. |
| `duolingo_friend_streak.jsonl` | Friend streaks, one line per match. |
| `duolingo_streak.jsonl` | Streak info (daily goal, site streak), one line per day. |

`DatetimeLocal` is formatted as an ISO 8601 datetime with offset
(e.g. `2026-08-19T07:30:06+02:00`) in the timezone from your Duolingo
profile, and `DateLocal` is the corresponding date (e.g. `2026-08-19`).
