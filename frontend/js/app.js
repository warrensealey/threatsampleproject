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
let customTemplates = {};
let schedulesCache = [];

async function initDashboard() {
  await loadHistory();
  await loadDefaultRecipients();
  await loadCustomTemplates();
  setupSendButtons();
  setupEmailSendModal();
  await loadSchedules();
  setupScheduleUI();

  // Custom templates: save button handler
  const saveTemplateBtn = document.getElementById('saveCustomTemplateBtn');
  if (saveTemplateBtn) {
    saveTemplateBtn.addEventListener('click', async () => {
      const subject = document.getElementById('customSubject').value.trim();
      const body = document.getElementById('customBody').value.trim();
      const displayName = document
        .getElementById('customDisplayName')
        .value.trim();
      const attachmentType =
        document.getElementById('customAttachment').value || null;

      if (!subject || !body) {
        showAlert(
          'Please enter both subject and body before saving a template.',
          'error'
        );
        return;
      }

      const name = prompt(
        'Enter a name for this template (e.g., "Test campaign 1"):'
      );
      if (!name || !name.trim()) {
        return;
      }

      try {
        await api.saveTemplate('custom', name.trim(), {
          subject,
          body,
          display_name: displayName || '',
          attachment_type: attachmentType,
        });
        showAlert(`Template "${name.trim()}" saved successfully.`, 'success');
        await loadCustomTemplates();
      } catch (error) {
        showAlert('Failed to save template: ' + error.message, 'error');
      }
    });
  }
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

// ---------------------------------------------------------------------------
// Scheduled sends (dashboard)
// ---------------------------------------------------------------------------

async function loadSchedules() {
  try {
    const data = await api.getSchedules();
    const schedulesDiv = document.getElementById('schedulesTable');
    if (!schedulesDiv) return;

    const schedules = data.schedules || [];
    const tz = data.timezone || 'UTC';
    schedulesCache = schedules;

    if (!schedules.length) {
      schedulesDiv.innerHTML =
        '<p class="loading">No schedules defined yet. Click \"Create Schedule\" to add one.</p>';
      return;
    }

    let html =
      '<table class="history-table"><thead><tr><th>Name</th><th>Type</th><th>Email Type</th><th>Recipients</th><th>Next Run (UTC)</th><th>Enabled</th><th>Last Status</th><th>Actions</th></tr></thead><tbody>';

    schedules.forEach((s) => {
      const nextRun =
        s.next_run_utc && typeof s.next_run_utc === 'string'
          ? new Date(s.next_run_utc).toLocaleString()
          : 'N/A';
      const recipients = Array.isArray(s.recipients)
        ? s.recipients.join(', ')
        : '';
      html += `<tr>
        <td>${s.name || ''}</td>
        <td>${s.schedule_type || 'one_off'}</td>
        <td>${s.email_type || ''}</td>
        <td>${recipients}</td>
        <td>${nextRun}</td>
        <td>${s.enabled ? 'Yes' : 'No'}</td>
        <td>${s.last_status || ''}</td>
        <td>
          <button class="btn btn-secondary btn-small" data-action="edit-schedule" data-id="${
            s.id
          }">Edit</button>
          <button class="btn btn-secondary btn-small" data-action="toggle-schedule" data-id="${
            s.id
          }">${s.enabled ? 'Disable' : 'Enable'}</button>
          <button class="btn btn-danger btn-small" data-action="delete-schedule" data-id="${
            s.id
          }">Delete</button>
        </td>
      </tr>`;
    });

    html += '</tbody></table>';
    html += `<p style="margin-top: 8px; font-size: 0.85em; color: #666;">Times shown are converted from UTC using your browser's locale. Application timezone: ${tz}</p>`;
    schedulesDiv.innerHTML = html;
  } catch (error) {
    console.error('Failed to load schedules:', error);
    const schedulesDiv = document.getElementById('schedulesTable');
    if (schedulesDiv) {
      schedulesDiv.innerHTML =
        '<p class="alert alert-error">Failed to load schedules.</p>';
    }
  }
}

function setupScheduleUI() {
  const createBtn = document.getElementById('createScheduleBtn');
  const scheduleModal = document.getElementById('scheduleModal');
  const scheduleModalClose = document.getElementById('scheduleModalClose');
  const scheduleCancelBtn = document.getElementById('scheduleCancelBtn');
  const scheduleForm = document.getElementById('scheduleForm');
  const scheduleTypeSelect = document.getElementById('scheduleType');

  if (!createBtn || !scheduleModal || !scheduleForm || !scheduleTypeSelect) {
    return;
  }

  const scheduleOneOffFields = document.getElementById('scheduleOneOffFields');
  const scheduleIntervalFields = document.getElementById(
    'scheduleIntervalFields'
  );
  const scheduleWeeklyFields = document.getElementById('scheduleWeeklyFields');

  const updateScheduleTypeVisibility = () => {
    const type = scheduleTypeSelect.value;
    if (scheduleOneOffFields) {
      scheduleOneOffFields.classList.toggle('hidden', type !== 'one_off');
    }
    if (scheduleIntervalFields) {
      scheduleIntervalFields.classList.toggle('hidden', type !== 'interval');
    }
    if (scheduleWeeklyFields) {
      scheduleWeeklyFields.classList.toggle('hidden', type !== 'weekly');
    }
  };

  scheduleTypeSelect.addEventListener('change', updateScheduleTypeVisibility);
  updateScheduleTypeVisibility();

  createBtn.addEventListener('click', async () => {
    await populateScheduleConfigNames();
    openScheduleModal();
  });

  scheduleModalClose?.addEventListener('click', () => {
    scheduleModal.classList.add('hidden');
  });

  scheduleCancelBtn?.addEventListener('click', () => {
    scheduleModal.classList.add('hidden');
  });

  scheduleModal.addEventListener('click', (e) => {
    if (e.target.id === 'scheduleModal') {
      scheduleModal.classList.add('hidden');
    }
  });

  scheduleForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await saveScheduleFromForm();
  });

  // Delegate actions from schedules table
  const schedulesTable = document.getElementById('schedulesTable');
  if (schedulesTable) {
    schedulesTable.addEventListener('click', async (e) => {
      const target = e.target;
      if (!(target instanceof HTMLElement)) return;
      const action = target.getAttribute('data-action');
      const id = target.getAttribute('data-id');
      if (!action || !id) return;

      if (action === 'edit-schedule') {
        await populateScheduleConfigNames();
        const schedule = schedulesCache.find((s) => s.id === id);
        if (schedule) {
          openScheduleModal(schedule);
        }
      } else if (action === 'toggle-schedule') {
        const schedule = schedulesCache.find((s) => s.id === id);
        if (!schedule) return;
        const newEnabled = !schedule.enabled;
        try {
          await api.toggleSchedule(id, newEnabled);
          await loadSchedules();
        } catch (error) {
          showAlert('Failed to toggle schedule: ' + error.message, 'error');
        }
      } else if (action === 'delete-schedule') {
        if (!confirm('Are you sure you want to delete this schedule?')) {
          return;
        }
        try {
          await api.deleteSchedule(id);
          await loadSchedules();
        } catch (error) {
          showAlert('Failed to delete schedule: ' + error.message, 'error');
        }
      }
    });
  }
}

