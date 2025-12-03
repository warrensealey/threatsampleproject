/**
 * Main application logic for Email Data Generation.
 */

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;

  if (path === '/' || path === '/index.html') {
    initDashboard();
  } else if (path === '/config' || path === '/config.html') {
    initConfig();
  }
});

// Dashboard functions
let defaultRecipients = [];

async function initDashboard() {
  await loadHistory();
  await loadDefaultRecipients();
  setupSendButtons();
  setupEmailSendModal();
}

function setupEmailSendModal() {
  // Email send modal close handlers
  document
    .getElementById('emailSendModalClose')
    ?.addEventListener('click', () => {
      document.getElementById('emailSendModal').classList.add('hidden');
    });

  document
    .getElementById('closeEmailSendModalBtn')
    ?.addEventListener('click', () => {
      document.getElementById('emailSendModal').classList.add('hidden');
    });

  document.getElementById('emailSendModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'emailSendModal') {
      document.getElementById('emailSendModal').classList.add('hidden');
    }
  });

  // Custom email modal handlers
  document
    .getElementById('customEmailModalClose')
    ?.addEventListener('click', () => {
      document.getElementById('customEmailModal').classList.add('hidden');
    });

  document
    .getElementById('cancelCustomEmailBtn')
    ?.addEventListener('click', () => {
      document.getElementById('customEmailModal').classList.add('hidden');
    });

  document
    .getElementById('customEmailModal')
    ?.addEventListener('click', (e) => {
      if (e.target.id === 'customEmailModal') {
        document.getElementById('customEmailModal').classList.add('hidden');
      }
    });

  // Custom email form submission
  document
    .getElementById('customEmailForm')
    ?.addEventListener('submit', async (e) => {
      e.preventDefault();
      await sendCustomEmail();
    });

  // Phishing warning modal handlers
  document
    .getElementById('phishingWarningConfirmBtn')
    ?.addEventListener('click', () => {
      document.getElementById('phishingWarningModal').classList.add('hidden');
      showSendDialog('phishing');
    });

  document
    .getElementById('phishingWarningCancelBtn')
    ?.addEventListener('click', () => {
      document.getElementById('phishingWarningModal').classList.add('hidden');
    });

  document
    .getElementById('phishingWarningModal')
    ?.addEventListener('click', (e) => {
      if (e.target.id === 'phishingWarningModal') {
        document.getElementById('phishingWarningModal').classList.add('hidden');
      }
    });
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
    showPhishingWarning();
  });

  document.getElementById('sendEicarBtn')?.addEventListener('click', () => {
    showSendDialog('eicar');
  });

  document.getElementById('sendCynicBtn')?.addEventListener('click', () => {
    showSendDialog('cynic');
  });

  document.getElementById('sendGtubeBtn')?.addEventListener('click', () => {
    showSendDialog('gtube');
  });

  document.getElementById('sendCustomBtn')?.addEventListener('click', () => {
    showCustomEmailModal();
  });
}

function showPhishingWarning() {
  const modal = document.getElementById('phishingWarningModal');
  if (modal) {
    modal.classList.remove('hidden');
  }
}

function showSendDialog(type) {
  let countValue = '1';
  if (type !== 'gtube') {
    countValue = prompt(`How many ${type} emails to send?`, '1');
    if (!countValue) return;
  }

  // Pre-populate with default recipients if available
  const defaultRecipientsStr =
    defaultRecipients.length > 0 ? defaultRecipients.join(', ') : '';
  const recipients = prompt(
    'Enter recipient email addresses (comma-separated):',
    defaultRecipientsStr
  );
  if (!recipients) return;

  const recipientList = recipients
    .split(',')
    .map((r) => r.trim())
    .filter((r) => r);

  if (recipientList.length === 0) {
    alert('No valid recipient addresses provided');
    return;
  }

  const parsedCount = type === 'gtube' ? 1 : parseInt(countValue, 10);
  sendEmails(type, parsedCount, recipientList);
}

