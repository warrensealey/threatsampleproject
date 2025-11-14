/**
 * API client for Email Data Generation application.
 */

const API_BASE = '/api';

class APIClient {
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);
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
            body: config
        });
    }

    // Email client configuration
    async getEmailClientConfig() {
        return this.request('/email/config');
    }

    async updateEmailClientConfig(config) {
        return this.request('/email/config', {
            method: 'POST',
            body: config
        });
    }

    // Email sending
    async sendPhishing(count, recipients, templateType = 'warning') {
        return this.request('/send/phishing', {
            method: 'POST',
            body: { count, recipients, template_type: templateType }
        });
    }

    async sendEicar(count, recipients) {
        return this.request('/send/eicar', {
            method: 'POST',
            body: { count, recipients }
        });
    }

    async sendCynic(count, recipients) {
        return this.request('/send/cynic', {
            method: 'POST',
            body: { count, recipients }
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
            body: { recipient, email_client_config: emailClientConfig }
        });
    }

    // Mutt status and installation
    async getMuttStatus() {
        return this.request('/mutt/status');
    }

    async installMutt() {
        return this.request('/mutt/install', {
            method: 'POST'
        });
    }
}

const api = new APIClient();

