# Asset Assistant Distribution & Sustainability Roadmap

This document extends the main Asset Assistant roadmap with the work required to make the Blender project installable, discoverable, maintainable, and financially sustainable without requiring a paid advertising budget. Product quality remains the priority: distribution and growth work should support a useful tool rather than distract from building one.

## Principles

1. Keep Asset Assistant free and open source.
2. Do not lock core functionality behind payment, registration, or sponsorship.
3. Make installation, upgrades, and releases as low-friction and repeatable as practical.
4. Prefer distribution channels where Blender users already discover extensions instead of building a separate acquisition system first.
5. Keep promotion lightweight. Do not make regular development videos a requirement for project growth.
6. Reuse product screenshots, release notes, documentation, and real user outcomes as marketing material.
7. Ask for support without guilt or pressure: donations support continued development; they are not payment required to use the software.
8. Measure real adoption before spending money or significant development time on marketing infrastructure.
9. Preserve the artist-first message: Asset Assistant exists to empower artists and remove repetitive technical friction, not replace creative judgment.

## P0 - Modern Blender and extension readiness

Official Blender extension distribution depends on a modern Blender-compatible package. This work should align with the main roadmap's modern-Blender verification rather than becoming a separate compatibility effort.

- [ ] Select and document the primary supported modern Blender version.
- [ ] Verify the complete Generate -> Rig -> Animate -> Validate -> Export workflow on that version.
- [ ] Add the metadata/manifest required for modern Blender extension packaging.
- [ ] Ensure the packaged extension installs cleanly through Blender's supported extension/add-on installation workflow.
- [ ] Validate the extension package with Blender's extension tooling where applicable.
- [ ] Decide and document the support policy for older Blender versions, including Blender 2.92.
- [ ] Ensure licensing, source availability, documentation, and extension behavior remain compatible with official Blender distribution requirements.

Definition of done: Asset Assistant can be built as a reproducible modern Blender extension package and installed into the documented supported Blender version without repository-specific/manual setup.

## P0 - Reproducible release pipeline

Deployment should become part of the repository rather than a manual checklist that must be rediscovered for every release.

- [ ] Define semantic/versioned releases for Asset Assistant.
- [ ] Add automated extension/package build steps to CI.
- [ ] Run core tests and Blender integration tests before producing a release artifact.
- [ ] Run extension/package validation before release where supported.
- [ ] Produce a deterministic distributable ZIP/artifact from the release pipeline.
- [ ] Create a GitHub Release workflow for tagged versions, including the installable artifact and release notes.
- [ ] Document the release procedure and rollback/fix-forward procedure.
- [ ] Keep signing, credentials, tokens, or publishing secrets out of source control.

Definition of done: a maintainer can create a tested, validated Asset Assistant release without manually assembling the package.

## P1 - Official Blender Extensions distribution

Once Asset Assistant is useful, stable enough for outside users, and compatible with the current extension requirements, use the official Blender extension ecosystem as the primary discovery/install path.

- [ ] Review the current Blender Extensions submission and moderation requirements immediately before submission.
- [ ] Prepare listing name, concise description, documentation links, compatibility information, license information, screenshots, and support links.
- [ ] Submit a release candidate for official review when the product meets the required quality bar.
- [ ] Address moderation/review feedback without weakening project architecture or artist-first principles.
- [ ] Document how users install and update through Blender after publication.
- [ ] Keep GitHub releases available as a direct/open-source distribution path where appropriate.

Definition of done: a Blender user can discover Asset Assistant through an appropriate Blender distribution channel, install it with minimal friction, and reach its documentation/source repository.

## P1 - Donations and project sustainability

The first sustainability mechanism should be simple and should not create a second product to maintain.

- [ ] Set up GitHub Sponsors for the maintainer/project if eligible.
- [ ] Start with a small number of simple one-time/monthly sponsorship options rather than complex reward tiers.
- [ ] Add a tasteful Sponsor/support section to the GitHub repository and other permitted project listings.
- [ ] Use clear language such as: "Asset Assistant is free and open source. If it saves you time, you can sponsor continued development."
- [ ] Do not put core features, updates, fixes, or documentation behind sponsorship.
- [ ] Do not add donation prompts inside Blender where platform/distribution rules prohibit them.
- [ ] Re-evaluate additional donation platforms only if users demonstrate demand for an alternative to GitHub Sponsors.

Definition of done: users who voluntarily want to support continued Asset Assistant development have one clear, low-friction way to do so without affecting access to the software.

