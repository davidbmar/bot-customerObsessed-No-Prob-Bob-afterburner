# Documentation Site — Published to S3 + CloudFront

## What Gets Published

A polished, user-friendly documentation site covering the entire Afterburner ecosystem — the vision, architecture, how to use it, and how each piece fits together. Readable by anyone with the URL.

## Site Structure

```
docs-site/
├── index.html              # Landing page — the big picture
├── vision.html             # Vision: why this exists, what problem it solves
├── architecture.html       # How the pieces fit together (diagrams)
├── customer-bot.html       # The customer discovery bot — personality, tools, UX
├── personality-framework.html  # How personalities work — principles, memory, evaluation
├── afterburner.html        # Afterburner sprint engine overview
├── tool-telegram.html      # tool-telegram-whatsapp — setup, config, API
├── getting-started.html    # Quick start: install, configure, first conversation
├── api-reference.html      # All APIs across all tools
├── css/styles.css          # Dark theme consistent with Afterburner dashboard
└── js/nav.js               # Sidebar navigation
```

## Deployment

Using `~/src/tool-s3-cloudfront-push/`:

1. Build the static HTML site locally
2. Serve it on a local port (e.g., `python3 -m http.server 8080`)
3. Run `step2-onetime-create-s3-bucket-and-cloudfront-once-per-site.sh` to create the bucket
4. Run `step1-crawl-site.sh` to snapshot the site
5. Run `step3-deploy-upload-files-to-s3-and-refresh-cloudfront-cache.sh` to deploy

The site gets a CloudFront URL (HTTPS, globally cached).

## Content Highlights

The documentation should tell a story:

**Landing page**: "Build products by talking to customers. The AI does the engineering."

**The flow**: Customer conversation → Seed docs → Vision → Plan → Sprint → Shipped code → Customer feedback → Loop

**Why it's different**: Most AI dev tools start with the code. This starts with the customer. The bot obsessively understands the problem before a single line is written.