async function populateScheduleConfigNames() {
  try {
    const result = await api.getAllEmailClientConfigs();
    const configs = result.configs || {};
    const current = result.current;
    const select = document.getElementById('scheduleConfigName');
    if (!select) return;

    select.innerHTML =
      '<option value=\"\">Use current active configuration</option>';
    Object.keys(configs)
      .sort()
      .forEach((name) => {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name + (current === name ? ' (Active)' : '');
        select.appendChild(opt);
      });
  } catch (error) {
    console.error('Failed to load configs for schedules:', error);
  }
}

function openScheduleModal(schedule = null) {
  const modal = document.getElementById('scheduleModal');
  const title = document.getElementById('scheduleModalTitle');
  const idInput = document.getElementById('scheduleId');
  const nameInput = document.getElementById('scheduleName');
  const emailTypeSelect = document.getElementById('scheduleEmailType');
  const recipientsInput = document.getElementById('scheduleRecipients');
  const countInput = document.getElementById('scheduleCount');
  const configSelect = document.getElementById('scheduleConfigName');
  const typeSelect = document.getElementById('scheduleType');
  const oneOffInput = document.getElementById('scheduleOneOffDateTime');
  const intervalHoursInput = document.getElementById('scheduleIntervalHours');
  const weeklyTimeInput = document.getElementById('scheduleWeeklyTime');

  const weekdayCheckboxes = Array.from(
    document.querySelectorAll('.scheduleWeekday')
  );

  if (!modal || !title) return;

  if (schedule) {
    title.textContent = 'Edit Schedule';
    idInput.value = schedule.id || '';
    nameInput.value = schedule.name || '';
    emailTypeSelect.value = schedule.email_type || 'phishing';
    recipientsInput.value = Array.isArray(schedule.recipients)
      ? schedule.recipients.join(', ')
      : '';
    countInput.value = schedule.count || 1;
    if (configSelect) {
      configSelect.value = schedule.config_name || '';
    }
    typeSelect.value = schedule.schedule_type || 'one_off';
    if (schedule.schedule_type === 'one_off' && schedule.next_run_utc) {
      // Convert ISO string to datetime-local value
      const dt = new Date(schedule.next_run_utc);
      const local = new Date(
        dt.getTime() - dt.getTimezoneOffset() * 60000
      ).toISOString();
      oneOffInput.value = local.substring(0, 16);
    } else {
      oneOffInput.value = '';
    }
    intervalHoursInput.value = schedule.interval_hours || 24;
    const weeklyDays = Array.isArray(schedule.weekly_days)
      ? schedule.weekly_days
      : [];
    weekdayCheckboxes.forEach((cb) => {
      cb.checked = weeklyDays.includes(cb.value);
    });
    weeklyTimeInput.value = schedule.time_of_day_local || '09:00';
  } else {
    title.textContent = 'Create Schedule';
    idInput.value = '';
    nameInput.value = '';
    emailTypeSelect.value = 'phishing';
    recipientsInput.value =
      defaultRecipients.length > 0 ? defaultRecipients.join(', ') : '';
    countInput.value = 1;
    if (configSelect) {
      configSelect.value = '';
    }
    typeSelect.value = 'one_off';
    oneOffInput.value = '';
    intervalHoursInput.value = 24;
    weekdayCheckboxes.forEach((cb) => {
      cb.checked = false;
    });
    weeklyTimeInput.value = '09:00';
  }

  const scheduleTypeSelect = document.getElementById('scheduleType');
  if (scheduleTypeSelect) {
    const event = new Event('change');
    scheduleTypeSelect.dispatchEvent(event);
  }

  modal.classList.remove('hidden');
}