async function sendEmails(type, count, recipients) {
  const statusDiv = document.getElementById('sendStatus');
  const modal = document.getElementById('emailSendModal');
  const modalTitle = document.getElementById('emailSendModalTitle');
  const modalStatus = document.getElementById('emailSendStatus');
  const modalConnectionInfo = document.getElementById(
    'emailSendConnectionInfo'
  );
  const modalConnectionDetails = document.getElementById(
    'emailSendConnectionDetails'
  );
  const modalActions = document.getElementById('emailSendActions');

  // Update modal title based on type
  const typeNames = {
    phishing: 'Phishing',
    eicar: 'EICAR',
    cynic: 'Cynic',
    gtube: 'GTUBE',
  };
  modalTitle.textContent = `${
    typeNames[type] || type.toUpperCase()
  } Email Send Results`;

  // Show status in dashboard
  statusDiv.innerHTML = '<div class="alert alert-info">Sending emails...</div>';
  statusDiv.classList.remove('hidden');

  // Show modal
  modal.classList.remove('hidden');
  modalStatus.innerHTML = '<p class="loading">Sending emails...</p>';
  modalConnectionInfo.classList.add('hidden');
  modalActions.classList.add('hidden');

  try {
    let result;
    if (type === 'phishing') {
      result = await api.sendPhishing(count, recipients);
    } else if (type === 'eicar') {
      result = await api.sendEicar(count, recipients);
    } else if (type === 'cynic') {
      result = await api.sendCynic(count, recipients);
    } else if (type === 'gtube') {
      result = await api.sendGtube(count, recipients);
    } else {
      throw new Error(`Unsupported email type: ${type}`);
    }

    // Build connection details text
    let connectionText = '';
    if (result.connection_info) {
      const connInfo = result.connection_info;
      connectionText = `IMAP Connection:
Server: ${connInfo.imap_server || 'N/A'}:${connInfo.imap_port || 993}
Username: ${connInfo.username || 'N/A'}
Encryption: ${
        connInfo.imap_use_ssl
          ? 'SSL'
          : connInfo.imap_use_starttls
          ? 'STARTTLS'
          : 'None'
      }

SMTP Connection:
Server: ${connInfo.smtp_server || 'N/A'}:${connInfo.smtp_port || 587}
Username: ${connInfo.username || 'N/A'}
Encryption: ${connInfo.use_ssl ? 'SSL' : connInfo.use_tls ? 'TLS' : 'None'}

Email Details:
Type: ${typeNames[type] || type}
Total: ${result.total || count}
Sent: ${result.sent || 0}
Failed: ${result.failed || 0}`;

      // Add success or error details
      if (result.success && result.connection_details) {
        connectionText += `\n\n${result.connection_details}`;
      } else if (result.error_details) {
        connectionText += `\n\n${result.error_details}`;
      } else if (result.connection_attempt) {
        const attempt = result.connection_attempt;
        connectionText += `\n\nConnection Attempt:
Server: ${attempt.attempted_server || 'N/A'}
Username: ${attempt.attempted_username || 'N/A'}
Encryption: ${attempt.attempted_encryption || 'N/A'}
Method: ${attempt.connection_method || 'N/A'}`;
      }
    }

    if (result.success) {
      // Success
      statusDiv.innerHTML = `<div class="alert alert-success">
                Successfully sent ${result.sent} email(s)!
            </div>`;

      modalStatus.innerHTML = `<div class="alert alert-success">
                <strong>Success!</strong> Successfully sent ${result.sent} email(s)!
            </div>`;

      if (connectionText) {
        modalConnectionDetails.innerHTML = `
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; font-size: 13px; line-height: 1.6;">${connectionText}</pre>
                `;
        modalConnectionInfo.classList.remove('hidden');
      }

      modalActions.classList.remove('hidden');
      await loadHistory();
    } else {
      // Partial or complete failure
      statusDiv.innerHTML = `<div class="alert alert-error">
                Failed to send some emails. Sent: ${result.sent}, Failed: ${
        result.failed
      }
                ${
                  result.errors ? '<br>Errors: ' + result.errors.join(', ') : ''
                }
            </div>`;

      modalStatus.innerHTML = `<div class="alert alert-error">
                <strong>Error:</strong> Failed to send some emails. Sent: ${
                  result.sent || 0
                }, Failed: ${result.failed || 0}
                ${
                  result.errors && result.errors.length > 0
                    ? '<br><br>Errors:<br>' +
                      result.errors.slice(0, 5).join('<br>')
                    : ''
                }
            </div>`;

      if (connectionText) {
        modalConnectionDetails.innerHTML = `
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; font-size: 13px; line-height: 1.6; color: #d32f2f;">${connectionText}</pre>
                `;
        modalConnectionInfo.classList.remove('hidden');
      }

      modalActions.classList.remove('hidden');
    }
  } catch (error) {
    statusDiv.innerHTML = `<div class="alert alert-error">
            Error: ${error.message}
        </div>`;

    modalStatus.innerHTML = `<div class="alert alert-error">
            <strong>Error:</strong> ${error.message}
        </div>`;

    modalActions.classList.remove('hidden');
  }
}

