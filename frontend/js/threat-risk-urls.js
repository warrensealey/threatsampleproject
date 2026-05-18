/**
 * Symantec WebFilter threat risk test URLs (levels 1–10).
 * Source: https://sitereview.bluecoat.com/#/threat-risk-test-pages
 */
const THREAT_RISK_BASE_URL =
  'http://testrating.webfilter.bluecoat.com/threatrisk/level/';

const THREAT_RISK_LABELS = {
  1: 'Very Safe',
  2: 'Safe',
  3: 'Probably Safe',
  4: 'Leans Safe',
  5: 'May Not Be Safe',
  6: 'Exercise Caution',
  7: 'Suspicious/Risky',
  8: 'Possibly Malicious',
  9: 'Probably Malicious',
  10: 'Malicious',
};

function getThreatRiskTestUrl(level) {
  return `${THREAT_RISK_BASE_URL}${level}`;
}

function getThreatRiskLinkHtml(level) {
  const url = getThreatRiskTestUrl(level);
  const text = `URL of risk level ${level}`;
  return `<a href="${url}">${text}</a>`;
}
