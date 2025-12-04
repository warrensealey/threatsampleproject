/**
 * API client for Email Data Generation application.
 */

const API_BASE = '/api';

// Basic fetch wrapper with timeout and simple retry logic to make the UI
// more resilient to transient Docker / network hiccups.
async function fetchWithTimeoutAndRetry(
  url,
  config = {},
  { timeoutMs = 15000, retries = 2, retryDelayMs = 500 } = {}
) {
  let lastError;

  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });
      clearTimeout(timer);
      return response;
    } catch (err) {
      clearTimeout(timer);
      lastError = err;

      const isAbortError =
        err &&
        (err.name === 'AbortError' ||
          err.message === 'The user aborted a request.');

      // Only retry on network/abort errors, not HTTP errors (those still give a response)
      if (attempt < retries && (isAbortError || err instanceof TypeError)) {
        await new Promise((r) => setTimeout(r, retryDelayMs));
        continue;
      }

      throw err;
    }
  }

  throw lastError;
}

class APIClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetchWithTimeoutAndRetry(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Configuration
  async getConfig() {
    return this.request('/config');
  }

  async updateConfig(config) {
    return this.request('/config', {
      method: 'POST',
      body: config,
    });
  }

  // Email client configuration
  async getEmailClientConfig(name = null) {
    const endpoint = name
      ? `/email/config?name=${encodeURIComponent(name)}`
      : '/email/config';
    return this.request(endpoint);
  }

  async updateEmailClientConfig(config) {
    return this.request('/email/config', {
      method: 'POST',
      body: config,
    });
  }

  async getAllEmailClientConfigs() {
    return this.request('/email/configs');
  }

  async deleteEmailClientConfig(name) {
    return this.request(`/email/config/${encodeURIComponent(name)}`, {
      method: 'DELETE',
    });
  }

  async getCurrentEmailClient() {
    return this.request('/email/config/current');
  }

  async setCurrentEmailClient(name) {
    return this.request('/email/config/current', {
      method: 'POST',
      body: { name },
    });
  }

  // Email sending
  async sendPhishing(count, recipients, templateType = 'warning') {
    return this.request('/send/phishing', {
      method: 'POST',
      body: { count, recipients, template_type: templateType },
    });
  }

  async sendEicar(count, recipients) {
    return this.request('/send/eicar', {
      method: 'POST',
      body: { count, recipients },
    });
  }

  async sendCynic(count, recipients) {
    return this.request('/send/cynic', {
      method: 'POST',
      body: { count, recipients },
    });
  }

  async sendGtube(count, recipients) {
    return this.request('/send/gtube', {
      method: 'POST',
      body: { count, recipients },
    });
  }

  async sendCustom(
    count,
    recipients,
    subject,
    body,
    displayName,
    attachmentType
  ) {
    return this.request('/send/custom', {
      method: 'POST',
      body: {
        count,
        recipients,
        subject,
        body,
        display_name: displayName,
        attachment_type: attachmentType,
      },
    });
  }

  // History
  async getHistory() {
    return this.request('/history');
  }

  // Test email configuration
  async testEmailConfig(recipient, emailClientConfig) {
    return this.request('/test/email', {
      method: 'POST',
      body: { recipient, email_client_config: emailClientConfig },
    });
  }
}

const api = new APIClient();
