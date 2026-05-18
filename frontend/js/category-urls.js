/**
 * WebFilter category test URLs for custom emails.
 */
const CATEGORY_URL_ENTRIES = {
  news: {
    url: 'https://www.bbc.co.uk',
    category: 'News',
  },
  'social-media': {
    url: 'https://www.facebook.com',
    category: 'Social Media',
  },
  'technology-internet': {
    url: 'https://www.broadcom.com',
    category: 'Technology/Internet',
  },
  'software-downloads': {
    url: 'https://www.snapfiles.com',
    category: 'Software Downloads',
  },
  scam: {
    url: 'http://www.hmrcgov.uk',
    category: 'Scam',
  },
};

function getCategoryLinkHtml(entryId) {
  const entry = CATEGORY_URL_ENTRIES[entryId];
  if (!entry) {
    return '';
  }
  const text = `URL of category: ${entry.category}`;
  return `<a href="${entry.url}">${text}</a>`;
}
