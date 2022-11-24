# cloudflare-dns-updater

Use Cloudflare's API to update your DNS A records if you have a dynamic IP address.

## Cron

setup following line in crontab where {ABS_PATH} is the path to this directory:

```crontab
*/5 * * * * {ABS_PATH}/check_zone.py update-all --zone-name=your-domain.xyz
```
