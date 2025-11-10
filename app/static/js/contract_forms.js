/**
 * Contract Forms - Formular-Generatoren für Contract Workflow
 * Sterbegeldversicherung
 */

// Form Renderer Mapping
const FORM_RENDERERS = {
    'health_check': renderHealthCheckForm,
    'personal_data': renderPersonalDataForm,
    'policyholder': renderPolicyholderForm,
    'beneficiary': renderBeneficiaryForm,
    'bank_details': renderBankDetailsForm,
    'summary': renderSummaryForm
};

/**
 * Main entry: Render form based on type
 */
function renderForm(formType, prefillData = {}, contextMessage = '') {
    const renderer = FORM_RENDERERS[formType];
    if (!renderer) {
        console.error(`Unknown form type: ${formType}`);
        return '<div class="error">Formular-Typ nicht gefunden</div>';
    }
    
    return renderer(prefillData, contextMessage);
}

/**
 * 1. Health Check Form
 */
function renderHealthCheckForm(prefillData = {}, contextMessage = '') {
    return `
        <form class="inline-form health-check-form" data-form-type="health_check">
            <h4>Gesundheitserklärung</h4>
            
            <div class="health-declaration">
                <p><strong>Die versicherte Person bestätigt, dass Sie in den letzten 5 Jahren für keine der folgenden Erkrankungen in ärztlicher Behandlung war:</strong></p>
                <ul>
                    <li>Krebs/Tumore</li>
                    <li>Herz- und Gefäßkrankheiten</li>
                    <li>Alkohol- oder Drogensucht</li>
                    <li>Neurologische, psychische Störungen</li>
                    <li>HIV/Aids</li>
                    <li>Eine der folgenden Krankheiten: COPD, Lungenfibrose, Niereninsuffizienz, polyzystische Nierenerkrankung, Cholangitis, Leberzirrhose</li>
                </ul>
                
                <p>Des Weiteren bestätigt die versicherte Person, in den letzten 2 Jahren keine apothekenpflichtigen Medikamente länger als 6 Wochen ununterbrochen verwendet zu haben.</p>
                
                <p><strong>Nicht zu nennen sind:</strong></p>
                <ul>
                    <li>Medikamente gegen Heuschnupfen/Allergien</li>
                    <li>Gicht/erhöhte Harnsäurewerte</li>
                    <li>Anti-Babypille</li>
                    <li>Schilddrüse</li>
                    <li>Erhöhte Magensäure</li>
                </ul>
            </div>
            
            <div class="form-group checkbox-group">
                <label class="checkbox-label">
                    <input type="checkbox" name="confirmed" required>
                    <span>Ich bestätige die Gesundheitserklärung</span>
                </label>
            </div>
            
            <button type="submit" class="form-submit-btn">Bestätigen</button>
        </form>
    `;
}

/**
 * 2. Personal Data Form
 */
