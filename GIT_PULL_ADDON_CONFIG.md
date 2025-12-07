# Git Pull Add-on Configuration

## Step 1: Generate SSH Key in Add-on

1. Go to http://homeassistant.local:8123/hassio/addon/core_git_pull
2. Click **Configuration** tab
3. Under **Options**, add this configuration:

```yaml
deployment_user: feedmetaco
deployment_password: ""
deployment_key:
  - ""
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
  - GIT_PULL_ADDON_CONFIG.md
  - CI_CD_WORKFLOW.md
  - README.md
repeat:
  active: false
  interval: 300
```

4. Click **Save**
5. Go to **Info** tab
6. Click **Start**

## Step 2: Get SSH Public Key

After starting the add-on:

1. Go to **Log** tab
2. Look for a line that says: `RSA public key: ssh-rsa AAA...`
3. **Copy the entire public key** (starts with `ssh-rsa` and ends with `root@...`)

## Step 3: Add Deploy Key to GitHub

1. Go to https://github.com/feedmetaco/ha-2026-config/settings/keys
2. Click **Add deploy key**
3. **Title:** `Home Assistant Git Pull`
4. **Key:** Paste the SSH public key from step 2
5. ✅ Check **Allow write access** (important!)
6. Click **Add key**

## Step 4: Configure Webhook (Already Done!)

✅ Webhook is already created and configured!

The webhook URL is: `http://homeassistant.local:8123/api/webhook/github_push`

## Step 5: Enable Auto-Pull via Webhook

Add this automation to your `automations.yaml`:

```yaml
- id: git_pull_on_webhook
  alias: "Git Pull on GitHub Push"
  description: "Automatically pull config changes when pushed to GitHub"
  trigger:
    - platform: webhook
      webhook_id: github_push
  action:
    - service: hassio.addon_stdin
      data:
        addon: core_git_pull
        input: pull
    - delay:
        seconds: 10
    - service: homeassistant.check_config
    - delay:
        seconds: 5
    - choose:
        - conditions:
            - condition: template
              value_template: "{{ states('sensor.config_valid') == 'true' }}"
          sequence:
            - service: homeassistant.restart
      default:
        - service: notify.notify
          data:
            title: "⚠️ Git Pull Failed"
            message: "Config validation failed. Check logs."
```

## Step 6: Test the Workflow

1. Make a small change locally (add a comment to `configuration.yaml`)
2. Commit: `git commit -am "test: verify CI/CD pipeline"`
3. Push: `git push`
4. Watch the add-on logs - you should see it pull automatically!

## Troubleshooting

**SSH Key Issues:**
- Make sure you copied the ENTIRE key including `ssh-rsa` prefix
- Ensure "Allow write access" is checked on GitHub

**Webhook Not Triggering:**
- Check webhook deliveries: https://github.com/feedmetaco/ha-2026-config/settings/hooks
- Verify webhook URL is correct

**Manual Pull:**
- Go to add-on Log tab
- Type `pull` and press Enter

## Security Note

The webhook is currently HTTP (not HTTPS). For production use, consider:
- Setting up HTTPS with Let's Encrypt
- Using webhook secret validation
- IP whitelist for GitHub webhook IPs

