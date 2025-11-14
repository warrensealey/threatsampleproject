/**
 * Main application logic for Email Data Generation.
 */

// Global state
let currentFolder = 'INBOX';
let currentMessage = null;

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    
    if (path === '/' || path === '/index.html') {
        initDashboard();
    } else if (path === '/config' || path === '/config.html') {
        initConfig();
    } else if (path === '/email' || path === '/email.html') {
        initEmailClient();
    }
});

// Dashboard functions
let defaultRecipients = [];

async function initDashboard() {
    await loadHistory();
    await loadDefaultRecipients();
    setupSendButtons();
}

async function loadDefaultRecipients() {
    try {
        const config = await api.getConfig();
        if (config.email_generation && config.email_generation.default_recipients) {
            defaultRecipients = config.email_generation.default_recipients;
        }
    } catch (error) {
        console.error('Failed to load default recipients:', error);
    }
}

function setupSendButtons() {
    document.getElementById('sendPhishingBtn')?.addEventListener('click', () => {
        showSendDialog('phishing');
    });
    
    document.getElementById('sendEicarBtn')?.addEventListener('click', () => {
        showSendDialog('eicar');
    });
    
    document.getElementById('sendCynicBtn')?.addEventListener('click', () => {
        showSendDialog('cynic');
    });
}

function showSendDialog(type) {
    const count = prompt(`How many ${type} emails to send?`, '1');
    if (!count) return;
    
    // Pre-populate with default recipients if available
    const defaultRecipientsStr = defaultRecipients.length > 0 ? defaultRecipients.join(', ') : '';
    const recipients = prompt('Enter recipient email addresses (comma-separated):', defaultRecipientsStr);
    if (!recipients) return;
    
    const recipientList = recipients.split(',').map(r => r.trim()).filter(r => r);
    
    if (recipientList.length === 0) {
        alert('No valid recipient addresses provided');
        return;
    }
    
    sendEmails(type, parseInt(count), recipientList);
}