## P1 - Zero-budget launch assets

Do not require a recurring video/content-production schedule. Create a small reusable set of assets when the product is visually ready to show.

- [ ] Capture 3-5 strong screenshots demonstrating the real workflow and output.
- [ ] Include at least one generated asset, the Asset Assistant Blender UI, validation/readiness, and a successful downstream-engine result when available.
- [ ] Add a concise visual introduction to the GitHub README so the repository can initially serve as the project website.
- [ ] Reuse the same approved screenshots and product description for GitHub, Blender listings, documentation, release notes, and community posts.
- [ ] Keep screenshots truthful to the released version; do not market unreleased or manually repaired output as automatic behavior.
- [ ] Do not build a standalone marketing website until adoption demonstrates that it would solve a real problem.

Definition of done: the project has enough reusable visual/product material to explain itself clearly without requiring ongoing video production or paid creative work.

## P1 - Organic discovery and feedback

Promotion should initially be participation-oriented rather than ad-oriented.

- [ ] Publish the first useful releases through GitHub and the appropriate Blender distribution channel.
- [ ] Make issue reporting, feature requests, documentation, and contribution paths easy to find.
- [ ] Share meaningful releases selectively with relevant Blender/game-development communities where self-promotion rules allow it.
- [ ] Lead with the problem solved, actual workflow/result, open-source availability, and request for feedback rather than promotional hype.
- [ ] Avoid spam, repetitive cross-posting, and claims that Asset Assistant replaces artists.
- [ ] Treat early user problems as product research: convert recurring feedback into roadmap issues/tests where appropriate.
- [ ] Encourage community screenshots/examples only when users voluntarily want to share them.

Definition of done: new users have at least a few sustainable ways to discover the project and a clear way to provide actionable feedback, without paid advertising.

## P2 - Adoption measurement

Do not optimize vanity metrics in isolation. Use lightweight measurements to determine whether additional investment is justified.

Track where practical:

- release/extension downloads;
- GitHub stars and watchers as weak discovery signals;
- issue volume and issue quality;
- repeat contributors and pull requests;
- documentation/support friction;
- sponsorship count and recurring support;
- downstream target/provider usage when users voluntarily report it.

Questions to answer periodically:

1. Are people actually installing Asset Assistant?
2. Do they successfully reach a useful result?
3. Where do they get stuck?
4. Which features/providers/targets are creating repeat use?
5. Are users recommending or contributing to the project without being prompted?
6. Is sponsorship meaningful enough to justify additional sustainability work?

Do not add invasive telemetry merely to obtain these numbers. Prefer aggregate platform-provided metrics and voluntary community feedback unless a future telemetry design has a clear user benefit and explicit privacy model.

## P2 - Growth experiments only after product signal

Consider these only after the project demonstrates real adoption:

- a dedicated project website/domain;
- additional funding platforms;
- occasional short demo/release videos when the value clearly exceeds the production effort;
- community showcases or example galleries;
- contributor recognition;
- partnerships/integrations with complementary open-source game-development tools;
- more structured release announcements.

Paid advertising is intentionally not a prerequisite and should not be added to the roadmap merely because it is a conventional marketing tactic.

## Suggested rollout

1. Continue core Asset Assistant development and target verification.
2. Move the supported Blender baseline to a modern version.
3. Make Asset Assistant a valid modern Blender extension package.
4. Automate testing, validation, packaging, and GitHub release creation.
5. Reach a useful alpha quality bar before seeking broad attention.
6. Set up GitHub Sponsors and a restrained repository support message.
7. Capture a small reusable screenshot set from the real product.
8. Release to a small group of early testers and fix installation/workflow friction.
9. Submit to the official Blender extension ecosystem when requirements and quality are satisfied.
10. Make a small number of targeted community announcements and ask for feedback.
11. Measure adoption, issues, contributions, and sponsorship before deciding whether larger growth work is justified.

## Relationship to the main roadmap

Distribution work should not replace the immediate engineering priorities in `docs/roadmap.md`. Modern Blender compatibility is the bridge between the two roadmaps and should be coordinated as one workstream. Human Provider 1.0 remains the near-term product milestone; distribution work should make that milestone easy to install and discover once it is genuinely useful.

The project should avoid a common failure mode: spending significant time marketing an impressive promise while the actual artist workflow remains immature. The preferred loop is:

`Build something useful -> package it well -> make it easy to discover -> listen to users -> improve it -> repeat`