function showCustomEmailModal() {
  const modal = document.getElementById('customEmailModal');
  const recipientsInput = document.getElementById('customRecipients');

  // Pre-populate recipients from defaults
  if (recipientsInput && defaultRecipients.length > 0) {
    recipientsInput.value = defaultRecipients.join(', ');
  }

  // Clear other fields
  document.getElementById('customSubject').value = '';
  document.getElementById('customBody').value = '';
  document.getElementById('customDisplayName').value = '';
  document.getElementById('customAttachment').value = '';
  document.getElementById('customCount').value = '1';

  modal.classList.remove('hidden');
}

async function sendCustomEmail() {
  const subject = document.getElementById('customSubject').value.trim();
  const body = document.getElementById('customBody').value.trim();
  const displayName = document.getElementById('customDisplayName').value.trim();
  const attachmentType = document.getElementById('customAttachment').value;
  const recipientsStr = document
    .getElementById('customRecipients')
    .value.trim();
  const count = parseInt(document.getElementById('customCount').value) || 1;

  // Validate required fields
  if (!subject) {
    showAlert('Subject is required', 'error');
    return;
  }

  if (!body) {
    showAlert('Body is required', 'error');
    return;
  }

  if (!recipientsStr) {
    showAlert('Recipients are required', 'error');
    return;
  }

  const recipients = recipientsStr
    .split(',')
    .map((r) => r.trim())
    .filter((r) => r);
  if (recipients.length === 0) {
    showAlert('No valid recipient addresses provided', 'error');
    return;
  }

  // Close custom email modal
  document.getElementById('customEmailModal').classList.add('hidden');

  // Use existing email send modal for results
  const statusDiv = document.getElementById('sendStatus');
  const modal = document.getElementById('emailSendModal');
  const modalTitle = document.getElementById('emailSendModalTitle');
  const modalStatus = document.getElementById('emailSendStatus');
  const modalConnectionInfo = document.getElementById(
    'emailSendConnectionInfo'
  );
  const modalConnectionDetails = document.getElementById(
    'emailSendConnectionDetails'
  );
  const modalActions = document.getElementById('emailSendActions');

  modalTitle.textContent = 'Custom Email Send Results';

  // Show status in dashboard
  statusDiv.innerHTML =
    '<div class="alert alert-info">Sending custom email...</div>';
  statusDiv.classList.remove('hidden');

  // Show modal
  modal.classList.remove('hidden');
  modalStatus.innerHTML = '<p class="loading">Sending email...</p>';
  modalConnectionInfo.classList.add('hidden');
  modalActions.classList.add('hidden');

  try {
    const result = await api.sendCustom(
      count,
      recipients,
      subject,
      body,
      displayName || null,
      attachmentType || null
    );

    // Build connection details text
    let connectionText = '';
    if (result.connection_info) {
      const connInfo = result.connection_info;
      connectionText = `IMAP Connection:
Server: ${connInfo.imap_server || 'N/A'}:${connInfo.imap_port || 993}
Username: ${connInfo.username || 'N/A'}
Encryption: ${
        connInfo.imap_use_ssl
          ? 'SSL'
          : connInfo.imap_use_starttls
          ? 'STARTTLS'
          : 'None'
      }

SMTP Connection:
Server: ${connInfo.smtp_server || 'N/A'}:${connInfo.smtp_port || 587}
Username: ${connInfo.username || 'N/A'}
Encryption: ${connInfo.use_ssl ? 'SSL' : connInfo.use_tls ? 'TLS' : 'None'}

Email Details:
Type: Custom
Subject: ${subject}
Display Name: ${displayName || 'N/A'}
Attachment: ${attachmentType || 'None'}
Total: ${result.total || count}
Sent: ${result.sent || 0}
Failed: ${result.failed || 0}`;

      // Add success or error details
      if (result.success && result.connection_details) {
        connectionText += `\n\n${result.connection_details}`;
      } else if (result.error_details) {
        connectionText += `\n\n${result.error_details}`;
      } else if (result.connection_attempt) {
        const attempt = result.connection_attempt;
        connectionText += `\n\nConnection Attempt:
Server: ${attempt.attempted_server || 'N/A'}
Username: ${attempt.attempted_username || 'N/A'}
Encryption: ${attempt.attempted_encryption || 'N/A'}
Method: ${attempt.connection_method || 'N/A'}`;
      }
    }

    if (result.success) {
      // Success
      statusDiv.innerHTML = `<div class="alert alert-success">
                Successfully sent ${result.sent} email(s)!
            </div>`;

      modalStatus.innerHTML = `<div class="alert alert-success">
                <strong>Success!</strong> Successfully sent ${result.sent} email(s)!
            </div>`;

      if (connectionText) {
        modalConnectionDetails.innerHTML = `
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; font-size: 13px; line-height: 1.6;">${connectionText}</pre>
                `;
        modalConnectionInfo.classList.remove('hidden');
      }

      modalActions.classList.remove('hidden');
      await loadHistory();
    } else {
      // Partial or complete failure
      statusDiv.innerHTML = `<div class="alert alert-error">
                Failed to send some emails. Sent: ${result.sent}, Failed: ${
        result.failed
      }
                ${
                  result.errors ? '<br>Errors: ' + result.errors.join(', ') : ''
                }
            </div>`;

      modalStatus.innerHTML = `<div class="alert alert-error">
                <strong>Error:</strong> Failed to send some emails. Sent: ${
                  result.sent || 0
                }, Failed: ${result.failed || 0}
                ${
                  result.errors && result.errors.length > 0
                    ? '<br><br>Errors:<br>' +
                      result.errors.slice(0, 5).join('<br>')
                    : ''
                }
            </div>`;

      if (connectionText) {
        modalConnectionDetails.innerHTML = `
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; font-size: 13px; line-height: 1.6; color: #d32f2f;">${connectionText}</pre>
                `;
        modalConnectionInfo.classList.remove('hidden');
      }

      modalActions.classList.remove('hidden');
    }
  } catch (error) {
    statusDiv.innerHTML = `<div class="alert alert-error">
            Error: ${error.message}
        </div>`;

    modalStatus.innerHTML = `<div class="alert alert-error">
            <strong>Error:</strong> ${error.message}
        </div>`;

    modalActions.classList.remove('hidden');
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

    let html =
      '<table class="history-table"><thead><tr><th>Type</th><th>Subject</th><th>Recipients</th><th>Time</th><th>Status</th></tr></thead><tbody>';

    data.history.forEach((entry) => {
      html += `<tr>
                <td>${entry.type}</td>
                <td>${entry.subject}</td>
                <td>${
                  Array.isArray(entry.recipients)
                    ? entry.recipients.join(', ')
                    : entry.recipients
                }</td>
                <td>${new Date(entry.timestamp).toLocaleString()}</td>
                <td>${entry.status}</td>
            </tr>`;
    });

    html += '</tbody></table>';
    historyDiv.innerHTML = html;
  } catch (error) {
    console.error('Failed to load history:', error);
    document.getElementById('history').innerHTML =
      '<p class="alert alert-error">Failed to load history.</p>';
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
    smtp_use_ssl: true,
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
    smtp_use_ssl: false,
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
    smtp_use_ssl: false,
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
    smtp_use_ssl: false,
  },
  yahoo: {
    imap_server: 'imap.mail.yahoo.com',
    imap_port: 993,
    smtp_server: 'smtp.mail.yahoo.com',
    smtp_port: 587,
    username: '',
    password: '',
    use_ssl: true,
    use_starttls: false,
    smtp_use_tls: true,
    smtp_use_ssl: false,
  },
  icloud: {
    imap_server: 'imap.mail.me.com',
    imap_port: 993,
    smtp_server: 'smtp.mail.me.com',
    smtp_port: 587,
    username: '',
    password: '',
    use_ssl: true,
    use_starttls: false,
    smtp_use_tls: true,
    smtp_use_ssl: false,
  },
  zoho: {
    imap_server: 'imap.zoho.com',
    imap_port: 993,
    smtp_server: 'smtp.zoho.com',
    smtp_port: 587,
    username: '',
    password: '',
    use_ssl: true,
    use_starttls: false,
    smtp_use_tls: true,
    smtp_use_ssl: false,
  },
  outlookcom: {
    imap_server: 'imap-mail.outlook.com',
    imap_port: 993,
    smtp_server: 'smtp-mail.outlook.com',
    smtp_port: 587,
    username: '',
    password: '',
    use_ssl: true,
    use_starttls: false,
    smtp_use_tls: true,
    smtp_use_ssl: false,
  },
};

