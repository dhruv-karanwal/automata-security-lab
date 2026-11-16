/**
 * Synthetic Sample Emails for Demonstration & Viva Presentation
 */

export const SAMPLE_EMAILS = [
  {
    id: "sample_a",
    label: "A. Suspicious sequence",
    subject: "Congratulations on your reward",
    body: "WIN PRIZE NOW",
    summary: "Matches DFA sequence and NFA Branch 1."
  },
  {
    id: "sample_b",
    label: "B. Ordinary-looking email",
    subject: "Meeting agenda for tomorrow",
    body: "Hello team, please review the meeting agenda before tomorrow's discussion. Thank you.",
    summary: "Benign email. Does not match any configured rule."
  },
  {
    id: "sample_c",
    label: "C. URL pattern",
    subject: "Account notification",
    body: "Please review this link: https://example.com/verify-account!!! and confirm whether the account details are correct.",
    summary: "Matches URL and repeated exclamation marks regex."
  },
  {
    id: "sample_d",
    label: "D. Multiple patterns",
    subject: "Urgent account notice",
    body: "WIN PRIZE NOW. CLAIM REWARD NOW. ACCOUNT VERIFY IMMEDIATELY. Visit https://example.com/confirm!!!",
    summary: "Matches all three NFA branches, URL, and exclamation marks."
  }
];
