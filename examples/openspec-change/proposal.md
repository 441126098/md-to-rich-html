# Add Dark Mode Support

## Why

Users have repeatedly requested a dark theme for the dashboard. Telemetry shows
68% of users browse the app between 6pm and midnight, when bright UI causes eye
strain. A system-aware dark mode is now table stakes for any modern web product.

## What changes

- New theme context provider with `light` / `dark` / `auto` modes
- CSS custom properties replace all hard-coded colors in `tokens.css`
- Persisted user preference in `localStorage` under `ui.theme`
- New toggle component in the header navigation

## Impact

- Affects every page that consumes design tokens (~all of them)
- No backend changes
- One-time CSS migration; expected to land in v2.4

## ADDED Requirements

### Requirement: Theme Selection

The application SHALL provide three theme modes: light, dark, and auto.

#### Scenario: User selects dark mode explicitly

- **WHEN** the user clicks the theme toggle and selects "Dark"
- **THEN** the application SHALL apply dark theme tokens immediately
- **AND** persist the choice to `localStorage`
- **AND** keep this preference across browser restarts

#### Scenario: User leaves theme on auto

- **GIVEN** the user has not set a preference
- **WHEN** the operating system reports a dark color scheme via media query
- **THEN** the application SHALL apply dark theme tokens
- **AND** automatically switch when the OS preference changes

### Requirement: Token-driven Styling

All visible colors in the application SHALL come from CSS custom properties,
never hard-coded hex values.

#### Scenario: New component is added

- **WHEN** a developer adds a new component
- **THEN** the linter SHALL reject any non-token color values
- **AND** suggest the closest semantic token

## MODIFIED Requirements

### Requirement: Color Tokens (was: Hard-coded Brand Palette)

Previously the design tokens shipped only light-mode values. They MUST now
include a paired dark-mode value for every token.

#### Scenario: Token lookup at runtime

- **WHEN** a component reads `var(--color-surface)`
- **THEN** the browser SHALL resolve to the active theme's value
- **AND** transitions between themes SHALL be CSS-animated over 150ms

## REMOVED Requirements

### Requirement: Inline Style Color Overrides

The previous spec allowed components to override token values with inline
styles for "exceptional cases". This loophole is removed — there are no
exceptional cases.

## Implementation Tasks

- [x] 1.1 Add ThemeProvider component
- [x] 1.2 Wire context to root layout
- [x] 2.1 Define dark-mode token values in tokens.css
- [ ] 2.2 Audit existing components for hard-coded colors
- [ ] 2.3 Migrate found violations
- [ ] 3.1 Build toggle UI component
- [ ] 3.2 Add localStorage persistence
- [ ] 4.1 Add lint rule for non-token colors
- [ ] 5.1 Update Storybook to show both themes
- [ ] 5.2 Write migration notes for component authors