function renderPersonalDataForm(prefillData = {}, contextMessage = '') {
    return `
        <form class="inline-form personal-data-form" data-form-type="personal_data">
            <h4>Persönliche Daten des Versicherten</h4>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="firstname">Vorname *</label>
                    <input type="text" id="firstname" name="firstname" 
                           value="${prefillData.firstname || ''}" 
                           placeholder="Max" required>
                </div>
                
                <div class="form-group">
                    <label for="lastname">Nachname *</label>
                    <input type="text" id="lastname" name="lastname" 
                           value="${prefillData.lastname || ''}" 
                           placeholder="Mustermann" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="birthdate">Geburtsdatum *</label>
                    <input type="text" id="birthdate" name="birthdate" 
                           value="${prefillData.birthdate || ''}" 
                           placeholder="15.05.1980" 
                           pattern="\\d{2}\\.\\d{2}\\.\\d{4}" 
                           class="${prefillData.birthdate_readonly ? 'birthdate-prefilled' : ''}"
                           ${prefillData.birthdate_readonly ? 'readonly' : ''} required>
                </div>
                
                <div class="form-group">
                    <label for="phone">Telefon *</label>
                    <input type="tel" id="phone" name="phone" 
                           value="${prefillData.phone || ''}" 
                           placeholder="+49 123 456789" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group form-group-small">
                    <label for="zipcode">PLZ *</label>
                    <input type="text" id="zipcode" name="zipcode" 
                           value="${prefillData.zipcode || ''}" 
                           placeholder="80331" 
                           pattern="[0-9]{5}" 
                           maxlength="5" required>
                </div>
                
                <div class="form-group form-group-large">
                    <label for="city">Stadt *</label>
                    <input type="text" id="city" name="city" 
                           value="${prefillData.city || ''}" 
                           placeholder="München" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group form-group-large">
                    <label for="street">Straße *</label>
                    <input type="text" id="street" name="street" 
                           value="${prefillData.street || ''}" 
                           placeholder="Musterstraße" required>
                </div>
                
                <div class="form-group form-group-small">
                    <label for="housenumber">Nr. *</label>
                    <input type="text" id="housenumber" name="housenumber" 
                           value="${prefillData.housenumber || ''}" 
                           placeholder="123" required>
                </div>
            </div>
            
            <div class="form-group">
                <label for="nationality">Staatsangehörigkeit *</label>
                <select id="nationality" name="nationality" required>
                    <option value="Deutsch" ${prefillData.nationality === 'Deutsch' ? 'selected' : ''}>Deutsch</option>
                    <option value="Österreichisch" ${prefillData.nationality === 'Österreichisch' ? 'selected' : ''}>Österreichisch</option>
                    <option value="Schweizerisch" ${prefillData.nationality === 'Schweizerisch' ? 'selected' : ''}>Schweizerisch</option>
                    <option value="Andere EU" ${prefillData.nationality === 'Andere EU' ? 'selected' : ''}>Andere EU</option>
                    <option value="Nicht-EU" ${prefillData.nationality === 'Nicht-EU' ? 'selected' : ''}>Nicht-EU</option>
                </select>
            </div>
            
            <button type="submit" class="form-submit-btn">Weiter</button>
        </form>
    `;
}

/**
 * Helper: Render personal data fields (for reuse in policyholder)
 */
function renderPersonalDataFields(prefillData = {}, prefix = '') {
    const namePrefix = prefix ? `${prefix}_` : '';
    return `
        <div class="form-row">
            <div class="form-group">
                <label for="${namePrefix}firstname">Vorname *</label>
                <input type="text" id="${namePrefix}firstname" name="${namePrefix}firstname" 
                       value="${prefillData.firstname || ''}" 
                       placeholder="Max" required>
            </div>
            
            <div class="form-group">
                <label for="${namePrefix}lastname">Nachname *</label>
                <input type="text" id="${namePrefix}lastname" name="${namePrefix}lastname" 
                       value="${prefillData.lastname || ''}" 
                       placeholder="Mustermann" required>
            </div>
        </div>
        
        <div class="form-row">
            <div class="form-group">
                <label for="${namePrefix}birthdate">Geburtsdatum *</label>
                <input type="text" id="${namePrefix}birthdate" name="${namePrefix}birthdate" 
                       value="${prefillData.birthdate || ''}" 
                       placeholder="15.05.1980" 
                       pattern="\\d{2}\\.\\d{2}\\.\\d{4}" required>
                <small>Format: TT.MM.JJJJ</small>
            </div>
            
            <div class="form-group">
                <label for="${namePrefix}phone">Telefon *</label>
                <input type="tel" id="${namePrefix}phone" name="${namePrefix}phone" 
                       value="${prefillData.phone || ''}" 
                       placeholder="+49 123 456789" required>
            </div>
        </div>
        
        <div class="form-row">
            <div class="form-group form-group-small">
                <label for="${namePrefix}zipcode">PLZ *</label>
                <input type="text" id="${namePrefix}zipcode" name="${namePrefix}zipcode" 
                       value="${prefillData.zipcode || ''}" 
                       placeholder="80331" 
                       pattern="[0-9]{5}" 
                       maxlength="5" required>
            </div>
            
            <div class="form-group form-group-large">
                <label for="${namePrefix}city">Stadt *</label>
                <input type="text" id="${namePrefix}city" name="${namePrefix}city" 
                       value="${prefillData.city || ''}" 
                       placeholder="München" required>
            </div>
        </div>
        
        <div class="form-row">
            <div class="form-group form-group-large">
                <label for="${namePrefix}street">Straße *</label>
                <input type="text" id="${namePrefix}street" name="${namePrefix}street" 
                       value="${prefillData.street || ''}" 
                       placeholder="Musterstraße" required>
            </div>
            
            <div class="form-group form-group-small">
                <label for="${namePrefix}housenumber">Nr. *</label>
                <input type="text" id="${namePrefix}housenumber" name="${namePrefix}housenumber" 
                       value="${prefillData.housenumber || ''}" 
                       placeholder="123" required>
            </div>
        </div>
        
        <div class="form-group">
            <label for="${namePrefix}nationality">Staatsangehörigkeit *</label>
            <select id="${namePrefix}nationality" name="${namePrefix}nationality" required>
                <option value="Deutsch" ${prefillData.nationality === 'Deutsch' ? 'selected' : ''}>Deutsch</option>
                <option value="Österreichisch">Österreichisch</option>
                <option value="Schweizerisch">Schweizerisch</option>
                <option value="Andere EU">Andere EU</option>
                <option value="Nicht-EU">Nicht-EU</option>
            </select>
        </div>
    `;
}

