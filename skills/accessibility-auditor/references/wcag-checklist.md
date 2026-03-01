# WCAG 2.1 AA Compliance Checklist

This checklist covers all WCAG 2.1 Level A and Level AA success criteria relevant to web content auditing. Each item includes the criterion number, a plain-language description, and a concrete test procedure.

---

## 1. Perceivable

Content must be presentable to users in ways they can perceive.

### 1.1 Text Alternatives

- [ ] **1.1.1 Non-text Content (A)**: Every `<img>`, `<svg>`, `<canvas>`, and `<video>` element has a text alternative.
  - **Test**: Check that all `<img>` elements have a non-empty `alt` attribute. Decorative images must have `alt=""`. Icon fonts must have `aria-label` or be `aria-hidden="true"` with adjacent text.
  - **Common failures**: Images with `alt="image"`, `alt="photo"`, or the filename as alt text.

### 1.2 Time-Based Media

- [ ] **1.2.1 Audio-only and Video-only (A)**: Pre-recorded audio has a transcript. Pre-recorded video-only has a text or audio description.
  - **Test**: Locate all `<audio>` and `<video>` elements. Verify an adjacent transcript link or `<track kind="descriptions">`.

- [ ] **1.2.2 Captions (Pre-recorded) (A)**: All pre-recorded video with audio has synchronized captions.
  - **Test**: Check for `<track kind="captions">` on `<video>` elements. Verify captions are accurate and synchronized.

- [ ] **1.2.3 Audio Description or Media Alternative (A)**: Pre-recorded video has audio description or a full text alternative.
  - **Test**: Check for `<track kind="descriptions">` or an adjacent text transcript.

- [ ] **1.2.4 Captions (Live) (AA)**: Live video with audio has real-time captions.
  - **Test**: If the site hosts live video, verify caption support is available.

- [ ] **1.2.5 Audio Description (Pre-recorded) (AA)**: Pre-recorded video has audio description for visual-only information.
  - **Test**: Check for a secondary audio track or `<track kind="descriptions">`.

### 1.3 Adaptable

- [ ] **1.3.1 Info and Relationships (A)**: Information, structure, and relationships conveyed visually are available programmatically.
  - **Test**: Verify headings use `<h1>`-`<h6>` tags (not styled `<div>` or `<span>`). Tables use `<th>` headers. Lists use `<ul>`/`<ol>`/`<li>`. Form groups use `<fieldset>`/`<legend>`.

- [ ] **1.3.2 Meaningful Sequence (A)**: Reading order in the DOM matches the visual order.
  - **Test**: Linearize the page (disable CSS) and verify content reads in a logical order.

- [ ] **1.3.3 Sensory Characteristics (A)**: Instructions do not rely solely on shape, size, location, or sound.
  - **Test**: Search for text like "click the round button", "the red text above", "the item on the left". These must be supplemented with non-visual identifiers.

- [ ] **1.3.4 Orientation (AA)**: Content is not restricted to a single display orientation unless essential.
  - **Test**: Rotate the viewport between portrait and landscape. Content must remain functional.

- [ ] **1.3.5 Identify Input Purpose (AA)**: Input fields that collect user information have programmatic purpose.
  - **Test**: Check that form fields for name, email, phone, address use the `autocomplete` attribute with appropriate values.

### 1.4 Distinguishable

- [ ] **1.4.1 Use of Color (A)**: Color is not the only visual means of conveying information.
  - **Test**: View the page in grayscale. All information must still be distinguishable (e.g., error states use icons + text, not just red color).

- [ ] **1.4.2 Audio Control (A)**: Auto-playing audio lasting more than 3 seconds has a pause/stop mechanism.
  - **Test**: Load the page and listen for auto-playing audio. Verify controls are present.

- [ ] **1.4.3 Contrast (Minimum) (AA)**: Text has a contrast ratio of at least 4.5:1 (normal text) or 3:1 (large text).
  - **Test**: Use a contrast checker tool on all text/background color combinations. Large text is >= 18px regular or >= 14px bold.

- [ ] **1.4.4 Resize Text (AA)**: Text can be resized up to 200% without loss of content or functionality.
  - **Test**: Set browser zoom to 200%. Verify no content is clipped, overlapped, or requires horizontal scrolling.

- [ ] **1.4.5 Images of Text (AA)**: Text is used instead of images of text, except for logos and essential images.
  - **Test**: Check for text rendered as images (common in hero banners, buttons). These should use real text with CSS styling.

