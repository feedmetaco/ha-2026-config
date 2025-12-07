# Home Assistant Configuration - ha-2026-config

Production Home Assistant configuration with automated CI/CD pipeline.

## 🏗️ Architecture

**Development Flow:**
```
Local (Cursor) → GitHub → HA Server (Auto-Deploy)
```

- **Local:** `c:\Users\Sami\Documents\ha_2026_git_cicd`
- **GitHub:** https://github.com/feedmetaco/ha-2026-config
- **Production:** Home Assistant at homeassistant.local

## 📋 Setup Status

✅ Fresh production snapshot pulled  
✅ Git repository initialized  
✅ GitHub repository created  
✅ Webhook configured  
⏳ **Git Pull add-on** - Needs SSH key (see [CI_CD_WORKFLOW.md](CI_CD_WORKFLOW.md))  

## 🚀 Quick Start

See **[CI_CD_WORKFLOW.md](CI_CD_WORKFLOW.md)** for complete setup instructions!

## 📂 Structure

```
ha_2026_git_cicd/
├── configuration.yaml      # Main HA config
├── automations.yaml        # Automations
├── scripts.yaml           # Scripts  
├── secrets.yaml           # Secrets (NOT in Git)
├── custom_components/     # Custom integrations
├── packages/             # Config packages
├── templates/            # Template helpers
├── dashboards/           # Lovelace dashboards
└── agents/              # Multi-agent system
```

## 🔒 Security

- `secrets.yaml` is gitignored (never committed)
- Use `secrets.template.yaml` as reference
- GitHub deploy key with write access
- Webhook for secure auto-deployment

## 💻 Development Workflow

```bash
# Make changes locally
nano configuration.yaml

# Commit and push
git commit -am "descriptive message"
git push

# ✅ Auto-deploys to HA server via webhook!
```

## 🛠️ Key Files

- **[CI_CD_WORKFLOW.md](CI_CD_WORKFLOW.md)** - Setup guide & daily workflow
- **[GIT_PULL_ADDON_CONFIG.md](GIT_PULL_ADDON_CONFIG.md)** - Detailed add-on configuration
- **secrets.template.yaml** - Template for required secrets

## 📊 Home Assistant Info

- **Version:** 2025.11.3+
- **Entities:** 2,479+
- **Location:** America/Los_Angeles
- **IP:** 192.168.10.6

## 🤝 Contributing

This is a personal HA configuration. Feel free to use as reference for your own setup!

## 📝 License

Personal configuration - use at your own discretion.

