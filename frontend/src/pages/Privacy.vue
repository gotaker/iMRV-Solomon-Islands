<script setup>
import EditorialStub from '@/components/EditorialStub.vue'
</script>

<template>
  <EditorialStub
    eyebrow="(Index 00) Privacy"
    title-a="Privacy"
    title-b="Statement."
    lede="How the iMRV platform handles personal information collected through public access, contributor accounts, and the open data API."
    contact-subject="iMRV Privacy Policy Inquiry"
    :body-paragraphs="[
      'iMRV is operated by the Climate Change Division of the Ministry of Environment, Climate Change, Disaster Management and Meteorology (MECDM), Government of Solomon Islands. The platform serves two audiences: the public, who can browse the project ledger and GHG inventory without authentication, and registered contributors who maintain that data on behalf of agencies.',
      'For public visitors, the platform records standard server access logs (IP address, user-agent, timestamps, requested URLs) for at most 90 days. These logs are used for security monitoring, capacity planning, and abuse prevention. They are not shared with third parties and are not used for advertising or analytics profiling.',
      'For registered contributors, the platform stores the email address used at sign-up, role assignments, and an audit trail of changes made through the desk interface. This information is retained for the lifetime of the account plus the statutory record-keeping period required by the Government of Solomon Islands.',
      'iMRV does not deploy third-party trackers, social-media pixels, or behavioural advertising. The only cookies set are a session cookie (frappe_*) for logged-in contributors and a CSRF cookie used to protect form submissions. Both are first-party and removed when you sign out or close the browser.',
      'Subject access, correction, and deletion requests should be sent to the address below; the Climate Change Division will respond within 21 working days.',
    ]"
  />
</template>