/**
 * Helper: Render address fields
 */
function renderAddressFields(prefillData = {}, prefix = '', required = true) {
    const namePrefix = prefix ? `${prefix}_` : '';
    const requiredAttr = required ? 'required' : '';
    return `
        <div class="form-row">
            <div class="form-group form-group-small">
                <label for="${namePrefix}zipcode">PLZ *</label>
                <input type="text" id="${namePrefix}zipcode" name="${namePrefix}zipcode" 
                       value="${prefillData.zipcode || ''}" 
                       placeholder="80331" 
                       pattern="[0-9]{5}" 
                       maxlength="5" ${requiredAttr}>
            </div>
            
            <div class="form-group form-group-large">
                <label for="${namePrefix}city">Stadt *</label>
                <input type="text" id="${namePrefix}city" name="${namePrefix}city" 
                       value="${prefillData.city || ''}" 
                       placeholder="München" ${requiredAttr}>
            </div>
        </div>
        
        <div class="form-row">
            <div class="form-group form-group-large">
                <label for="${namePrefix}street">Straße *</label>
                <input type="text" id="${namePrefix}street" name="${namePrefix}street" 
                       value="${prefillData.street || ''}" 
                       placeholder="Musterstraße" ${requiredAttr}>
            </div>
            
            <div class="form-group form-group-small">
                <label for="${namePrefix}housenumber">Nr. *</label>
                <input type="text" id="${namePrefix}housenumber" name="${namePrefix}housenumber" 
                       value="${prefillData.housenumber || ''}" 
                       placeholder="123" ${requiredAttr}>
            </div>
        </div>
    `;
}

/**
 * 3. Policyholder Form
 */
function renderPolicyholderForm(prefillData = {}, contextMessage = '') {
    const isChecked = prefillData.same_as_insured !== false;
    return `
        <form class="inline-form policyholder-form" data-form-type="policyholder">
            <h4>Versicherungsnehmer</h4>
            
            <div class="form-group checkbox-group">
                <label class="checkbox-label">
                    <input type="checkbox" id="same_as_insured" name="same_as_insured" 
                           ${isChecked ? 'checked' : ''}
                           onchange="togglePolicyholderFields(this)">
                    <span>Versicherungsnehmer ist gleich wie versicherte Person</span>
                </label>
            </div>
            
            <div id="policyholder-fields" style="display: ${isChecked ? 'none' : 'block'}">
                ${renderPersonalDataFields(prefillData.policyholder || {}, 'ph')}
            </div>
            
            <button type="submit" class="form-submit-btn">Weiter</button>
        </form>
    `;
}

/**
 * 4. Beneficiary Form
 */
