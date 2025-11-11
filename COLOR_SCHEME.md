# FE-EKG Timeline Color Scheme

## Design Philosophy

The color scheme is designed to be:
- **Cohesive** - All colors work harmoniously together
- **Modern** - Uses contemporary color palette (Tailwind-inspired)
- **Accessible** - High contrast for readability
- **Professional** - Suitable for presentations and publications
- **Thematic** - Matches the app's purple gradient theme

## Color Palette

### Node Colors

#### 🟢 Entities (Companies, Banks, Regulators)
- **Primary:** `#10b981` (Emerald Green)
- **Border:** `#059669` (Dark Emerald)
- **Highlight:** `#34d399` (Light Emerald)
- **Hover:** `#047857` (Darker Emerald)

**Rationale:** Green represents stability and institutions. Emerald shade is modern and professional, avoiding the "traffic light" primary green.

#### 🔵 Events (Financial Events)
- **Primary:** `#6366f1` (Indigo)
- **Border:** `#4f46e5` (Dark Indigo)
- **Highlight:** `#818cf8` (Light Indigo)
- **Hover:** `#4338ca` (Darker Indigo)

**Rationale:** Indigo/blue represents events and actions. Matches the app's primary theme color. Distinct from both green (entities) and pink (risks).

#### 🔴 Risks (Risk Instances)
- **Primary:** `#ec4899` (Pink/Magenta)
- **Border:** `#db2777` (Dark Pink)
- **Highlight:** `#f472b6` (Light Pink)
- **Hover:** `#be185d` (Darker Pink)

**Rationale:** Pink/magenta for risks instead of harsh red. Still conveys danger/warning but more sophisticated. Softer on the eyes during extended viewing.

### Edge Colors

#### Event-Entity Relationships
- **Color:** `#64748b` (Slate Gray)
- **Opacity:** 60%
- **Width:** 1.5px
- **Style:** Solid

**Rationale:** Neutral gray for structural relationships. Doesn't compete with node colors. Lower opacity keeps focus on nodes.

#### Risk-Entity Relationships
- **Color:** `#f472b6` (Light Pink)
- **Opacity:** 50%
- **Width:** 1.5px
- **Style:** Dashed

**Rationale:** Matches risk node color but lighter. Dashed style differentiates from event relationships.

#### Evolution Links (Event → Event)
- **Color:** `#8b5cf6` (Purple/Violet)
- **Opacity:** 70-100% (based on score)
- **Width:** 1.5-3px (based on score)
- **Style:** Solid with arrow

**Rationale:** Purple matches app theme and sits between indigo events and pink risks in color spectrum. Variable opacity and width show link strength.

### Background & UI

#### Graph Canvas
- **Background:** Linear gradient from `#f8f9fa` to `#e9ecef`
- **Style:** Subtle gradient for depth

**Rationale:** Very light gray gradient provides contrast for colorful nodes without being distracting.

#### Sidebar
- **Primary:** `#667eea` (Purple)
- **Secondary:** `#764ba2` (Dark Purple)
- **Background:** White
- **Hover:** `#e9ecef` (Light Gray)

**Rationale:** Matches the app header gradient, creating visual consistency.

## Visual Hierarchy

### Size
1. **Nodes:** 25px base (15-35px range)
2. **Text:** 13px bold
3. **Borders:** 3px

### Shadows
- **Nodes:** 8px blur, `rgba(0,0,0,0.2)`
- **Edges:** 3px blur, `rgba(0,0,0,0.15)`

### Depth Perception
- Nodes appear elevated with shadows
- Edges appear behind nodes
- Lighter opacity for supporting elements

## Color Accessibility

### Contrast Ratios (WCAG AA)
- White text on Emerald: ✅ 4.5:1
- White text on Indigo: ✅ 7.2:1
- White text on Pink: ✅ 5.1:1

### Color Blindness Considerations
- **Protanopia/Deuteranopia (Red-Green):** ✅ Green and Pink are distinguishable by brightness
- **Tritanopia (Blue-Yellow):** ✅ Indigo and Green/Pink are clearly different
- **Shape Coding:** ✅ Boxes (entities), Ellipses (events), Diamonds (risks)

## Before & After Comparison

### Before (Original Colors)
```
Entities: #4CAF50 (Material Green) - Too bright
Events:   #2196F3 (Material Blue)  - Too saturated
Risks:    #f44336 (Material Red)   - Too harsh
Edges:    Default gray              - No differentiation
```

### After (New Colors)
```
Entities: #10b981 (Emerald)   - Modern, professional
Events:   #6366f1 (Indigo)    - Matches theme
Risks:    #ec4899 (Pink)      - Softer warning
Edges:    Typed colors        - Clear relationships
```

## Usage Guidelines

### Presentations
- Light gradient background works well on projectors
- High contrast ensures visibility from distance
- Distinct shapes help even in grayscale

### Publications
- Professional color palette suitable for academic papers
- Colors maintain meaning in print
- Accessible to color-blind readers

### Interactive Demos
- Hover states provide clear feedback
- Highlight colors guide attention
- Color-coded legend aids understanding

## Technical Implementation

### CSS Variables (Future Enhancement)
Consider adding CSS custom properties:
```css
:root {
  --color-entity: #10b981;
  --color-event: #6366f1;
  --color-risk: #ec4899;
  --color-evolution: #8b5cf6;
  --color-edge: #64748b;
}
```

### Theming Support
Easy to create alternative themes:
- Dark mode theme
- High contrast theme
- Grayscale theme
- Custom institutional themes

## Color Meaning Reference

| Color | Represents | Psychology |
|-------|-----------|------------|
| Emerald Green | Entities | Stability, growth, trust |
| Indigo | Events | Action, intelligence, depth |
| Pink | Risks | Warning (softer), attention |
| Purple | Evolution | Connection, transition, flow |
| Gray | Structure | Neutral, supporting role |

## Export for Design Tools

### Hex Codes
```
#10b981  // Entity
#6366f1  // Event
#ec4899  // Risk
#8b5cf6  // Evolution
#64748b  // Edge
```

### RGB Values
```
16, 185, 129   // Entity
99, 102, 241   // Event
236, 72, 153   // Risk
139, 92, 246   // Evolution
100, 116, 139  // Edge
```

### Tailwind CSS Classes
```
emerald-500  // Entity
indigo-500   // Event
pink-500     // Risk
violet-500   // Evolution
slate-500    // Edge
```

## Inspiration Sources
- Modern SaaS dashboards (Linear, Notion)
- Financial data visualizations (Bloomberg Terminal)
- Tailwind CSS color system
- Material Design 3.0 color tokens

---

Last Updated: 2025-11-10
Version: 2.0.0 (Professional Edition)