async function saveScheduleFromForm() {
  const id = document.getElementById('scheduleId').value || null;
  const name = document.getElementById('scheduleName').value.trim();
  const emailType = document.getElementById('scheduleEmailType').value;
  const recipientsStr = document
    .getElementById('scheduleRecipients')
    .value.trim();
  const count = parseInt(document.getElementById('scheduleCount').value) || 1;
  const configName = document.getElementById('scheduleConfigName').value || null;
  const scheduleType = document.getElementById('scheduleType').value;

  if (!name) {
    showAlert('Schedule name is required', 'error');
    return;
  }

  const recipients = recipientsStr
    .split(',')
    .map((r) => r.trim())
    .filter((r) => r);
  if (!recipients.length) {
    showAlert('At least one recipient is required', 'error');
    return;
  }

  const schedule = {
    id: id || undefined,
    name,
    email_type: emailType,
    recipients,
    count,
    config_name: configName || undefined,
    schedule_type: scheduleType,
    enabled: true,
  };

  if (scheduleType === 'interval') {
    const intervalHours =
      parseInt(document.getElementById('scheduleIntervalHours').value) || 24;
    schedule.interval_hours = intervalHours;
  } else if (scheduleType === 'weekly') {
    const weeklyTime = document.getElementById('scheduleWeeklyTime').value;
    const weekdayCheckboxes = Array.from(
      document.querySelectorAll('.scheduleWeekday')
    );
    const weeklyDays = weekdayCheckboxes
      .filter((cb) => cb.checked)
      .map((cb) => cb.value);
    if (!weeklyDays.length) {
      showAlert('Please select at least one weekday for a weekly schedule', 'error');
      return;
    }
    schedule.weekly_days = weeklyDays;
    schedule.time_of_day_local = weeklyTime || '09:00';
  } else if (scheduleType === 'one_off') {
    const oneOffValue = document
      .getElementById('scheduleOneOffDateTime')
      .value.trim();
    if (!oneOffValue) {
      showAlert(
        'Please choose a run date and time for a one-off schedule.',
        'error'
      );
      return;
    }
    // Convert local datetime-local value to UTC ISO string
    const local = new Date(oneOffValue);
    const utc = new Date(local.getTime() - local.getTimezoneOffset() * 60000);
    schedule.next_run_utc = utc.toISOString();
  }

  try {
    await api.saveSchedule(schedule);
    showAlert('Schedule saved successfully', 'success');
    document.getElementById('scheduleModal').classList.add('hidden');
    await loadSchedules();
  } catch (error) {
    showAlert('Failed to save schedule: ' + error.message, 'error');
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
    // Load templates into config page list
    await loadTemplateList();
  } catch (error) {
    console.error('Failed to load config:', error);
    showAlert('Failed to load configuration', 'error');
  }
}