// Configuration functions
let currentConfigName = null;

async function initConfig() {
  setupConfigForm();
  setupProviderDropdown();
  setupConfigSelector();

  await loadEmailClientConfigs();
  await loadConfig();

  // After loading config, if SMTP server is still empty and GMX is selected, populate it
  const providerSelect = document.getElementById('emailProvider');
  const smtpServer = document.getElementById('smtpServer');
  if (
    providerSelect &&
    providerSelect.value === 'gmx' &&
    smtpServer &&
    !smtpServer.value
  ) {
    populateProviderSettings(emailProviderConfigs.gmx);
  }
}

function setupConfigSelector() {
  const configSelector = document.getElementById('configSelector');
  const configNameInput = document.getElementById('configName');
  const configNameGroup = document.getElementById('configNameGroup');

  if (configSelector) {
    configSelector.addEventListener('change', async (e) => {
      const selectedName = e.target.value;
      if (selectedName) {
        // Load existing config
        currentConfigName = selectedName;
        configNameInput.value = selectedName;
        configNameInput.disabled = true;
        configNameGroup.style.display = 'none';
        await loadConfig(selectedName);
      } else {
        // Create new config
        currentConfigName = null;
        configNameInput.value = '';
        configNameInput.disabled = false;
        configNameGroup.style.display = 'block';
        clearForm();
      }
    });
  }
}