function renderBeneficiaryForm(prefillData = {}, contextMessage = '') {
    const isLegal = !prefillData.type || prefillData.type === 'legal_succession';
    const sameAddress = prefillData.same_address === true;
    
    return `
        <form class="inline-form beneficiary-form" data-form-type="beneficiary">
            <h4>Begünstigter im Todesfall</h4>
            
            <div class="form-group radio-group">
                <label>Wer soll die Versicherungssumme erhalten? *</label>
                
                <label class="radio-label">
                    <input type="radio" name="type" value="legal_succession" 
                           ${isLegal ? 'checked' : ''} required
                           onchange="toggleBeneficiaryFields(this)">
                    <span>Gesetzliche Erbfolge</span>
                </label>
                
                <label class="radio-label">
                    <input type="radio" name="type" value="individual" 
                           ${!isLegal ? 'checked' : ''} required
                           onchange="toggleBeneficiaryFields(this)">
                    <span>Individuelle Person(en) benennen</span>
                </label>
            </div>
            
            <div id="beneficiary-fields" style="display: ${isLegal ? 'none' : 'block'}">
                <div class="form-row">
                    <div class="form-group">
                        <label for="beneficiary_firstname">Vorname *</label>
                        <input type="text" id="beneficiary_firstname" name="beneficiary_firstname" 
                               value="${prefillData.beneficiary_firstname || ''}" 
                               placeholder="Anna"
                               ${!isLegal ? 'required' : ''}>
                    </div>
                    
                    <div class="form-group">
                        <label for="beneficiary_lastname">Nachname *</label>
                        <input type="text" id="beneficiary_lastname" name="beneficiary_lastname" 
                               value="${prefillData.beneficiary_lastname || ''}" 
                               placeholder="Mustermann"
                               ${!isLegal ? 'required' : ''}>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="beneficiary_birthdate">Geburtsdatum *</label>
                    <input type="text" id="beneficiary_birthdate" name="beneficiary_birthdate" 
                           value="${prefillData.beneficiary_birthdate || ''}" 
                           placeholder="15.05.1990" 
                           pattern="\\d{2}\\.\\d{2}\\.\\d{4}"
                           ${!isLegal ? 'required' : ''}>
                    <small>Format: TT.MM.JJJJ</small>
                </div>
                
                <div class="form-group checkbox-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="same_address" name="same_address"
                               ${sameAddress ? 'checked' : ''}
                               onchange="toggleBeneficiaryAddress(this)">
                        <span>Adresse gleich wie versicherte Person</span>
                    </label>
                </div>
                
                <div id="beneficiary-address" style="display: ${sameAddress ? 'none' : 'block'}">
                    ${renderAddressFields(prefillData.address || {}, 'ben', !sameAddress)}
                </div>
            </div>
            
            <button type="submit" class="form-submit-btn">Weiter</button>
        </form>
    `;
}

/**
 * 5. Bank Details Form
 */
function renderBankDetailsForm(prefillData = {}, contextMessage = '') {
    return `
        <form class="inline-form bank-details-form" data-form-type="bank_details">
            <h4>Bankverbindung</h4>
            
            <div class="form-group">
                <label for="account_holder">Kontoinhaber *</label>
                <input type="text" id="account_holder" name="account_holder" 
                       value="${prefillData.account_holder || ''}" 
                       placeholder="Max Mustermann" required>
            </div>
            
            <div class="form-group">
                <label for="iban">IBAN *</label>
                                    <input type="text" id="iban" name="iban" 
                           value="${prefillData.iban || ''}" 
                           placeholder="DE89 3704 0044 0532 0130 00" 
                           minlength="22"
                           maxlength="27"
                           oninput="formatIBAN(this)" required>
                <small>Deutsche IBAN (22 Zeichen: DE + 20 Ziffern)</small>
            </div>
            
            <div class="info-box">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="7" stroke="#006CFF" stroke-width="2"/>
                    <path d="M8 4V8M8 10V11" stroke="#006CFF" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <span>Ihre Zahlungsdaten werden sicher verschlüsselt übertragen.</span>
            </div>
            
            <button type="submit" class="form-submit-btn">Weiter zur Zusammenfassung</button>
        </form>
    `;
}

/**
 * 6. Summary Form (Read-only with Edit buttons)
 */