async function loadCustomTemplates() {
  try {
    const result = await api.getTemplates('custom');
    customTemplates = result.templates || {};

    const select = document.getElementById('customTemplateSelect');
    if (!select) return;

    // Reset options
    select.innerHTML = '<option value="">-- No Template --</option>';

    Object.keys(customTemplates)
      .sort()
      .forEach((name) => {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        select.appendChild(opt);
      });

    select.onchange = () => {
      const tplName = select.value;
      if (!tplName || !customTemplates[tplName]) {
        return;
      }
      const tpl = customTemplates[tplName];
      if (tpl.subject) {
        document.getElementById('customSubject').value = tpl.subject;
      }
      if (tpl.body) {
        document.getElementById('customBody').value = tpl.body;
      }
      if (typeof tpl.display_name === 'string') {
        document.getElementById('customDisplayName').value = tpl.display_name;
      }
      if (tpl.attachment_type) {
        document.getElementById('customAttachment').value = tpl.attachment_type;
      }
    };
  } catch (error) {
    console.error('Failed to load custom templates:', error);
  }
}

async function loadTemplateList() {
  const container = document.getElementById('templateList');
  if (!container) return;

  container.innerHTML = '<p class="loading">Loading templates...</p>';

  try {
    const result = await api.getTemplates();
    const templates = result.templates || {};

    const types = Object.keys(templates);
    if (types.length === 0) {
      container.innerHTML =
        '<p class="loading">No templates saved yet. Use the Custom Email dialog on the dashboard to create one.</p>';
      return;
    }

    let html = '';
    types.sort().forEach((type) => {
      const typeTemplates = templates[type] || {};
      const names = Object.keys(typeTemplates);
      if (names.length === 0) {
        return;
      }
      html += `<h3 style="margin-top: 10px;">${type} templates</h3>`;
      html += '<ul style="list-style: none; padding-left: 0;">';
      names.sort().forEach((name) => {
        html += `<li style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #eee;">
              <span><strong>${name}</strong></span>
              <button class="btn btn-secondary template-delete-btn"
                      style="padding: 4px 8px; font-size: 0.85em;"
                      data-template-type="${type}"
                      data-template-name="${name}">
                Delete
              </button>
            </li>`;
      });
      html += '</ul>';
    });

    container.innerHTML =
      html || '<p class="loading">No templates saved yet.</p>';

    // Attach delete handlers
    container.querySelectorAll('.template-delete-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const type = btn.getAttribute('data-template-type');
        const name = btn.getAttribute('data-template-name');
        if (type && name) {
          window.deleteTemplateConfig(type, name);
        }
      });
    });
  } catch (error) {
    console.error('Failed to load templates:', error);
    container.innerHTML =
      '<p class="alert alert-error">Failed to load templates.</p>';
  }
}

// Expose template delete for config page list
window.deleteTemplateConfig = async function (type, name) {
  if (
    !confirm(
      `Are you sure you want to delete template "${name}" of type "${type}"?`
    )
  ) {
    return;
  }

  try {
    await api.deleteTemplate(type, name);
    showAlert(`Template "${name}" deleted.`, 'success');
    await loadTemplateList();
    // Refresh custom templates in dashboard if on that page
    await loadCustomTemplates();
  } catch (error) {
    showAlert('Failed to delete template: ' + error.message, 'error');
  }
};

async function saveEmailClientConfig() {
  const configNameInput = document.getElementById('configName');
  const configName = configNameInput.value.trim();

  if (!configName) {
    showConfigSaveModal(
      'Missing Configuration Name',
      'Please enter a configuration name before saving.',
      'error'
    );
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
    showConfigSaveModal(
      'Email Client Configuration Saved',
      `Email client configuration "${configName}" was saved successfully.`,
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
    showConfigSaveModal(
      'Failed to Save Email Client Configuration',
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
    showConfigSaveModal(
      'Email Generation Configuration Saved',
      'Email generation configuration was saved successfully.',
      'success'
    );
  } catch (error) {
    showConfigSaveModal(
      'Failed to Save Email Generation Configuration',
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
    showConfigSaveModal(
      'Missing Required Fields',
      'Please fill in IMAP server, username, and password before testing the configuration.',
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

function showConfigSaveModal(title, message, type) {
  const modal = document.getElementById('configSaveModal');
  const modalTitle = document.getElementById('configSaveModalTitle');
  const modalBody = document.getElementById('configSaveModalBody');
  const okBtn = document.getElementById('configSaveModalOkBtn');
  const closeBtn = document.getElementById('configSaveModalClose');

  if (!modal || !modalTitle || !modalBody || !okBtn || !closeBtn) {
    // Fallback to inline alert if modal markup is missing
    showAlert(message, type);
    return;
  }

  modalTitle.textContent = title;
  modalBody.innerHTML = `
    <div class="alert alert-${type === 'error' ? 'error' : 'success'}">
      ${message}
    </div>
  `;

  const hideModal = () => {
    modal.classList.add('hidden');
  };

  // Ensure previous listeners don't stack
  okBtn.onclick = hideModal;
  closeBtn.onclick = hideModal;

  modal.onclick = (e) => {
    if (e.target.id === 'configSaveModal') {
      hideModal();
    }
  };

  modal.classList.remove('hidden');
}