async function loadEmailClientConfigs() {
  try {
    const result = await api.getAllEmailClientConfigs();
    const configs = result.configs || {};
    const current = result.current;

    const configSelector = document.getElementById('configSelector');
    const configList = document.getElementById('configList');
    const configListItems = document.getElementById('configListItems');

    // Clear existing options except "Create New"
    if (configSelector) {
      configSelector.innerHTML =
        '<option value="">-- Create New Configuration --</option>';
    }

    // Populate selector and list
    if (Object.keys(configs).length > 0) {
      configList.classList.remove('hidden');
      configListItems.innerHTML = '';

      for (const [name, config] of Object.entries(configs)) {
        // Add to selector
        if (configSelector) {
          const option = document.createElement('option');
          option.value = name;
          option.textContent = name + (current === name ? ' (Active)' : '');
          if (current === name) {
            option.selected = true;
            currentConfigName = name;
          }
          configSelector.appendChild(option);
        }

        // Add to list
        const item = document.createElement('div');
        item.style.cssText =
          'display: flex; justify-content: space-between; align-items: center; padding: 10px; margin: 5px 0; background: white; border-radius: 4px; border: 1px solid #ddd;';
        item.innerHTML = `
                    <div>
                        <strong>${name}</strong>
                        ${
                          current === name
                            ? '<span style="color: #27ae60; margin-left: 10px;">● Active</span>'
                            : ''
                        }
                        <div style="font-size: 0.9em; color: #666; margin-top: 3px;">
                            ${config.username || 'No username'} @ ${
          config.imap_server || 'No server'
        }
                        </div>
                    </div>
                    <div>
                        ${
                          current !== name
                            ? `<button class="btn btn-secondary" style="margin-right: 5px; padding: 5px 10px; font-size: 0.9em;" onclick="setActiveConfig('${name}')">Set Active</button>`
                            : ''
                        }
                        <button class="btn btn-secondary" style="margin-right: 5px; padding: 5px 10px; font-size: 0.9em;" onclick="editConfig('${name}')">Edit</button>
                        <button class="btn btn-danger" style="padding: 5px 10px; font-size: 0.9em;" onclick="deleteConfig('${name}')">Delete</button>
                    </div>
                `;
        configListItems.appendChild(item);
      }
    } else {
      configList.classList.add('hidden');
    }
  } catch (error) {
    console.error('Failed to load email client configs:', error);
  }
}