function renderSummaryForm(prefillData = {}, contextMessage = '') {
    const data = prefillData.summary || prefillData;
    
    return `
        <form class="inline-form summary-form" data-form-type="summary">
            <h4>Zusammenfassung</h4>
            
            <div class="summary-section">
                <div class="summary-header">
                    <h5>Ausgewählter Tarif</h5>
                </div>
                <div class="summary-content">
                    <p><strong>${data.tariff?.name || 'N/A'}</strong> (${data.tariff?.provider || 'N/A'})</p>
                    <p>Monatsbeitrag: <strong>${data.tariff?.monthly_premium || 'N/A'} €</strong></p>
                    <p>Versicherungssumme: ${data.tariff?.coverage_amount || 'N/A'} €</p>
                </div>
            </div>
            
            <div class="summary-section">
                <div class="summary-header">
                    <h5>Versicherte Person</h5>
                    <button type="button" class="edit-btn" onclick="editFormSection('personal_data')">Bearbeiten</button>
                </div>
                <div class="summary-content">
                    <p>${data.personal?.firstname || ''} ${data.personal?.lastname || ''}</p>
                    <p>${data.personal?.street || ''} ${data.personal?.housenumber || ''}, ${data.personal?.zipcode || ''} ${data.personal?.city || ''}</p>
                    <p>Geb.: ${data.personal?.birthdate || ''}</p>
                </div>
            </div>
            
            <div class="summary-section">
                <div class="summary-header">
                    <h5>Versicherungsnehmer</h5>
                    <button type="button" class="edit-btn" onclick="editFormSection('policyholder')">Bearbeiten</button>
                </div>
                <div class="summary-content">
                    <p>${data.policyholder?.same_as_insured ? 'Gleich wie versicherte Person' : `${data.policyholder?.firstname || ''} ${data.policyholder?.lastname || ''}`}</p>
                </div>
            </div>
            
            <div class="summary-section">
                <div class="summary-header">
                    <h5>Begünstigter</h5>
                    <button type="button" class="edit-btn" onclick="editFormSection('beneficiary')">Bearbeiten</button>
                </div>
                <div class="summary-content">
                    <p>${data.beneficiary?.type === 'legal_succession' ? 'Gesetzliche Erbfolge' : `${data.beneficiary?.firstname || ''} ${data.beneficiary?.lastname || ''}`}</p>
                </div>
            </div>
            
            <div class="summary-section">
                <div class="summary-header">
                    <h5>Bankverbindung</h5>
                    <button type="button" class="edit-btn" onclick="editFormSection('bank_details')">Bearbeiten</button>
                </div>
                <div class="summary-content">
                    <p>IBAN: ${data.bank?.iban || 'N/A'}</p>
                    <p>Kontoinhaber: ${data.bank?.account_holder || 'N/A'}</p>
                </div>
            </div>
            
            <div class="legal-notes">
                <ul>
                    <li>Mit Ihrer Bestätigung schließen Sie den Versicherungsvertrag verbindlich ab.</li>
                    <li>Sie haben ein 14-tägiges Widerrufsrecht nach Erhalt der Vertragsunterlagen.</li>
                    <li>Der Versicherer prüft Ihren Antrag und sendet Ihnen die Vertragsunterlagen zu.</li>
                </ul>
            </div>
            
            <button type="submit" class="form-submit-btn primary">Verbindlich abschließen</button>
        </form>
    `;
}

// ============================================================================
// Helper Functions for Form Interactions
// ============================================================================

/**
 * Format IBAN with spaces
 */
function formatIBAN(input) {
    let value = input.value.replace(/\s/g, '').toUpperCase();
    if (value.length > 22) value = value.substr(0, 22);
    
    // Format: DE12 3456 7890 1234 5678 90
    let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
    input.value = formatted;
}

/**
 * Toggle policyholder fields visibility
 */
function togglePolicyholderFields(checkbox) {
    const fields = document.getElementById('policyholder-fields');
    if (fields) {
        fields.style.display = checkbox.checked ? 'none' : 'block';
        
        // Update required state of fields
        const inputs = fields.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.required = !checkbox.checked;
        });
    }
}

/**
 * Toggle beneficiary fields visibility
 */
function toggleBeneficiaryFields(radio) {
    const fields = document.getElementById('beneficiary-fields');
    if (fields) {
        fields.style.display = radio.value === 'individual' ? 'block' : 'none';
        
        // Update required state of fields
        const inputs = fields.querySelectorAll('input:not([type="checkbox"])');
        inputs.forEach(input => {
            input.required = radio.value === 'individual';
        });
    }
}

/**
 * Toggle beneficiary address visibility
 */
function toggleBeneficiaryAddress(checkbox) {
    const address = document.getElementById('beneficiary-address');
    if (address) {
        address.style.display = checkbox.checked ? 'none' : 'block';
        
        // Update required state of fields
        const inputs = address.querySelectorAll('input');
        inputs.forEach(input => {
            input.required = !checkbox.checked;
        });
    }
}

/**
 * Edit form section (from summary)
 */
function editFormSection(formType) {
    // Tell LLM to show that form again
    const message = `Ich möchte ${formType} bearbeiten`;
    // This would trigger the normal chat flow
    console.log('Edit section:', formType);
    // TODO: Implement actual edit flow
    alert('Edit-Funktionalität folgt in nächster Phase');
}
