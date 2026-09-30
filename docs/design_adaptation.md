# Design adaptation: Car Rental → Paradigm Diagnostics

The Mapua University Group 4 team adapted five files from the lead developer’s previous Java Car Rental project for Paradigm Diagnostics. Their source comments describe that project; they do not add requirements such as authentication, rental management, or copying its business logic into this app.

## Reference mapping

| Selected reference | Python adaptation |
| :--- | :--- |
| `UIAssets.java` | Light/dark palette, typography hierarchy, four shades of green, subtle borders, and shared style factories in `ui/ui_assets.py` |
| `LoginGUI.java` | Split branding/setup launcher, large welcome heading, four-shade green brand mark, primary/secondary actions |
| `SignUpChoiceGUI.java` | Comparison-pair choices in the launcher and actionable demonstration cards in the dashboard |
| `AdminDashboardGUI.java` | Product title and subtitle in the top bar, collapsible sidebar, active green navigation, persistent content pages |
| `Main.java` | Native UI event-loop discipline; Python's main thread owns Tk while a worker handles comparisons |

The actual Java dashboard calls `getSurface()` for its sidebar and top bar, even though some comments and unused chrome constants suggest an always-dark surface. The adaptation follows that actual theme-aware behavior: a white shell in light mode and near-black surfaces in dark mode.

## Deliberate changes

The earlier application required sharp corners and fixed eight-panel positions. The new request explicitly changes the overall design, so the interface now uses shared 8-pixel control radii and 12-pixel showcase/badge radii, a shell/content layout, and persistent pages. These values remain centralized rather than scattered through panel code.

The launcher opens in light mode, matching the selected Java project's default. It remembers the user's selected appearance during the launcher-to-dashboard handoff. All functional pages work in either appearance.

Native macOS window controls remain available. The Java project uses undecorated windows and a custom title bar; recreating that mechanism would add dragging, focus, minimize, and accessibility work without helping the language demonstration. The in-app top bar provides the visual identity while native controls handle window management.

The car photograph and account roles are replaced with programming-specific content. A small factorial showcase introduces the subject. Pair cards select Python/JavaScript or Python/C++; individual selectors also allow other supported combinations. No image downloads, authentication services, or Java dependencies are needed.

## State and navigation logic

- `_new_page()` creates each page once.
- `_show_page()` changes page visibility and navigation styling. Editors and the lesson input preset remain alive, so source is preserved across navigation.
- `_toggle_sidebar()` changes sidebar width and label presentation. Editor/grid resize notifications update the gutters automatically.
- `_select_lesson()` loads the appropriate source variants and returns to the workspace. It does not execute code automatically.
- `_refresh_report_page()` shows a processing message, the completed snapshot, or an empty-state explanation. Changing source, language, timeout, or the loaded lesson clears previous evidence on both the workspace and report page.
- Result-view buttons independently style their selected/inactive text to preserve contrast in both themes.
- All lesson-loading and editing controls disable during a comparison. Navigation remains available; it cannot mutate the worker's source snapshot.

## Editor and workspace refinements

Both source editors use independent line-number canvases and Pygments syntax tags. Gutters attach scroll callbacks to native Tk text widgets for wrapper compatibility. Syntax tags follow the selected language and theme, preserve source and undo, and handle supplementary Unicode characters.

The launcher offers **Start with empty editors**. **Clear results** retains source; **Clear workspace** also clears both editors and preset stdin. Both actions are unavailable during a comparison. Lessons supply finite input presets; there is no editable stdin panel or separate Guide page. Demonstration cards use responsive summaries, aligned actions, and local **View Lesson** PDF links.

**Back to Menu** preserves appearance and the native window while disposing of the workspace, cancelling work and callbacks. It does not retain unsaved source or reports. Moving among dashboard pages retains them.

## Verification

The native smoke test covers launcher preset selection and theme handoff, all three dashboard pages (Workspace, Demonstrations, and Reports), green active navigation, source preservation, collapse/expand behavior, library actions, report freshness, and essential control bounds at the supported minimum window size. Existing checks still exercise line numbers, both scroll directions, source editing, execution, errors, cancellation, file opening, and export.

The finalization smoke script also covers clearing, empty startup, card layout, PDF action routing, and menu cancellation; external PDF open calls are mocked. The syntax smoke script checks token tags, Unicode, selection, undo, theme, and cleanup. Recorded results are in [project documentation](documentation.md#10-testing-and-results).

The backend is independent of the redesigned UI and retains the same comparison/execution contracts. Desktop screenshot review remains unavailable unless Computer Use permission is enabled; native layout and callback checks provide functional evidence, not a claim of pixel-by-pixel visual inspection.

## Entry transition refinement

The entry and workspace are child frames of `Application`, which owns one native Tk window. Opening the workspace swaps content without destroying, withdrawing, recentering, or recreating that window. Language and appearance choices are passed directly to the new page. Native tests verify window identity, visibility, and unchanged geometry through the transition.

The latest visual refinement changes accent colors to terminal greens and enlarges the product title/subtitle after removing the G4 badge. Existing shapes, cards, navigation, and editor components retain their design.