// Make functions globally accessible for onclick handlers
window.setActiveConfig = async function (name) {
  try {
    await api.setCurrentEmailClient(name);
    showAlert(`Configuration "${name}" set as active`, 'success');
    await loadEmailClientConfigs();
  } catch (error) {
    showAlert('Failed to set active config: ' + error.message, 'error');
  }
};

window.editConfig = async function (name) {
  const configSelector = document.getElementById('configSelector');
  if (configSelector) {
    configSelector.value = name;
    configSelector.dispatchEvent(new Event('change'));
  }
};

window.deleteConfig = async function (name) {
  if (!confirm(`Are you sure you want to delete configuration "${name}"?`)) {
    return;
  }

  try {
    await api.deleteEmailClientConfig(name);
    showAlert(`Configuration "${name}" deleted`, 'success');
    await loadEmailClientConfigs();

    // Clear form if deleted config was selected
    if (currentConfigName === name) {
      const configSelector = document.getElementById('configSelector');
      if (configSelector) {
        configSelector.value = '';
        configSelector.dispatchEvent(new Event('change'));
      }
    }
  } catch (error) {
    showAlert('Failed to delete config: ' + error.message, 'error');
  }
};

function clearForm() {
  document.getElementById('imapServer').value = '';
  document.getElementById('imapPort').value = '993';
  document.getElementById('imapUsername').value = '';
  document.getElementById('imapPassword').value = '';
  document.getElementById('imapUseSSL').checked = true;
  document.getElementById('imapUseSTARTTLS').checked = false;
  document.getElementById('smtpServer').value = '';
  document.getElementById('smtpPort').value = '587';
  document.getElementById('smtpUseTLS').checked = true;
  document.getElementById('smtpUseSSL').checked = false;
  document.getElementById('emailProvider').value = 'gmx';
}

