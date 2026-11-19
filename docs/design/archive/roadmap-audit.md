# Roadmap change audit

*Archived November 18, 2026: historical record of the November roadmap restructuring. Not a planning document; see the [design index](../README.md).*

Faculty audit, November 18, 2026. The comparison is between the current
`COURSE_ROADMAP.md` and the exact October version in Git commit `c5d5ee1`.
The [archived October roadmap](roadmap-october-2026.md) preserves
that complete original text, including historical status and open questions.

The restructuring did remove the explicit course-goals section and compress
some details without a specific instructor request to remove them. Some ideas
survived in other files; others were no longer explicit in the documents
checked. Those omissions are acknowledged below and restored in the current
roadmap rather than treated as deliberate scope decisions.

| Original section | Audit result |
| --- | --- |
| Course goals | The five original goals were dispersed or shortened. The explicit goals, including arms and simple mobile bases, cross-platform access, faculty/student boundaries, and permission/attribution for outside material, are restored in the roadmap. The base-first planning example also remains in the [planning brief](../../../instructor/briefs/path_planning.md). |
| Learning sequence | ROS/Python, transforms, FK, planning, vision, and learning remain. The instructor subsequently specified rotation matrices only, general FK without required DH, planar Jacobians, and optional project RL; those are intentional later decisions, not accidental omissions. |
| Student software environment | ROS 2, Compose, RViz, native architectures, workspace directories, platform instructions, and optional dev containers remain in the roadmap, [setup](../../setup.md), [Mac guide](../../macos.md), or [improvements](../../../instructor/IMPROVEMENTS.md). The explicit no-forced-emulation rule, same-tag multiarchitecture prebuilt-image goal, per-host measurement list, and fresh-clone validation were no longer all visible in the roadmap; they are restored there. |
| Faculty maintenance and releases | Faculty masters, an allowlist, separate generated copies, review, and no in-place stripping remain in the [release guide](../../../release_tools/README.md). Notebook stripping was deferred until needed, as recorded there and in the improvements list; this is an implementation decision, not a claim that notebooks are prohibited. Publication and instructor review remain open. |
| Roadmap and acceptance points | The task list retains the platform, release, homework, project, and compute gates. The original request to measure resources and establish an acceptable graphics-performance target is restored explicitly. The original simulator comparison included ROS 2 integration and Gazebo Harmonic as a candidate; those are restored as conditional evaluation details, while the instructor's later preference for a small kinematic baseline and optional MuJoCo remains the current direction. |
| October immediate steps | Apple Silicon and Windows observations and remaining platform checks are recorded in [TASKS.md](../../../TASKS.md) and the platform guides. The old instruction to create the first commit is historical: the repository now has commits and an `origin/main` tracking reference. Remote privacy and backup policy were not verified by this audit. The original text remains in the archive. |
| Open decisions | Course length, prerequisites, 2.5D task scope, and first-offering simulation/CPU constraints were subsequently supplied by the instructor. Course number, assessments, project scoring, publication, and hardware limits remain open. A choice being recorded does not approve any homework. |
| Research brief | The current roadmap had shortened the original assistant brief. Its requested resource types, software/maintenance details, simulator and RL comparisons, separation of verified facts from recommendations, matrix/pilot outputs, and three named reference repositories were no longer all explicit there. They are restored in the roadmap; the reference repositories are not assumed to be present. |

All HW01--HW09 handouts are faculty drafts awaiting careful instructor review.
This audit preserves the old plan as history; it does not silently reinstate
DH, a required RL project, or other scope that the instructor later changed.
