# Bluejacket RX square planar spiral NFC antenna viewer

The static viewer in web/nfc-viewer is titled 13.56 MHz Square Planar Spiral NFC Antenna for Bluejacket RX Vending Machines and displays the 1.7 mm pitch winding prototype. Public descriptions explain the components and their intended functions in the vending system. Geometry provenance and validation limits are retained in this engineering document. It requires a current browser with JavaScript and WebGL. The model is 1.02 mm outside diameter wire, five available turns, a 330.2 mm square frame with a 304.8 mm clear opening and an integrated upright housing. Covers, carriers, boards and wiring can be shown separately. Rotation, camera views, an exploded view slider, touch pinch zoom and GLB download are included.

This prototype is separate from the Rev A3 custom controller and PCB panel. It depicts the purchased PN5180 module and a wire winding experiment. It does not establish label compatibility, complete refresh range, electrical matching or measured RF performance.

## Publish with GitHub Pages

GitHub repository file previews do not execute the viewer. Use GitHub Pages or another static website host to serve the site.

The included Publish NFC viewer workflow runs only when manually dispatched. Merging this change does not publish anything by itself. In the repository, open Settings, then Pages and select GitHub Actions as the source. After merging, open Actions, select Publish NFC viewer and run it from main. The deployed address is reported by the workflow. For this repository the expected project address is https://liberty-chris.github.io/trXb5/ . This is an expected address, not evidence that the site is live.

The workflow uploads ONLY web/nfc-viewer. It does not publish the repository root, private engineering documents, vendor software or firmware. The published model and logos can be downloaded by website visitors. Review that intended public content before running the workflow.

The repository is currently private. GitHub Pages from a private repository requires a supported paid GitHub plan. A private repository does not by itself make the published site private. If that plan is unavailable, use a separate public repository containing only web/nfc-viewer, or upload that directory to an existing static web host. Keep the engineering repository private unless its owner deliberately chooses otherwise. No visibility changes are made by this PR.

Official references: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages and https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site .

## Model and browser behavior

All asset paths are relative, so the page works at a project path or below an existing website directory. There are no external scripts, fonts, analytics, logins or model hosting services. The compressed model is approximately 1.1 MB and decompresses locally to a standard GLB file of approximately 7.3 MB. The browser model download is the decompressed GLB with conventional metre units. CAD source assembly coordinates use millimetres.

The web viewer requires DecompressionStream for gzip decoding and WebGL for drawing. Unsupported browsers receive an error instead of a silent blank page. The compressed model has a content fingerprint in its filename to avoid stale model caching when the page is updated.

The model contains 224 named meshes. XIAO board outline and component positions were derived from Seeed's XIAO STM32C5 KiCad project. Some component bodies and heights are simplified. PN5180 dimensions and package layout are nominal and the matching board is a placement concept. The original small PCB antenna is shown mechanically but requires electrical isolation before using the large winding. No completed tuning circuit is implied by the illustration.

## Branding and attribution

Balto uses the owner supplied black and white husky logo uploaded on November 18, 2026. The image is preserved without redrawing.

ROACH uses the wordmark and emblem geometry from the owner's existing ROACH V5 enclosure package. Its source note identifies the lettering as traced from the supplied original and the emblem as a symmetric reconstruction of an angled reference. These are existing project assets rather than newly invented branding. The web SVG files preserve that geometry with a dark fill.

Seeed Studio source: https://files.seeedstudio.com/wiki/XIAO_STM32C5/res/XIAO_STM32C5_v1.0_SCH%26PCB.zip . The hardware schematic identifies CC BY SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/ . This attribution applies to the simplified geometry derived from that source. It does not assign a new license to this repository or the owner's brands.

## Validation

JavaScript syntax, gzip decompression, the model checksum, GLB parsing, all 224 component buffers, camera and explode controls, group visibility and the 7,312,760 byte model download were checked in a Node API harness. The harness uses stand in DOM and WebGL methods and does not verify real GPU rendering or visual layout. A local Chromium launch was blocked by the execution container's socket restrictions, so a real browser and phone visual check remain open before public signoff.

To preview locally, serve web/nfc-viewer with a static HTTP server and open its index.html. Opening index.html directly from disk is not supported by this web distribution because it fetches a separate compressed model. The earlier standalone HTML distribution remains suitable for offline use.