- [ ] **1.4.10 Reflow (AA)**: Content reflows at 320px CSS width (equivalent to 400% zoom at 1280px) without horizontal scrolling.
  - **Test**: Set viewport to 320px width. Verify all content is accessible without horizontal scrolling, except for data tables, maps, and diagrams.

- [ ] **1.4.11 Non-text Contrast (AA)**: UI components and graphical objects have a contrast ratio of at least 3:1 against adjacent colors.
  - **Test**: Check form field borders, icon colors, chart elements, and interactive component boundaries.

- [ ] **1.4.12 Text Spacing (AA)**: Content adapts when text spacing is increased (line height 1.5x, letter spacing 0.12em, word spacing 0.16em, paragraph spacing 2x).
  - **Test**: Apply these CSS overrides and verify no content is clipped or overlapped.

- [ ] **1.4.13 Content on Hover or Focus (AA)**: Hover/focus-triggered content (tooltips, dropdowns) is dismissible, hoverable, and persistent.
  - **Test**: Trigger tooltips and verify: Escape key dismisses them, mouse can move to the tooltip without it disappearing, tooltip stays visible until dismissed.

---

## 2. Operable

User interface components and navigation must be operable.

### 2.1 Keyboard Accessible

- [ ] **2.1.1 Keyboard (A)**: All functionality is available from a keyboard.
  - **Test**: Unplug the mouse. Navigate the entire page using Tab, Shift+Tab, Enter, Space, Arrow keys, and Escape. All interactive elements must be reachable and operable.

- [ ] **2.1.2 No Keyboard Trap (A)**: Focus can always be moved away from any component.
  - **Test**: Tab through the entire page. Verify focus never gets stuck in a component. Test modals, embedded widgets, and video players specifically.

- [ ] **2.1.4 Character Key Shortcuts (A)**: Single character key shortcuts can be turned off, remapped, or are only active on focus.
  - **Test**: Check for keyboard shortcuts triggered by single letter keys. Verify they do not conflict with screen reader commands.

### 2.2 Enough Time

- [ ] **2.2.1 Timing Adjustable (A)**: Time limits can be turned off, adjusted, or extended (with at least 20 seconds warning).
  - **Test**: Identify any session timeouts, auto-advancing carousels, or timed interactions. Verify extension mechanisms.

- [ ] **2.2.2 Pause, Stop, Hide (A)**: Auto-updating content (carousels, tickers, auto-refresh) can be paused, stopped, or hidden.
  - **Test**: Identify all auto-moving or auto-updating content. Verify pause controls are present.

### 2.3 Seizures and Physical Reactions

- [ ] **2.3.1 Three Flashes or Below (A)**: No content flashes more than 3 times per second.
  - **Test**: Review animations and video content for rapid flashing. Check CSS animations for high-frequency property changes.

### 2.4 Navigable

- [ ] **2.4.1 Bypass Blocks (A)**: A mechanism exists to bypass repeated blocks of content.
  - **Test**: Verify a "Skip to main content" link is the first focusable element. It may be visually hidden but must appear on focus.

- [ ] **2.4.2 Page Titled (A)**: Pages have descriptive, unique titles.
  - **Test**: Check `<title>` element. Must describe the page content and be unique across the site.

- [ ] **2.4.3 Focus Order (A)**: Focus order is logical and sequential.
  - **Test**: Tab through the page. Focus must move in a predictable order that matches the visual layout.

- [ ] **2.4.4 Link Purpose (In Context) (A)**: The purpose of each link can be determined from the link text or its context.
  - **Test**: Check for ambiguous link text: "click here", "read more", "learn more", "more". These must be supplemented with `aria-label` or surrounding context.

- [ ] **2.4.5 Multiple Ways (AA)**: At least two ways to locate a page within a site (e.g., navigation + search + sitemap).
  - **Test**: Verify the site provides at least two navigation mechanisms.

- [ ] **2.4.6 Headings and Labels (AA)**: Headings and labels describe their topic or purpose.
  - **Test**: Review all headings and form labels for descriptive accuracy.

- [ ] **2.4.7 Focus Visible (AA)**: Keyboard focus indicator is visible on all interactive elements.
  - **Test**: Tab through the page and verify every focused element has a visible indicator with at least 3:1 contrast.

### 2.5 Input Modalities

- [ ] **2.5.1 Pointer Gestures (A)**: Multipoint or path-based gestures have single-pointer alternatives.
  - **Test**: Check for pinch-zoom, swipe, or drag-and-drop interactions. Verify alternative controls (buttons, taps) exist.

