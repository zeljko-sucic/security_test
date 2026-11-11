# Candidate brief

## Assignment

You are joining the team that maintains HelpSpace. A security scan has produced a
queue of findings. Review the supplied report and relevant code, decide which
findings require changes, and explain your reasoning to the developers. You may
also report issues absent from the scanner output.

We care about careful investigation, curiosity, understanding and communication.
We do not expect a junior candidate to find everything or know every security term.

## Intended behavior and permissions

- Authentication is required for ticket content, comments, attachments, profiles
  and administration. Anonymous visitors may view the login page and static assets.
- Each user belongs to exactly one organization.
- Members can list, search and read their organization's tickets, download their
  attachments, and add plain-text comments. Attachments inherit ticket permissions.
- Members can change their display name, but cannot choose their role or organization.
- Organization administrators can additionally read their own organization's
  administration page and its internal planning note. They cannot access another
  organization's information.
- Comments are plain text. Formatting or executable HTML is not a product requirement.
- The supplied database contains only fictional information. Other users' fixture
  accounts are available to verify whether behavior crosses a permission boundary.

## Time and tools

Spend **90–120 minutes**, excluding setup. Stop at the time limit and record what
remains uncertain. Tell the interviewer about setup problems; they are not scored.
A 20-minute discussion will follow.

AI assistants (including Codex or Claude), Semgrep, documentation and other tools
are allowed. Use only this lab as your target. Do not test external systems.
Record which tools you used, one useful prompt or query, and how you checked the
result. We will ask you to explain your submission in your own words. You do not
need to share a private account's full chat history or credentials.

## Deliverables

Copy [SUBMISSION_TEMPLATE.md](SUBMISSION_TEMPLATE.md) into `candidate-notes/` or
submit a separate document. The local `candidate-notes/` directory is Git-ignored.

1. Triage the supplied findings: confirmed, false positive, conditional, or needs
   more evidence. Include file/line references and an explanation.
2. For confirmed or conditional issues, state who can trigger them, the required
   conditions, the likely impact and a concrete fix.
3. Propose a verification or regression test for the fixes.
4. Report additional issues you discover, with evidence.
5. Choose the three things you would investigate or fix first, explaining why.
6. Describe one uncertainty and one tool suggestion you independently checked.

A small patch for one issue is optional. A clear explanation and verification plan
are sufficient. Do not spend the whole exercise trying to produce a polished UI,
a long penetration-test report, or a high count of findings.

## Working assumptions

Use the provided local/Compose configuration as the baseline. Distinguish risks
in that configuration from concerns that require a hypothetical production setup.
Scanner priority is an initial label, not an instruction to accept its severity.
A successful HTTP response alone does not prove authorization is correct.

You may ask clarifying questions about intended behavior. We assess your reasoning,
not whether you memorize an exploit, agree with every scanner alert, or use a
particular vendor's AI tool.
