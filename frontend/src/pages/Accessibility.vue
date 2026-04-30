<script setup>
import EditorialStub from '@/components/EditorialStub.vue'
</script>

<template>
  <EditorialStub
    eyebrow="(Index 00) Accessibility"
    title-a="Accessibility"
    title-b="Statement."
    lede="Our commitment to making climate accountability information available to every visitor — at every level of vision, motor, and connectivity capability."
    contact-subject="iMRV Accessibility Inquiry"
    :body-paragraphs="[
      'iMRV aims to meet WCAG 2.1 Level AA across the public-facing pages. We test the SPA against the screen-reader pairings most common in the region — VoiceOver on iOS and macOS, NVDA + Firefox on Windows — and against keyboard-only navigation. The desk interface, used by registered contributors, inherits Frappe v16 accessibility behaviour and is audited separately.',
      'Forest-and-Sage typography pairs Anton (display) with Inter (body) at sizes that hold their contrast ratio against cream and forest backgrounds. The minimum body text contrast is 7:1, the minimum eyebrow / micro-copy contrast is 4.5:1. Where reveal-on-scroll animations would prevent reading, prefers-reduced-motion is honoured: every transition is disabled and content lands at its final position immediately.',
      'Known accessibility gaps under active fix: a small subset of legacy report PDFs in the Knowledge Resources library are scans without OCR text layers; we are re-tagging those with searchable text. The drawer navigation in the desk interface is keyboard-trappable but does not yet expose a roving tabindex on its accordion sub-menus.',
      'Where accessibility falls short of what you expected, please let us know. We use field reports as the primary input to our quarterly accessibility iteration plan, and respond to every report individually.',
    ]"
  />
</template>