- [ ] **2.5.2 Pointer Cancellation (A)**: For single-pointer actions, at least one of the following: up-event fires the action, abort/undo is available, up-event reverses down-event.
  - **Test**: Click and hold on interactive elements, then drag away before releasing. The action must not fire.

- [ ] **2.5.3 Label in Name (A)**: The accessible name of a component contains the visible label text.
  - **Test**: Compare `aria-label` or `aria-labelledby` text with the visible label. The visible text must be included in the accessible name.

- [ ] **2.5.4 Motion Actuation (A)**: Device motion triggers (shake, tilt) have UI alternatives and can be disabled.
  - **Test**: Check for motion-activated features and verify button/touch alternatives exist.

---

## 3. Understandable

Content and operation must be understandable.

### 3.1 Readable

- [ ] **3.1.1 Language of Page (A)**: The `<html>` element has a `lang` attribute matching the page content.
  - **Test**: Check `<html lang="...">`. Value must be a valid BCP 47 language tag (e.g., `en`, `en-US`, `fr`).

- [ ] **3.1.2 Language of Parts (AA)**: Content in a different language from the page default has a `lang` attribute.
  - **Test**: Search for foreign-language text blocks and verify `lang` attributes on their container elements.

### 3.2 Predictable

- [ ] **3.2.1 On Focus (A)**: Receiving focus does not initiate a change of context.
  - **Test**: Tab to each interactive element. No page navigation, form submission, or modal opening should occur on focus alone.

- [ ] **3.2.2 On Input (A)**: Changing a form input does not automatically initiate a change of context unless the user is warned.
  - **Test**: Change select dropdowns, radio buttons, and checkboxes. Verify no unexpected navigation or form submission occurs.

- [ ] **3.2.3 Consistent Navigation (AA)**: Navigation menus appear in the same relative order across pages.
  - **Test**: Compare navigation across 3+ pages. Menu items must appear in the same order.

- [ ] **3.2.4 Consistent Identification (AA)**: Components with the same function are identified consistently.
  - **Test**: Check that search fields, login buttons, and other repeated components have the same label across pages.

### 3.3 Input Assistance

- [ ] **3.3.1 Error Identification (A)**: Errors are identified and described to the user in text.
  - **Test**: Submit forms with invalid data. Verify error messages are displayed, identify the field, and describe the error.

- [ ] **3.3.2 Labels or Instructions (A)**: Form inputs have labels or instructions.
  - **Test**: Check every input for an associated `<label>`, `aria-label`, or `aria-labelledby`. Placeholder text alone is not sufficient.

- [ ] **3.3.3 Error Suggestion (AA)**: Error messages suggest how to fix the error when possible.
  - **Test**: Trigger validation errors and verify messages include corrective guidance (e.g., "Enter a valid email address like name@example.com").

- [ ] **3.3.4 Error Prevention (Legal, Financial, Data) (AA)**: Submissions that cause legal, financial, or data changes are reversible, checked, or confirmed.
  - **Test**: Check for confirmation steps before purchases, account deletions, or legal agreements.

---

## 4. Robust

Content must be robust enough for diverse user agents and assistive technologies.

### 4.1 Compatible

- [ ] **4.1.1 Parsing (A)**: HTML is well-formed with no duplicate IDs, proper nesting, and complete start/end tags.
  - **Test**: Run HTML through the W3C validator. Check for duplicate `id` attributes on the page.

- [ ] **4.1.2 Name, Role, Value (A)**: Custom components have appropriate ARIA name, role, and value.
  - **Test**: Inspect custom widgets (tabs, accordions, sliders) for correct ARIA roles and states. Verify state changes (expanded/collapsed) are announced.

- [ ] **4.1.3 Status Messages (AA)**: Status messages (success, error, progress) are announced to screen readers without receiving focus.
  - **Test**: Trigger form submissions, loading states, and notifications. Verify `aria-live` regions announce the updates.

---

## Quick Audit Workflow

For a rapid WCAG audit, check these high-impact items first:

1. **Contrast**: Run an automated contrast checker on the full page
2. **Keyboard**: Tab through the entire page without a mouse
3. **Headings**: Verify heading hierarchy with a browser extension
4. **Images**: Check all images for meaningful alt text
5. **Forms**: Verify all inputs have labels and error states are announced
6. **Focus**: Verify all interactive elements have visible focus indicators

These six checks catch approximately 70% of accessibility issues.
