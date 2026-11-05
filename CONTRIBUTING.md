# Working on trXb5

Use focused branches for design revisions after this initial baseline. Describe the concrete circuit or documentation change and the validation performed. Update docs/STATUS.md when the project advances to a new stage.

Design evidence should include source URLs and revisions, exact component packages, calculation assumptions and measured conditions. Store captures and bench records under tests/bench with a commit identifier and hardware revision. Record failures and inconclusive results as well as successes.

Use hardware/controller for native controller KiCad projects and hardware/antenna for native panel projects. Store firmware and host tooling separately. Historical A0 material remains under hardware/reference/RevA0.

The repository does not currently grant an open source license. Do not copy third party implementations or binary distributions into it without reviewing their licenses and provenance. The independent protocol references can be used to guide interoperability research, with appropriate attribution.