function setupConfigForm() {
  document
    .getElementById('emailClientForm')
    ?.addEventListener('submit', async (e) => {
      e.preventDefault();
      await saveEmailClientConfig();
    });

  document
    .getElementById('emailGenForm')
    ?.addEventListener('submit', async (e) => {
      e.preventDefault();
      await saveEmailGenConfig();
    });

  // Test email button
  document
    .getElementById('testEmailBtn')
    ?.addEventListener('click', async () => {
      await testEmailConfiguration();
    });

  // Modal close button
  document.querySelector('.modal-close')?.addEventListener('click', () => {
    document.getElementById('testEmailModal').classList.add('hidden');
  });

  // Confirm receipt button
  document
    .getElementById('confirmReceiptBtn')
    ?.addEventListener('click', () => {
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

async function loadConfig(configName = null) {
  try {
    // Load email client config (use provided name or current)
    const emailClientConfig = await api.getEmailClientConfig(configName);

    if (emailClientConfig && Object.keys(emailClientConfig).length > 0) {
      // Check if config matches a provider
      let matchedProvider = '';
      for (const [key, providerConfig] of Object.entries(
        emailProviderConfigs
      )) {
        if (providerConfig.imap_server === emailClientConfig.imap_server) {
          matchedProvider = key;
          break;
        }
      }

      // Set provider dropdown if matched
      if (matchedProvider) {
        document.getElementById('emailProvider').value = matchedProvider;
      }

      document.getElementById('imapServer').value =
        emailClientConfig.imap_server || '';
      document.getElementById('imapPort').value =
        emailClientConfig.imap_port || 993;
      document.getElementById('imapUsername').value =
        emailClientConfig.username || '';
      // Don't populate password if it's masked
      if (emailClientConfig.password && emailClientConfig.password !== '***') {
        document.getElementById('imapPassword').value =
          emailClientConfig.password || '';
      }
      document.getElementById('imapUseSSL').checked =
        emailClientConfig.use_ssl !== false;
      document.getElementById('imapUseSTARTTLS').checked =
        emailClientConfig.use_starttls === true;

      // Load SMTP settings
      document.getElementById('smtpServer').value =
        emailClientConfig.smtp_server || '';
      document.getElementById('smtpPort').value =
        emailClientConfig.smtp_port || 587;
      document.getElementById('smtpUseTLS').checked =
        emailClientConfig.smtp_use_tls !== false;
      document.getElementById('smtpUseSSL').checked =
        emailClientConfig.smtp_use_ssl === true;

      // If SMTP server is empty but we have IMAP server, try to populate from provider
      if (!emailClientConfig.smtp_server && emailClientConfig.imap_server) {
        const providerSelect = document.getElementById('emailProvider');
        if (providerSelect && providerSelect.value) {
          const provider = emailProviderConfigs[providerSelect.value];
          if (provider && provider.smtp_server) {
            document.getElementById('smtpServer').value = provider.smtp_server;
            document.getElementById('smtpPort').value =
              provider.smtp_port || 587;
            document.getElementById('smtpUseTLS').checked =
              provider.smtp_use_tls !== false;
            document.getElementById('smtpUseSSL').checked =
              provider.smtp_use_ssl === true;
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
    const config = await api.getConfig();
    if (config.email_generation) {
      document.getElementById('defaultRecipients').value = (
        config.email_generation.default_recipients || []
      ).join(', ');
      document.getElementById('defaultCount').value =
        config.email_generation.default_count || 1;
    }
  } catch (error) {
    console.error('Failed to load config:', error);
    showAlert('Failed to load configuration', 'error');
  }
}

async function saveEmailClientConfig() {
  const configNameInput = document.getElementById('configName');
  const configName = configNameInput.value.trim();

  if (!configName) {
    showAlert('Please enter a configuration name', 'error');
    return;
  }

  const config = {
    config_name: configName,
    imap_server: document.getElementById('imapServer').value,
    imap_port: parseInt(document.getElementById('imapPort').value),
    username: document.getElementById('imapUsername').value,
    password: document.getElementById('imapPassword').value,
    use_ssl: document.getElementById('imapUseSSL').checked,
    use_starttls: document.getElementById('imapUseSTARTTLS').checked,
    smtp_server: document.getElementById('smtpServer').value,
    smtp_port: parseInt(document.getElementById('smtpPort').value) || 587,
    smtp_use_tls: document.getElementById('smtpUseTLS').checked,
    smtp_use_ssl: document.getElementById('smtpUseSSL').checked,
  };

  try {
    await api.updateEmailClientConfig(config);
    showAlert(
      `Email client configuration "${configName}" saved successfully!`,
      'success'
    );
    currentConfigName = configName;
    await loadEmailClientConfigs();

    // Update selector to show saved config
    const configSelector = document.getElementById('configSelector');
    if (configSelector) {
      configSelector.value = configName;
      configNameInput.disabled = true;
      document.getElementById('configNameGroup').style.display = 'none';
    }
  } catch (error) {
    showAlert(
      'Failed to save email client configuration: ' + error.message,
      'error'
    );
  }
}

async function saveEmailGenConfig() {
  const recipients = document
    .getElementById('defaultRecipients')
    .value.split(',')
    .map((r) => r.trim())
    .filter((r) => r);

  const config = {
    default_recipients: recipients,
    default_count: parseInt(document.getElementById('defaultCount').value) || 1,
  };

  try {
    await api.updateConfig({ email_generation: config });
    showAlert('Email generation configuration saved successfully!', 'success');
  } catch (error) {
    showAlert(
      'Failed to save email generation configuration: ' + error.message,
      'error'
    );
  }
}

async function testEmailConfiguration() {
  // Get default recipient
  const defaultRecipients = document
    .getElementById('defaultRecipients')
    .value.split(',')
    .map((r) => r.trim())
    .filter((r) => r);

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
    smtp_use_ssl: document.getElementById('smtpUseSSL').checked,
  };

  // Validate configuration
  if (
    !emailClientConfig.imap_server ||
    !emailClientConfig.username ||
    !emailClientConfig.password
  ) {
    showAlert(
      'Please fill in all required email client configuration fields',
      'error'
    );
    return;
  }

  // Show modal
  const modal = document.getElementById('testEmailModal');
  modal.classList.remove('hidden');

  // Reset modal content
  document.getElementById('testEmailStatus').innerHTML =
    '<p class="loading">Testing email configuration...</p>';
  document.getElementById('testEmailConnectionInfo').classList.add('hidden');
  document.getElementById('testEmailActions').classList.add('hidden');

  try {
    const result = await api.testEmailConfig(recipient, emailClientConfig);

    if (result.success) {
      // Show success message
      document.getElementById(
        'testEmailStatus'
      ).innerHTML = `<div class="alert alert-success">
                    <strong>Success!</strong> Test email sent successfully to ${recipient}
                </div>`;

      // Show connection information
      const connInfo = result.connection_info;
      const connectionText = `IMAP Connection:
Server: ${connInfo.imap_server || 'N/A'}:${connInfo.imap_port || 993}
Username: ${connInfo.username || 'N/A'}
Encryption: ${
        connInfo.imap_use_ssl
          ? 'SSL'
          : connInfo.imap_use_starttls
          ? 'STARTTLS'
          : 'None'
      }

SMTP Connection:
Server: ${connInfo.smtp_server || 'N/A'}:${connInfo.smtp_port || 587}
Username: ${connInfo.username || 'N/A'}
Encryption: ${connInfo.use_ssl ? 'SSL' : connInfo.use_tls ? 'TLS' : 'None'}

Test Email Details:
Recipient: ${connInfo.recipient || 'N/A'}
Subject: ${result.subject || 'N/A'}`;

      document.getElementById('connectionDetails').innerHTML = `
                <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; font-size: 13px; line-height: 1.6;">${connectionText}</pre>
            `;
      document
        .getElementById('testEmailConnectionInfo')
        .classList.remove('hidden');

      // Show confirmation buttons
      document.getElementById('testEmailActions').classList.remove('hidden');
    } else {
      // Show error message
      document.getElementById(
        'testEmailStatus'
      ).innerHTML = `<div class="alert alert-error">
                    <strong>Error:</strong> ${
                      result.error || 'Failed to send test email'
                    }
                </div>`;

      // Show connection information and connection attempt details on error
      if (result.connection_info) {
        const connInfo = result.connection_info;
        let connectionText = `IMAP Connection:
Server: ${connInfo.imap_server || 'N/A'}:${connInfo.imap_port || 993}
Username: ${connInfo.username || 'N/A'}
Encryption: ${
          connInfo.imap_use_ssl
            ? 'SSL'
            : connInfo.imap_use_starttls
            ? 'STARTTLS'
            : 'None'
        }

SMTP Connection:
Server: ${connInfo.smtp_server || 'N/A'}:${connInfo.smtp_port || 587}
Username: ${connInfo.username || 'N/A'}
Encryption: ${connInfo.use_ssl ? 'SSL' : connInfo.use_tls ? 'TLS' : 'None'}

Test Email Details:
Recipient: ${connInfo.recipient || 'N/A'}`;

        // Add connection attempt details if available
        if (result.error_details) {
          connectionText += `\n\n${result.error_details}`;
        } else if (result.connection_attempt) {
          const attempt = result.connection_attempt;
          connectionText += `\n\nConnection Attempt:
Server: ${attempt.attempted_server || 'N/A'}
Username: ${attempt.attempted_username || 'N/A'}
Encryption: ${attempt.attempted_encryption || 'N/A'}
Method: ${attempt.connection_method || 'N/A'}`;
        }

        document.getElementById('connectionDetails').innerHTML = `
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; font-size: 13px; line-height: 1.6; color: #d32f2f;">${connectionText}</pre>
                `;
        document
          .getElementById('testEmailConnectionInfo')
          .classList.remove('hidden');
      }
    }
  } catch (error) {
    document.getElementById(
      'testEmailStatus'
    ).innerHTML = `<div class="alert alert-error">
                <strong>Error:</strong> ${error.message}
            </div>`;

    // Show error details if available
    if (error.connection_attempt || error.error_details) {
      let errorText = `Connection Error:\n${error.message || 'Unknown error'}`;

      if (error.error_details) {
        errorText += `\n\n${error.error_details}`;
      } else if (error.connection_attempt) {
        const attempt = error.connection_attempt;
        errorText += `\n\nConnection Attempt:
Server: ${attempt.attempted_server || 'N/A'}
Username: ${attempt.attempted_username || 'N/A'}
Encryption: ${attempt.attempted_encryption || 'N/A'}
Method: ${attempt.connection_method || 'N/A'}`;
      }

      document.getElementById('connectionDetails').innerHTML = `
                <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; font-size: 13px; line-height: 1.6; color: #d32f2f;">${errorText}</pre>
            `;
      document
        .getElementById('testEmailConnectionInfo')
        .classList.remove('hidden');
    }
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