async function sendEmails(type, count, recipients) {
    const statusDiv = document.getElementById('sendStatus');
    statusDiv.innerHTML = '<div class="alert alert-info">Sending emails...</div>';
    statusDiv.classList.remove('hidden');
    
    try {
        let result;
        if (type === 'phishing') {
            result = await api.sendPhishing(count, recipients);
        } else if (type === 'eicar') {
            result = await api.sendEicar(count, recipients);
        } else if (type === 'cynic') {
            result = await api.sendCynic(count, recipients);
        }
        
        if (result.success) {
            statusDiv.innerHTML = `<div class="alert alert-success">
                Successfully sent ${result.sent} email(s)!
            </div>`;
            await loadHistory();
        } else {
            statusDiv.innerHTML = `<div class="alert alert-error">
                Failed to send some emails. Sent: ${result.sent}, Failed: ${result.failed}
                ${result.errors ? '<br>Errors: ' + result.errors.join(', ') : ''}
            </div>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="alert alert-error">
            Error: ${error.message}
        </div>`;
    }
}

async function loadHistory() {
    try {
        const data = await api.getHistory();
        const historyDiv = document.getElementById('history');
        
        if (!data.history || data.history.length === 0) {
            historyDiv.innerHTML = '<p class="loading">No email history yet.</p>';
            return;
        }
        
        let html = '<table class="history-table"><thead><tr><th>Type</th><th>Subject</th><th>Recipients</th><th>Time</th><th>Status</th></tr></thead><tbody>';
        
        data.history.forEach(entry => {
            html += `<tr>
                <td>${entry.type}</td>
                <td>${entry.subject}</td>
                <td>${Array.isArray(entry.recipients) ? entry.recipients.join(', ') : entry.recipients}</td>
                <td>${new Date(entry.timestamp).toLocaleString()}</td>
                <td>${entry.status}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        historyDiv.innerHTML = html;
    } catch (error) {
        console.error('Failed to load history:', error);
        document.getElementById('history').innerHTML = '<p class="alert alert-error">Failed to load history.</p>';
    }
}

// Email provider configurations
const emailProviderConfigs = {
    aol: {
        imap_server: 'imap.aol.com',
        imap_port: 993,
        smtp_server: 'smtp.aol.com',
        smtp_port: 465,
        username: '',
        password: '',
        use_ssl: true,
        use_starttls: false,
        smtp_use_tls: false,
        smtp_use_ssl: true
    },
    gmail: {
        imap_server: 'imap.gmail.com',
        imap_port: 993,
        smtp_server: 'smtp.gmail.com',
        smtp_port: 587,
        username: '',
        password: '',
        use_ssl: true,
        use_starttls: false,
        smtp_use_tls: true,
        smtp_use_ssl: false
    },
    msoutlook: {
        imap_server: 'outlook.office365.com',
        imap_port: 993,
        smtp_server: 'smtp.office365.com',
        smtp_port: 587,
        username: '',
        password: '',
        use_ssl: true,
        use_starttls: false,
        smtp_use_tls: true,
        smtp_use_ssl: false
    },
    gmx: {
        imap_server: 'imap.gmx.com',
        imap_port: 993,
        smtp_server: 'mail.gmx.com',
        smtp_port: 587,
        username: '',
        password: '',
        use_ssl: true,
        use_starttls: false,
        smtp_use_tls: true,
        smtp_use_ssl: false
    }
};

// Configuration functions
async function initConfig() {
    setupConfigForm();
    setupProviderDropdown();
    setupMuttModule();
    
    await loadConfig();
    await checkMuttStatus();
    
    // After loading config, if SMTP server is still empty and GMX is selected, populate it
    const providerSelect = document.getElementById('emailProvider');
    const smtpServer = document.getElementById('smtpServer');
    if (providerSelect && providerSelect.value === 'gmx' && smtpServer && !smtpServer.value) {
        populateProviderSettings(emailProviderConfigs.gmx);
    }
}

function setupConfigForm() {
    document.getElementById('emailClientForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveEmailClientConfig();
    });
    
    document.getElementById('emailGenForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveEmailGenConfig();
    });
    
    // Test email button
    document.getElementById('testEmailBtn')?.addEventListener('click', async () => {
        await testEmailConfiguration();
    });
    
    // Modal close button
    document.querySelector('.modal-close')?.addEventListener('click', () => {
        document.getElementById('testEmailModal').classList.add('hidden');
    });
    
    // Confirm receipt button
    document.getElementById('confirmReceiptBtn')?.addEventListener('click', () => {
        showAlert('Email configuration test completed successfully!', 'success');
        document.getElementById('testEmailModal').classList.add('hidden');
    });
    
    // Cancel test button
    document.getElementById('cancelTestBtn')?.addEventListener('click', () => {
        document.getElementById('testEmailModal').classList.add('hidden');
    });
    
    // Close modal when clicking outside
    document.getElementById('testEmailModal')?.addEventListener('click', (e) => {
        if (e.target.id === 'testEmailModal') {
            document.getElementById('testEmailModal').classList.add('hidden');
        }
    });
}

function setupMuttModule() {
    document.getElementById('installMuttBtn')?.addEventListener('click', async () => {
        await installMutt();
    });
    
    document.getElementById('refreshMuttStatusBtn')?.addEventListener('click', async () => {
        await checkMuttStatus();
    });
}

async function checkMuttStatus() {
    const statusDiv = document.getElementById('muttStatus');
    const actionsDiv = document.getElementById('muttActions');
    
    try {
        statusDiv.innerHTML = '<p class="loading">Checking mutt installation...</p>';
        actionsDiv.classList.add('hidden');
        
        const result = await api.getMuttStatus();
        
        if (result.installed) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <strong>Mutt is installed</strong><br>
                    <strong>Version:</strong> ${result.version || 'Unknown'}<br>
                    <strong>Path:</strong> ${result.path || 'Unknown'}<br>
                    <strong>OS:</strong> ${result.os_distro || result.os_type || 'Unknown'}
                </div>
            `;
            actionsDiv.classList.remove('hidden');
            document.getElementById('installMuttBtn').style.display = 'none';
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-error">
                    <strong>Mutt is not installed</strong><br>
                    <strong>OS:</strong> ${result.os_distro || result.os_type || 'Unknown'}<br>
                    Click the button below to install mutt automatically.
                </div>
            `;
            actionsDiv.classList.remove('hidden');
            document.getElementById('installMuttBtn').style.display = 'inline-block';
        }
    } catch (error) {
        statusDiv.innerHTML = `
            <div class="alert alert-error">
                <strong>Error checking mutt status:</strong> ${error.message}
            </div>
        `;
        actionsDiv.classList.remove('hidden');
    }
}

async function installMutt() {
    const statusDiv = document.getElementById('muttStatus');
    const installBtn = document.getElementById('installMuttBtn');
    
    const originalText = installBtn.textContent;
    installBtn.disabled = true;
    installBtn.textContent = 'Installing...';
    
    statusDiv.innerHTML = '<p class="loading">Installing mutt, please wait...</p>';
    
    try {
        const result = await api.installMutt();
        
        if (result.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <strong>Mutt installed successfully!</strong><br>
                    <strong>Path:</strong> ${result.path || 'Unknown'}<br>
                    ${result.message || ''}
                </div>
            `;
            // Refresh status to show updated info
            setTimeout(() => checkMuttStatus(), 2000);
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-error">
                    <strong>Installation failed:</strong> ${result.error || 'Unknown error'}<br>
                    ${result.stderr ? '<pre>' + result.stderr + '</pre>' : ''}
                    ${result.output ? '<pre>' + result.output + '</pre>' : ''}
                </div>
            `;
        }
    } catch (error) {
        statusDiv.innerHTML = `
            <div class="alert alert-error">
                <strong>Error installing mutt:</strong> ${error.message}
            </div>
        `;
    } finally {
        installBtn.disabled = false;
        installBtn.textContent = originalText;
    }
}

function setupProviderDropdown() {
    const providerSelect = document.getElementById('emailProvider');
    if (providerSelect) {
        providerSelect.addEventListener('change', (e) => {
            const provider = e.target.value;
            if (provider && emailProviderConfigs[provider]) {
                populateProviderSettings(emailProviderConfigs[provider]);
            }
        });
    }
}

function populateProviderSettings(settings) {
    if (settings.imap_server) {
        document.getElementById('imapServer').value = settings.imap_server;
    }
    if (settings.imap_port) {
        document.getElementById('imapPort').value = settings.imap_port;
    }
    if (settings.username) {
        document.getElementById('imapUsername').value = settings.username;
    }
    if (settings.password) {
        document.getElementById('imapPassword').value = settings.password;
    }
    if (settings.use_ssl !== undefined) {
        document.getElementById('imapUseSSL').checked = settings.use_ssl;
    }
    if (settings.use_starttls !== undefined) {
        document.getElementById('imapUseSTARTTLS').checked = settings.use_starttls;
    }
    // SMTP settings
    if (settings.smtp_server) {
        document.getElementById('smtpServer').value = settings.smtp_server;
    }
    if (settings.smtp_port) {
        document.getElementById('smtpPort').value = settings.smtp_port;
    }
    if (settings.smtp_use_tls !== undefined) {
        document.getElementById('smtpUseTLS').checked = settings.smtp_use_tls;
    }
    if (settings.smtp_use_ssl !== undefined) {
        document.getElementById('smtpUseSSL').checked = settings.smtp_use_ssl;
    }
}

async function loadConfig() {
    try {
        const config = await api.getConfig();
        
        // Load email client config
        if (config.email_client) {
            // Check if config matches a provider
            let matchedProvider = '';
            for (const [key, providerConfig] of Object.entries(emailProviderConfigs)) {
                if (providerConfig.imap_server === config.email_client.imap_server) {
                    matchedProvider = key;
                    break;
                }
            }
            
            // Set provider dropdown if matched
            if (matchedProvider) {
                document.getElementById('emailProvider').value = matchedProvider;
            }
            
            document.getElementById('imapServer').value = config.email_client.imap_server || '';
            document.getElementById('imapPort').value = config.email_client.imap_port || 993;
            document.getElementById('imapUsername').value = config.email_client.username || '';
            document.getElementById('imapPassword').value = config.email_client.password || '';
            document.getElementById('imapUseSSL').checked = config.email_client.use_ssl !== false;
            document.getElementById('imapUseSTARTTLS').checked = config.email_client.use_starttls === true;
            
            // Load SMTP settings
            document.getElementById('smtpServer').value = config.email_client.smtp_server || '';
            document.getElementById('smtpPort').value = config.email_client.smtp_port || 587;
            document.getElementById('smtpUseTLS').checked = config.email_client.smtp_use_tls !== false;
            document.getElementById('smtpUseSSL').checked = config.email_client.smtp_use_ssl === true;
            
            // If SMTP server is empty but we have IMAP server, try to populate from provider
            if (!config.email_client.smtp_server && config.email_client.imap_server) {
                const providerSelect = document.getElementById('emailProvider');
                if (providerSelect && providerSelect.value) {
                    const provider = emailProviderConfigs[providerSelect.value];
                    if (provider && provider.smtp_server) {
                        document.getElementById('smtpServer').value = provider.smtp_server;
                        document.getElementById('smtpPort').value = provider.smtp_port || 587;
                        document.getElementById('smtpUseTLS').checked = provider.smtp_use_tls !== false;
                        document.getElementById('smtpUseSSL').checked = provider.smtp_use_ssl === true;
                    }
                }
            }
        } else {
            // If no config exists, auto-populate GMX (default selected)
            const providerSelect = document.getElementById('emailProvider');
            if (providerSelect) {
                // Ensure GMX is selected
                providerSelect.value = 'gmx';
                populateProviderSettings(emailProviderConfigs.gmx);
            }
        }
        
        // Load email generation config
        if (config.email_generation) {
            document.getElementById('defaultRecipients').value = 
                (config.email_generation.default_recipients || []).join(', ');
            document.getElementById('defaultCount').value = config.email_generation.default_count || 1;
        }
    } catch (error) {
        console.error('Failed to load config:', error);
        showAlert('Failed to load configuration', 'error');
    }
}

async function saveEmailClientConfig() {
    const config = {
        imap_server: document.getElementById('imapServer').value,
        imap_port: parseInt(document.getElementById('imapPort').value),
        username: document.getElementById('imapUsername').value,
        password: document.getElementById('imapPassword').value,
        use_ssl: document.getElementById('imapUseSSL').checked,
        use_starttls: document.getElementById('imapUseSTARTTLS').checked,
        smtp_server: document.getElementById('smtpServer').value,
        smtp_port: parseInt(document.getElementById('smtpPort').value) || 587,
        smtp_use_tls: document.getElementById('smtpUseTLS').checked,
        smtp_use_ssl: document.getElementById('smtpUseSSL').checked
    };
    
    try {
        await api.updateEmailClientConfig(config);
        showAlert('Email client configuration saved successfully!', 'success');
    } catch (error) {
        showAlert('Failed to save email client configuration: ' + error.message, 'error');
    }
}

async function saveEmailGenConfig() {
    const recipients = document.getElementById('defaultRecipients').value
        .split(',')
        .map(r => r.trim())
        .filter(r => r);
    
    const config = {
        default_recipients: recipients,
        default_count: parseInt(document.getElementById('defaultCount').value) || 1
    };
    
    try {
        await api.updateConfig({ email_generation: config });
        showAlert('Email generation configuration saved successfully!', 'success');
    } catch (error) {
        showAlert('Failed to save email generation configuration: ' + error.message, 'error');
    }
}

async function testEmailConfiguration() {
    // Get default recipient
    const defaultRecipients = document.getElementById('defaultRecipients').value
        .split(',')
        .map(r => r.trim())
        .filter(r => r);
    
    let recipient = defaultRecipients.length > 0 ? defaultRecipients[0] : null;
    
    // Prompt for recipient if not set
    if (!recipient) {
        recipient = prompt('Enter recipient email address for test email:');
        if (!recipient || !recipient.trim()) {
            showAlert('Test cancelled: No recipient specified', 'error');
            return;
        }
        recipient = recipient.trim();
    }
    
    // Get email client configuration from form
    const emailClientConfig = {
        imap_server: document.getElementById('imapServer').value,
        imap_port: parseInt(document.getElementById('imapPort').value),
        username: document.getElementById('imapUsername').value,
        password: document.getElementById('imapPassword').value,
        use_ssl: document.getElementById('imapUseSSL').checked,
        use_starttls: document.getElementById('imapUseSTARTTLS').checked,
        smtp_server: document.getElementById('smtpServer').value,
        smtp_port: parseInt(document.getElementById('smtpPort').value) || 587,
        smtp_use_tls: document.getElementById('smtpUseTLS').checked,
        smtp_use_ssl: document.getElementById('smtpUseSSL').checked
    };
    
    // Validate configuration
    if (!emailClientConfig.imap_server || !emailClientConfig.username || !emailClientConfig.password) {
        showAlert('Please fill in all required email client configuration fields', 'error');
        return;
    }
    
    // Show modal
    const modal = document.getElementById('testEmailModal');
    modal.classList.remove('hidden');
    
    // Reset modal content
    document.getElementById('testEmailStatus').innerHTML = '<p class="loading">Testing email configuration...</p>';
    document.getElementById('testEmailConnectionInfo').classList.add('hidden');
    document.getElementById('testEmailActions').classList.add('hidden');
    
    try {
        const result = await api.testEmailConfig(recipient, emailClientConfig);
        
        if (result.success) {
            // Show success message
            document.getElementById('testEmailStatus').innerHTML = 
                `<div class="alert alert-success">
                    <strong>Success!</strong> Test email sent successfully to ${recipient}
                </div>`;
            
            // Show connection information
            const connInfo = result.connection_info;
            document.getElementById('connectionDetails').innerHTML = `
                <p><strong>SMTP Server:</strong> ${connInfo.smtp_server}:${connInfo.smtp_port}</p>
                <p><strong>Username:</strong> ${connInfo.username}</p>
                <p><strong>Recipient:</strong> ${connInfo.recipient}</p>
                <p><strong>SSL:</strong> ${connInfo.use_ssl ? 'Yes' : 'No'}</p>
                <p><strong>TLS:</strong> ${connInfo.use_tls ? 'Yes' : 'No'}</p>
                <p><strong>Subject:</strong> ${result.subject || 'N/A'}</p>
            `;
            document.getElementById('testEmailConnectionInfo').classList.remove('hidden');
            
            // Show confirmation buttons
            document.getElementById('testEmailActions').classList.remove('hidden');
        } else {
            // Show error message
            document.getElementById('testEmailStatus').innerHTML = 
                `<div class="alert alert-error">
                    <strong>Error:</strong> ${result.error || 'Failed to send test email'}
                </div>`;
            
            // Show connection information even on error
            if (result.connection_info) {
                const connInfo = result.connection_info;
                document.getElementById('connectionDetails').innerHTML = `
                    <p><strong>SMTP Server:</strong> ${connInfo.smtp_server}:${connInfo.smtp_port}</p>
                    <p><strong>Username:</strong> ${connInfo.username}</p>
                    <p><strong>Recipient:</strong> ${connInfo.recipient}</p>
                    <p><strong>SSL:</strong> ${connInfo.use_ssl ? 'Yes' : 'No'}</p>
                    <p><strong>TLS:</strong> ${connInfo.use_tls ? 'Yes' : 'No'}</p>
                `;
                document.getElementById('testEmailConnectionInfo').classList.remove('hidden');
            }
        }
    } catch (error) {
        document.getElementById('testEmailStatus').innerHTML = 
            `<div class="alert alert-error">
                <strong>Error:</strong> ${error.message}
            </div>`;
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'error' : 'success'}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

// Email client functions
async function initEmailClient() {
    await loadFolders();
    setupEmailClient();
}

function setupEmailClient() {
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
        loadMessages(currentFolder);
    });
}

async function loadFolders() {
    try {
        const data = await api.listFolders();
        const folderList = document.getElementById('folderList');
        
        if (!data.folders || data.folders.length === 0) {
            folderList.innerHTML = '<li class="folder-item">No folders found</li>';
            return;
        }
        
        let html = '';
        data.folders.forEach(folder => {
            const active = folder === currentFolder ? 'active' : '';
            html += `<li class="folder-item ${active}" data-folder="${folder}">${folder}</li>`;
        });
        
        folderList.innerHTML = html;
        
        // Add click handlers
        folderList.querySelectorAll('.folder-item').forEach(item => {
            item.addEventListener('click', () => {
                const folder = item.dataset.folder;
                currentFolder = folder;
                loadFolders(); // Refresh to update active state
                loadMessages(folder);
            });
        });
        
        // Load messages for current folder
        loadMessages(currentFolder);
    } catch (error) {
        console.error('Failed to load folders:', error);
        document.getElementById('folderList').innerHTML = 
            '<li class="folder-item">Failed to load folders</li>';
    }
}

async function loadMessages(folder) {
    try {
        const data = await api.getMessages(folder, 50);
        const messageList = document.getElementById('messageList');
        
        if (!data.messages || data.messages.length === 0) {
            messageList.innerHTML = '<li class="email-item">No messages</li>';
            return;
        }
        
        let html = '';
        data.messages.forEach(msg => {
            html += `<li class="email-item" data-msg-id="${msg.id}">
                <div class="email-header">
                    <span class="email-subject">${msg.subject || '(No subject)'}</span>
                    <span class="email-date">${msg.date ? new Date(msg.date).toLocaleString() : ''}</span>
                </div>
                <div class="email-from">From: ${msg.from || 'Unknown'}</div>
            </li>`;
        });
        
        messageList.innerHTML = html;
        
        // Add click handlers
        messageList.querySelectorAll('.email-item').forEach(item => {
            item.addEventListener('click', () => {
                const msgId = item.dataset.msgId;
                loadMessage(folder, msgId);
                
                // Update selected state
                messageList.querySelectorAll('.email-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
            });
        });
    } catch (error) {
        console.error('Failed to load messages:', error);
        document.getElementById('messageList').innerHTML = 
            '<li class="email-item">Failed to load messages</li>';
    }
}

async function loadMessage(folder, msgId) {
    try {
        const message = await api.getMessage(msgId, folder);
        const viewer = document.getElementById('messageViewer');
        
        if (!message) {
            viewer.innerHTML = '<div class="alert alert-error">Message not found</div>';
            return;
        }
        
        let html = `<div class="email-viewer">
            <div class="email-viewer-header">
                <h3>${message.subject || '(No subject)'}</h3>
                <p><strong>From:</strong> ${message.from || 'Unknown'}</p>
                <p><strong>To:</strong> ${message.to || 'Unknown'}</p>
                <p><strong>Date:</strong> ${message.date ? new Date(message.date).toLocaleString() : 'Unknown'}</p>
                ${message.attachments && message.attachments.length > 0 ? 
                    `<p><strong>Attachments:</strong> ${message.attachments.map(a => a.filename).join(', ')}</p>` : ''}
            </div>
            <div class="email-viewer-body">${message.body || '(No body)'}</div>
        </div>`;
        
        viewer.innerHTML = html;
        currentMessage = message;
    } catch (error) {
        console.error('Failed to load message:', error);
        document.getElementById('messageViewer').innerHTML = 
            '<div class="alert alert-error">Failed to load message</div>';
    }
}

