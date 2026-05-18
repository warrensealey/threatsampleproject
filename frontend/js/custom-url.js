/**
 * User-defined custom URL links for custom emails.
 */

function escapeHtmlAttribute(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function escapeHtmlText(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function normalizeCustomUrl(url) {
  const trimmed = url.trim();
  if (!trimmed) {
    return '';
  }
  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed;
  }
  return `https://${trimmed}`;
}

function isAllowedCustomUrl(url) {
  try {
    const parsed = new URL(normalizeCustomUrl(url));
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

function getCustomUrlLinkHtml(url, displayText) {
  const normalizedUrl = normalizeCustomUrl(url);
  if (!isAllowedCustomUrl(url)) {
    return '';
  }
  const safeHref = escapeHtmlAttribute(normalizedUrl);
  const safeText = escapeHtmlText(displayText.trim());
  return `<a href="${safeHref}">${safeText}</a>`;
}
