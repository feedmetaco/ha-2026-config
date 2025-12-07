# Home Assistant CI/CD Workflow

## 🚀 You're Almost Done!

Your HA config is now on GitHub: https://github.com/feedmetaco/ha-2026-config

---

## Next Steps (3 Quick Manual Steps)

### Step 1: Configure Git Pull Add-on

1. Go to http://homeassistant.local:8123/hassio/addon/core_git_pull/configuration

2. **Configuration tab** - Paste this:

```yaml
deployment_user: ""
deployment_password: ""
deployment_key: []
deployment_key_protocol: rsa
git_branch: main
git_command: pull
git_remote: origin
git_prune: true
repository: git@github.com:feedmetaco/ha-2026-config.git
auto_restart: false
restart_ignore:
  - secrets.yaml
  - .gitignore
  - "*.md"
repeat:
  active: false
  interval: 300
```

3. Click **Save**

4. Go to **Info tab** → Click **START**

---

### Step 2: Get SSH Key from Add-on

After starting the add-on:

1. Go to **Log tab**
2. Look for: `RSA public key: ssh-rsa AAA...`
3. **Copy the ENTIRE key** (starts with `ssh-rsa`, ends with `root@...`)

---

### Step 3: Add SSH Key to GitHub

1. Go to: https://github.com/feedmetaco/ha-2026-config/settings/keys
2. Click **Add deploy key**
3. **Title:** `Home Assistant Git Pull`
4. **Key:** Paste the SSH key from Step 2
5. ✅ **CHECK "Allow write access"** (important!)
6. Click **Add key**

---

## Test the CI/CD Pipeline!

Once the above 3 steps are done:

1. **Make a test change locally:**
   ```cmd
   cd c:\Users\Sami\Documents\ha_2026_git_cicd
   echo # CI/CD Test >> configuration.yaml
   git commit -am "test: verify CI/CD pipeline works"
   git push
   ```

2. **Watch it auto-deploy:**
   - Go to Git Pull add-on → Log tab
   - Within seconds, you should see it pulling your changes!
   - GitHub webhook triggers it automatically

3. **Verify on GitHub:**
   - https://github.com/feedmetaco/ha-2026-config/settings/hooks
   - Check webhook deliveries - should show successful pings

---

## Daily Workflow (After Setup)

```
1. Edit files locally in Cursor
2. git commit -m "your message"
3. git push
4. ✅ Changes auto-deploy to HA server!
```

**That's it!** No manual syncing, no Samba copying - just push and it goes live! 🚀

---

## Rollback if Needed

```cmd
git revert HEAD
git push
```

The bad change auto-reverts!

---

## Safety Features (Optional)

Want auto-backup before each deploy? Add this automation to `automations.yaml`:

```yaml
- id: git_pull_webhook
  alias: "Git Pull on GitHub Push"
  trigger:
    - platform: webhook
      webhook_id: github_push
  action:
    - service: hassio.addon_stdin
      data:
        addon: core_git_pull
        input: pull
```

---

## Troubleshooting

**SSH key not working?**
- Make sure you copied the ENTIRE key including `ssh-rsa` prefix
- Verify "Allow write access" is checked on GitHub

**Webhook not triggering?**
- Check: https://github.com/feedmetaco/ha-2026-config/settings/hooks
- Click on the webhook → "Recent Deliveries" tab
- Should show successful pings when you push

**Manual pull:**
- Go to add-on Log tab
- Type `pull` and press Enter

---

## What You Have Now

✅ Local dev environment (c:\Users\Sami\Documents\ha_2026_git_cicd)  
✅ GitHub repository with version control  
✅ Webhook configured for auto-deployment  
✅ Git Pull add-on ready (just needs SSH key)  
✅ Production HA server ready to receive updates  

**Complete Steps 1-3 above and you're live!** 🎉

