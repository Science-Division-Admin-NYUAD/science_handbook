# Editing the Handbook With Codex

This guide is for someone who needs to edit the handbook by chatting with Codex, rather than editing the website files directly.

The basic idea is simple: Codex can open the project, make edits, preview the website, commit changes, pull updates, and push changes to GitHub. You can work with it the same way you would work with a collaborator.

You will need:

- A GitHub account.
- Access to the `Science-Division-Admin-NYUAD/science_handbook` repository.
- Codex installed and connected to your GitHub account.
- The handbook repository available on your laptop.

Some basic terms:

- GitHub is the online place where the handbook files are stored. It keeps the official version of the website and tracks changes over time.
- A repository, or repo, is the project folder on GitHub. In this case, the repo contains the handbook text, website design, images, and build settings.
- A commit is a saved checkpoint. When Codex commits changes, it is saving a clear version of the work with a short note about what changed.
- A push sends your local commits from your laptop to GitHub.
- A pull brings the latest changes from GitHub down to your laptop.
- A merge combines changes from one version or branch into another. This is usually how approved edits become part of the main website.
- A branch is a separate working version of the project. It lets someone make edits without changing the main version until the edits are ready.
- A Pull Request is a request to merge one branch into another. It lets people review changes before they become part of the main website.

Ask the person managing the handbook to add your GitHub username to the repository. Once you have access, ask Codex to help you set everything up.

You can say:

```text
I need to start editing the Science Handbook website from my laptop. Please help me clone the repository, open it in Codex, and start a local preview.
```

If Codex asks for permission to run a terminal command, read the request and approve it if it matches what you asked it to do. This is normal. Codex may need the terminal to download the repository, build the website, start the preview, commit changes, pull updates, or push changes.

Before you start editing, ask Codex to make sure you have the latest version:

```text
Please pull the latest changes before we start.
```

To open the local website preview, ask:

```text
Please start the local preview and open the website for me.
```

If the preview does not load, tell Codex exactly what you see. For example:

```text
The preview is not loading.
```

or:

```text
The terminal says: Serving HTTP on 127.0.0.1 port 8011.
```

To make edits, describe the change in normal language. You do not need to know which file to edit.

Examples:

```text
In the Welcome page, please change “Standard mail and courier” to “Standard mail & courier.”
```

```text
Please separate these two sentences into two paragraphs.
```

```text
Can you make this paragraph smoother and shorter without losing important information?
```

```text
Please add this hyperlink to “Faculty Resources”: https://intranet.nyuad.nyu.edu/faculty-resources/
```

If you want to compare design options, ask Codex to preview them first:

```text
Can you give me three design options to preview before changing the actual website?
```

If you like one of the options, say:

```text
Let’s go with option 2 and apply it to the actual website.
```

After Codex makes a change, check the preview. If something looks wrong, describe it or send a screenshot.

Useful things to say:

```text
Please refresh the preview.
```

```text
I do not see the update. Can you check whether the build ran?
```

```text
This spacing is too tight. Can you loosen it slightly?
```

```text
This looks good. Please commit it.
```

Commit regularly. A commit saves a checkpoint in Git so changes are not lost.

When you are ready to commit, ask:

```text
Please commit the changes we have made so far.
```

Codex should check what changed, commit only the relevant files, and tell you the commit message or commit number.

When you are ready to send your changes to GitHub, ask:

```text
Please push origin.
```

If Codex says the push failed because there are new changes on GitHub, ask:

```text
Please pull the latest changes and help me resolve anything needed.
```

The website and downloadable PDF are both generated from the same handbook content. When you push changes to GitHub, GitHub builds the website and PDF automatically. If the PDF does not generate locally on your laptop, that is usually okay; GitHub is the important build.

To check the PDF after pushing, open GitHub and look at the latest workflow run. If it passes, download the PDF artifact or open the published website and use the PDF download button.

If a GitHub workflow fails, copy the error or send Codex a screenshot and ask:

```text
The GitHub build failed. Here is the error. Can you fix it?
```

Important habits:

- Do not edit the generated `site/` folder by hand.
- Ask Codex before pushing if you are unsure.
- Pull before starting a new editing session.
- Commit after a group of changes you are happy with.
- Push when you are ready for GitHub to build and publish the update.
- Use screenshots when something looks wrong.
- Be specific about page names, section names, and exact wording.

Helpful Codex prompts:

```text
Where did we stop last time?
```

```text
Please show me what files changed.
```

```text
Please summarize the changes since the last commit.
```

```text
Please commit this.
```

```text
Please push origin.
```

```text
Please pull the latest version.
```

```text
Please open the preview at the section we are working on.
```

```text
Please make this wording smoother, but keep all important information.
```

```text
Please give me three design options to preview.
```

You do not need to code. Your job is to review the content and design, tell Codex what you want changed, check the preview, and approve commits and pushes when you are ready.
