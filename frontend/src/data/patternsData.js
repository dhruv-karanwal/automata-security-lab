/**
 * Centralized Regular Expression Rule Catalogue
 * Configured patterns for URL, Email, Suspicious Phrases, and Exclamations
 */

export const PATTERNS_DATA = [
  {
    id: "RULE-URL",
    name: "HTTP/HTTPS URL Recognition",
    regex: "https?:\\/\\/[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}(\\/[^\\s]*)?",
    detects: "Web links starting with http:// or https://",
    exampleMatch: "https://example.com/verify-account",
    limitation: "Matches legitimate web links (e.g. genuine corporate websites or unsubscribe links)."
  },
  {
    id: "RULE-EMAIL",
    name: "Email Address Recognition",
    regex: "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
    detects: "Email addresses in the subject or body",
    exampleMatch: "support@service-auth.com",
    limitation: "Matches genuine sender or contact email addresses indiscriminately."
  },
  {
    id: "RULE-PHRASE-WIN",
    name: "Suspicious Phrase: WIN PRIZE NOW",
    regex: "\\bWIN\\s+PRIZE\\s+NOW\\b",
    detects: "Immediate prize reward lure phrase",
    exampleMatch: "WIN PRIZE NOW",
    limitation: "May flag genuine promotional marketing sales announcements."
  },
  {
    id: "RULE-PHRASE-CLAIM",
    name: "Suspicious Phrase: CLAIM REWARD NOW",
    regex: "\\bCLAIM\\s+REWARD\\s+NOW\\b",
    detects: "Urgent reward redemption call to action",
    exampleMatch: "CLAIM REWARD NOW",
    limitation: "May flag loyalty program customer service communications."
  },
  {
    id: "RULE-PHRASE-VERIFY",
    name: "Suspicious Phrase: ACCOUNT VERIFY IMMEDIATELY",
    regex: "\\bACCOUNT\\s+VERIFY\\s+IMMEDIATELY\\b",
    detects: "Urgent account verification ultimatum",
    exampleMatch: "ACCOUNT VERIFY IMMEDIATELY",
    limitation: "May flag official IT security compliance requests."
  },
  {
    id: "RULE-EXCLAMATION",
    name: "Repeated Exclamation Marks",
    regex: "!{2,}",
    detects: "Two or more consecutive exclamation marks (!!+)",
    exampleMatch: "Action required immediately!!!",
    limitation: "Informal, excited, but benign interpersonal emails also use repeated exclamation marks."
  }
];
