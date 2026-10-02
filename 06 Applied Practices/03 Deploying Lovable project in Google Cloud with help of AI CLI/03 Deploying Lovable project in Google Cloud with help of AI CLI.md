# Deploying a Lovable Prototype to Google Cloud with an AI CLI

**Sources:**

- Internal recorded walkthrough (approximately 30 minutes, Russian with English transcript)
- [Lovable: GitHub integration](https://docs.lovable.dev/integrations/github)
- [Lovable: Git sync overview](https://docs.lovable.dev/integrations/git-sync-overview)
- [GitHub CLI manual](https://cli.github.com/manual/)
- [Google Cloud CLI installation](https://docs.cloud.google.com/sdk/docs/install)
- [Cloud Run: Deploy services from source code](https://docs.cloud.google.com/run/docs/deploying-source-code)
- [Cloud Run: Mapping custom domains](https://docs.cloud.google.com/run/docs/mapping-custom-domains)
- [Cloud Run locations](https://docs.cloud.google.com/run/docs/locations)
- [Google AI Studio: Deploying apps](https://ai.google.dev/gemini-api/docs/aistudio-deploying)
- [Codelab: Deploy from AI Studio to Cloud Run](https://codelabs.developers.google.com/deploy-from-aistudio-to-run)
- [Gemini Code Assist consumer-tier deprecation](https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals)
- [Google Developer Program benefits FAQ](https://developers.google.com/profile/help/benefits)
- [Google: Developer benefits in Google AI Pro and Ultra](https://blog.google/innovation-and-ai/technology/developers-tools/gdp-premium-ai-pro-ultra/)

Prototype builders such as Lovable make it possible to produce a convincing web application in hours. Moving that prototype into an environment controlled by the company—its own cloud project, billing, region, domain, and branding—is a separate engineering task.

This lesson follows a recorded walkthrough in which a Lovable project was exported to GitHub, cloned locally, cleaned of builder-specific branding, containerized, and deployed to **Google Cloud Run** by an AI command-line agent driving the Google Cloud CLI. It then compares that route with the one-click Cloud Run deployment available in **Google AI Studio**.

The recording used Gemini CLI. The workflow itself is tool-agnostic: Claude Code, OpenAI Codex, Antigravity CLI, or OpenCode can perform the same steps, because the agent only plans the work and runs ordinary `git`, `gh`, and `gcloud` commands that the developer can inspect.

## Learning Objectives

By the end of this lesson, you should be able to:

- explain why a builder-hosted prototype is often moved to a company-controlled cloud project;
- export a Lovable project to GitHub and understand the consequences of two-way sync;
- prepare a cloud project, billing account, region, and local CLI tooling for deployment;
- direct an AI CLI to containerize and deploy a static frontend to Cloud Run;
- review the commands an agent proposes before they change cloud resources;
- remove builder branding and development-only dependencies safely through Git;
- choose public or restricted access, a custom-domain option, and cost limits deliberately;
- compare the manual CLI route with AI Studio's built-in deployment; and
- identify which parts of the process can be automated with continuous deployment.

## Version Notice

The recording was made before several mid-2026 product changes. Details below were checked against official documentation in **October 2026**.

- **Gemini CLI for consumer tiers.** Google states that, starting **June 18, 2026**, Gemini CLI and Gemini Code Assist IDE extensions stopped serving requests for the *Gemini Code Assist for individuals*, *Google AI Pro*, and *Google AI Ultra* tiers. Gemini Code Assist Standard and Enterprise subscriptions are not affected. Google points consumer users to the Antigravity product family, including Antigravity CLI. If your account is affected, replace "Gemini CLI" in this lesson with Antigravity CLI or another approved AI CLI.
- **Google Developer Program premium.** The recording quotes a monthly subscription of roughly 95 PLN that included about USD 45 of monthly Google Cloud credit. For **personal** Google Accounts, Google has consolidated these benefits into Google AI Pro and AI Ultra, with smaller monthly Cloud credit amounts; renewals of the standalone plan ended in 2026. Google states that premium on **Workspace** accounts did not change. Check the current benefits page for your account type before planning a budget.
- **Model names.** The recording selected Gemini 3 Flash for speed and mentioned Gemini 3 Pro for higher quality in AI Studio. Model availability changes quickly; choose from the live model list.

Treat the console screens, prices, credit amounts, and model names in the recording as examples, not current facts.

## Why Move a Prototype Out of the Builder?

A prototype published from a builder platform is usually hosted on the builder's domain, carries its branding, and is billed through the builder's subscription. That is fine for experiments. It becomes a problem when the prototype must be shown to a client, connected to company systems, or kept running under company policy.

| Builder-hosted prototype | Company-controlled deployment |
| --- | --- |
| Builder domain and branding in the tab icon, title, and link previews | Company branding and, optionally, a company domain |
| Billing and quotas tied to an individual builder account | Billing through an organizational cloud project |
| Region chosen by the platform | Region chosen to match latency, data-residency, or contract needs |
| Limited control over access | Public link, authenticated access, or private service as required |
| Source of truth in the builder | Source of truth in a Git repository the team controls |

The walkthrough split the work into two independent tasks: **(1) deploy** the existing project as-is, and **(2) remove builder traces**. Keeping them separate makes failures easier to localize: if the deployment breaks, the cause is in the infrastructure step, not in a branding edit.

## End-to-End Flow

```text
Lovable project
    │  Connect GitHub (two-way sync)
    ▼
GitHub repository
    │  gh auth login → gh repo clone
    ▼
Local working copy (VS Code)
    │  AI CLI: /init → project context file
    ▼
AI CLI plans the deployment
    │  Dockerfile + Nginx config
    │  gcloud config set project
    │  gcloud builds submit   → container image in Artifact Registry
    │  gcloud run deploy      → Cloud Run service + HTTPS URL
    ▼
Running service (*.run.app)
    │  optional: custom domain, continuous deployment
    ▼
Branding cleanup → commit → redeploy
```

Each arrow is a point where the developer should read what the agent proposes before approving it.

## Prerequisites

| Item | Why it is needed |
| --- | --- |
| Lovable project | The application to deploy |
| GitHub account or organization | Destination for the exported repository; a shared organization account can be used for a team or department |
| GitHub CLI (`gh`) | Simplest way to authenticate and clone a private repository |
| Google Cloud project with billing | Cloud Build, Artifact Registry, and Cloud Run require an active billing account |
| Google Cloud CLI (`gcloud`) | The agent deploys through it; the developer can repeat or audit every command |
| An approved AI CLI | Plans the work and runs commands with the developer's approval |
| An editor such as VS Code | Optional, but convenient for reviewing generated files and diffs |

**Project granularity.** A cloud project can be created per prototype, or several prototypes can share one project. Separate projects isolate billing, permissions, and cleanup; a shared project is simpler to administer. Whichever you choose, record the **project ID**—not just the display name—because every `gcloud` command uses it.

## Step 1: Export the Lovable Project to GitHub

1. In Lovable, open the project and select **GitHub → Connect GitHub**.
2. Authorize the Lovable GitHub app for the chosen account or organization. Grant access to all repositories or only to selected ones according to your policy.
3. Connect the project and confirm the repository transfer.

Lovable's integration is **two-way**: changes made in Lovable are pushed to GitHub, and changes pushed to the active GitHub branch (by default the repository's default branch) are synchronized back into Lovable. This has practical consequences:

- Branding cleanup committed to the default branch will also appear in the Lovable editor.
- Experimental commits pushed to the synced branch will change the live Lovable project.
- Deleting the GitHub repository stops synchronization; transferring it to another owner requires a matching GitHub connection in the Lovable workspace.

If you want to keep the builder and the deployment independent, work on a separate branch and merge deliberately, or stop editing in Lovable once the project has moved.

## Step 2: Clone the Repository Locally

Authenticate GitHub CLI once per machine:

```bash
gh auth login
```

Choose GitHub.com, HTTPS, and browser-based login. The CLI prints a one-time device code; enter it in the browser and authorize the account that owns the repository.

Then clone:

```bash
gh repo clone <owner>/<repository>
cd <repository>
```

Open the folder in your editor. Confirm that the working tree is clean before any agent starts changing files:

```bash
git status
```

## Step 3: Install and Authenticate the Google Cloud CLI

Install `gcloud` using the [official instructions](https://docs.cloud.google.com/sdk/docs/install) for your operating system. The recording asked the AI CLI to install it; that works, but read the proposed installation commands first, because an agent installing system software with your privileges is a high-impact action.

Authenticate and select the project:

```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
```

Prefer authenticating yourself rather than asking the agent to handle credentials. The agent will then run commands with whatever permissions your account has—so use a project where a mistake is cheap.

## Step 4: Give the Agent Project Context

Start the AI CLI in the repository root and generate a project context file. In Gemini CLI, `/init` scans the workspace and writes `GEMINI.md`; Claude Code and OpenCode provide equivalent `/init` commands that write `CLAUDE.md` or `AGENTS.md`. Antigravity CLI reads `AGENTS.md`.

This step costs a minute or two, but every later session starts with an understanding of the stack (in the recording: a Vite + React frontend that uses Supabase). Review the generated file before committing it—it may contain incorrect assumptions.

Model choice matters less here than scope control. A fast model is adequate for a well-defined deployment task; switch to a stronger model if the agent misreads the project or loops on errors.

## Step 5: Ask for a Bounded Deployment

The prompt in the recording was short and specific:

```text
Deploy this app to Google Cloud using the gcloud CLI.
Project ID: <PROJECT_ID>
Region: europe-central2 (Warsaw)
Deploy to Cloud Run. Do not create or change anything else.
```

Three elements make this prompt work:

- **Explicit target**: Cloud Run, not "the cloud". Without it, an agent may choose App Engine, a VM, or Firebase Hosting.
- **Explicit project and region**: avoids deploying into whatever project happens to be active. The agent correctly translated "Warsaw" into `europe-central2`.
- **Explicit boundary**: "do not change anything else" reduces the chance of extra resources, IAM changes, or unrelated file edits.

Some agents offer to expand a short prompt with additional details. Decline unless the additions are things you actually want.

### Why Cloud Run

Cloud Run runs containers as a serverless service and can **scale to zero**: when nobody uses the application, no instances run, and request-based charges stop. The first request after an idle period triggers a **cold start**; the recording estimated up to about 20 seconds, though a small static site served by Nginx usually starts much faster. Measure it for your own image.

Useful scaling settings:

| Setting | Effect |
| --- | --- |
| `--min-instances=0` | Allows scale to zero; cheapest, but cold starts occur |
| `--min-instances=1` | Keeps one instance warm; removes most cold starts but costs money continuously |
| `--max-instances=1` (or another small number) | Caps cost and concurrency; may reduce performance under load |

For a client demo, `min-instances=0` with a small `max-instances` value is usually a reasonable default.

## Step 6: Review What the Agent Generates and Runs

In the recording, the agent produced and executed the following plan. Expect something similar, and check each item.

### Files

- **`Dockerfile`** — a multi-stage build: install dependencies and run the Vite build in a Node image, then copy the static `dist/` output into an Nginx image.
- **Nginx configuration** — serves the static files, listens on the port Cloud Run provides (`8080` by default), and falls back to `index.html` so that client-side routes work after a page refresh.
- **`cloudbuild.yaml`** (optional) — the agent created a Cloud Build pipeline definition. A Dockerfile alone is enough for `gcloud run deploy --source .`; a separate pipeline file is useful when you want build arguments or continuous deployment.

### Commands

```bash
gcloud config set project <PROJECT_ID>

# Build the container image with Cloud Build and push it to Artifact Registry
gcloud builds submit --tag <REGION>-docker.pkg.dev/<PROJECT_ID>/<REPO>/<IMAGE>

# Deploy the image to Cloud Run
gcloud run deploy <SERVICE> \
  --image <REGION>-docker.pkg.dev/<PROJECT_ID>/<REPO>/<IMAGE> \
  --region <REGION> \
  --platform managed \
  --allow-unauthenticated
```

A shorter equivalent is `gcloud run deploy <SERVICE> --source . --region <REGION>`, which builds with Cloud Build, uses the Dockerfile if one exists, and stores the image in an Artifact Registry repository named `cloud-run-source-deploy`. The first run may ask to enable the Cloud Run Admin, Cloud Build, and Artifact Registry APIs.

In the recording, the build took about four minutes and the deployment about two. The result was a public HTTPS URL on `*.run.app`.

### What to Check

| Check | Why |
| --- | --- |
| The active project and region in every command | Prevents deploying to the wrong project |
| `--allow-unauthenticated` | Makes the service public; decide this explicitly |
| Build-time environment variables | Vite embeds `VITE_*` variables into the JavaScript bundle at build time |
| No secrets in the image or the bundle | Anything in a frontend bundle is readable by every visitor |
| New APIs, service accounts, or IAM bindings | These are changes outside the stated scope and need approval |

**Supabase and other backends.** The agent noticed that the project used Supabase and passed its URL into the build. A Supabase URL and *anon/publishable* key are designed to be public; the real protection is Row Level Security in the database. A service-role key must never be placed in a frontend build. Verify which keys the project contains before deploying.

## Step 7: Decide Who Can Access the Service

A public URL is convenient for showing a prototype to a client, but it is also reachable by anyone who finds it.

| Need | Option |
| --- | --- |
| Client demo with no sensitive data | Public service (`--allow-unauthenticated`), ideally with an unguessable service name and a planned shutdown date |
| Internal reviewers only | Require authentication, for example with Identity-Aware Proxy in front of the service |
| Service called only by another system | Private service that grants the Cloud Run Invoker role to a specific service account |

The recording gave a good example of the last case: a Google Chat app is deployed the same way, but access is restricted to the service account that Google Chat uses.

Some organizations block public access (`allUsers`) through organization policy. If deployment succeeds but the public binding fails, that is a policy decision, not a bug to work around.

## Step 8: Remove Builder Branding

With the deployment working, the second task is cleanup. The walkthrough started manually and then delegated the rest to the AI CLI.

### Typical Lovable Traces

| Location | What to change |
| --- | --- |
| `public/favicon.ico` (and other icons) | Replace with your own icon; an AI image tool can generate one |
| `index.html` `<title>` and meta description | Replace the generated title and "Lovable Generated Project" description |
| Open Graph and Twitter meta tags | Replace the preview image used by messengers and social networks |
| `package.json` | Rename the package; remove the `lovable-tagger` development dependency |
| `vite.config.ts` | Remove the `componentTagger()` plugin that `lovable-tagger` provides |
| `README.md` | Replace builder instructions with project-specific documentation |

**Preview images.** The recording copied an image address from the company website and pasted it into the Open Graph tags. Hotlinking works, but the preview breaks if that URL changes. Prefer adding the image to the repository's `public/` folder and referencing it with an absolute URL of the deployed site.

### Delegate the Rest, but Use Git

A clear instruction is enough:

```text
Remove all traces of Lovable from this app: branding, metadata, development-only
Lovable dependencies, and generated descriptions. Do not change application behavior.
```

In the recording, the agent removed `lovable-tagger`, updated the meta tags, and rewrote the project description to match the application domain. Before starting it, the deployment files were committed:

```bash
git add Dockerfile nginx.conf cloudbuild.yaml GEMINI.md
git commit -m "Add Cloud Run deployment configuration"
```

This creates a recovery point. After the agent finishes:

```bash
git diff            # review every change
npm run build       # confirm the app still builds
git commit -am "Remove Lovable branding"
```

If the commit is wrong, `git revert` restores the previous state. Remember the two-way sync: pushing this commit to the synced branch also updates the project in Lovable.

Then redeploy with the same command, or simply ask the agent to "deploy to Google Cloud again".

## Step 9: Optional Custom Domain

The default `*.run.app` URL is technical. A company domain makes a prototype look finished. Cloud Run currently documents three options:

| Option | Notes |
| --- | --- |
| Global external Application Load Balancer | Recommended by Google; works in every region; more setup and a running cost |
| Firebase Hosting in front of Cloud Run | Simple for web frontends; domain connected through Firebase |
| Cloud Run domain mapping | Preview feature; not recommended for production; available only in selected regions |

**Region matters.** Cloud Run domain mapping is not available in `europe-central2` (Warsaw), the region used in the recording. For a Warsaw deployment, use a load balancer or Firebase Hosting, or choose a supported region if latency and data-residency requirements allow it.

DNS changes and certificate issuance are performed by whoever administers the company domain. An agent can prepare the commands, but domain ownership verification and DNS records require the right people.

## Step 10: Optional Continuous Deployment

If the prototype will keep changing, a manual redeploy for every change becomes tedious. Cloud Run can be connected to a GitHub repository so that each push to a chosen branch triggers a Cloud Build build and a new revision.

Combined with Lovable's two-way sync, this creates a chain: an edit in Lovable → a commit on GitHub → an automatic Cloud Run deployment. That is powerful, but it also means an unreviewed edit in the builder reaches the public URL. Point continuous deployment at a branch that only receives reviewed changes.

The participants noted that the whole manual flow took about 20 minutes and asked whether it could be accelerated with a pipeline. Some steps remain manual by nature—connecting Lovable to GitHub, creating a project, linking billing—but everything after the first deployment can be automated.

## Alternative: Deploy from Google AI Studio

Google AI Studio's **Build** mode generates web applications from prompts, similar to Lovable. It also offers templates (for example, React or Angular) and a choice of Gemini models; the recording observed that output quality can differ between faster and stronger models.

Deployment is integrated: AI Studio can push the project to GitHub and **deploy it to Cloud Run** directly. The recording selected a Google Cloud project with billing enabled, clicked deploy, and received a running service in about a minute.

Current documentation describes two deployment modes:

- **Starter Tier** — eligible accounts can publish up to two full-stack applications without creating a Google Cloud project or billing account. Services run in a single Cloud Run region. Workspace accounts and accounts with prior paid Google Cloud billing are not eligible.
- **Standard deployment** — link a Google Cloud project with billing for more services, more resources, other regions, or other Google Cloud products.

### Comparison

| Aspect | Lovable → GitHub → AI CLI → Cloud Run | AI Studio → Cloud Run |
| --- | --- | --- |
| Time from finished prototype to URL | About 20 minutes in the recording, plus cleanup | About one minute in the recording |
| Branding cleanup | Required | Less builder branding to remove, according to the recording; still review metadata and icons |
| Control over Dockerfile, region, scaling, access | Full | Limited by the integrated flow; adjust afterwards in Cloud Run |
| Builder ecosystem | Lovable's editor, integrations, and Supabase support | Google ecosystem; Gemini models and Google Cloud billing |
| Repeatable for non-Google targets | Yes—the same agent can target other clouds | No—designed for Google Cloud |
| Skills learned | Containers, Cloud Build, Cloud Run, IAM | Mostly platform-specific |

Neither route is universally better. AI Studio is faster when the team already works in Google Cloud and the prototype fits its model. The CLI route is more transferable, works for prototypes from any builder, and leaves a reviewable Dockerfile and deployment history in Git.

### Cost Notes

The recording described prototyping in AI Studio as effectively free on the company account, with deployment covered by Google Developer Program cloud credits. It also suggested connecting an API key from a billed Cloud project if AI Studio limits are reached. As explained in the version notice, the credit amounts and plans differ by account type and have changed in 2026. Confirm:

- which subscription or program your account actually has;
- how many Cloud credits it includes and when they expire;
- whether Gemini API calls from the deployed app are billed to your project; and
- that a budget with alerts exists on the project.

A deployed AI-powered prototype that calls a model on every request can generate cost even when Cloud Run itself scales to zero between visits.

## Security and Governance Checklist

Before deploying a prototype under the company's name:

- [ ] Use a dedicated or clearly labeled Google Cloud project with an owner and a budget alert.
- [ ] Authenticate `gh` and `gcloud` yourself; do not paste credentials into the agent.
- [ ] Run the AI CLI in a mode that asks before executing shell commands.
- [ ] Read every `gcloud` command before approving it, especially those that enable APIs or change IAM.
- [ ] Confirm that the frontend bundle contains no secrets and that backend access is protected (for example, Supabase Row Level Security).
- [ ] Decide explicitly between public and authenticated access.
- [ ] Choose the region for a reason—latency, data residency, or feature availability.
- [ ] Commit before and after each agent task, and review `git diff`.
- [ ] Understand that pushes to the synced branch also change the Lovable project.
- [ ] Set `max-instances` and record when the prototype should be shut down or deleted.
- [ ] Remove builder branding only through reviewed commits.

## Practical Exercise

Use a non-sensitive prototype and a Google Cloud project where mistakes are inexpensive.

1. Create or select a small Lovable project and connect it to a GitHub repository.
2. Clone the repository with `gh` and confirm a clean working tree.
3. Authenticate `gcloud` and set the project.
4. Start an AI CLI, run `/init`, and review the generated context file.
5. Ask the agent to deploy the app to Cloud Run in a specific region, with an explicit scope boundary.
6. Approve each command only after reading it; record the build and deployment times.
7. Open the service URL, refresh a deep link, and confirm that client-side routing works.
8. Commit the deployment files, then ask the agent to remove all Lovable traces.
9. Review the diff, build locally, commit, and redeploy.
10. Optional: reproduce the same prototype in Google AI Studio and deploy it from there. Compare time, control, and the cleanup required.
11. Delete the Cloud Run services and container images when the exercise is complete.

## Common Mistakes

- Deploying into the wrong project because the agent used whatever `gcloud` project was active
- Leaving `--allow-unauthenticated` enabled without deciding that the prototype should be public
- Shipping a service-role key or other secret inside a frontend bundle
- Combining deployment and branding cleanup in one unreviewed agent run
- Forgetting that Lovable's two-way sync propagates commits back into the builder
- Hotlinking preview images from another website instead of storing them in the repository
- Expecting Cloud Run domain mapping in a region where it is not available
- Leaving warm instances or unused services running after the demo
- Treating one-click deployment as a substitute for access, cost, and data review
- Relying on the Gemini CLI or Developer Program terms shown in an older recording without checking current account eligibility

## Key Takeaway

Moving a builder prototype into a company-controlled cloud is a short but real engineering task: export to Git, give an AI CLI precise context and boundaries, review the Dockerfile and every `gcloud` command, decide access and cost limits, then clean up branding through reviewed commits. The agent removes most of the typing, not the responsibility. When the team already works in Google Cloud, AI Studio's built-in deployment can shorten the path from minutes to one click; the CLI route remains the more transferable and auditable option for prototypes from any builder.
