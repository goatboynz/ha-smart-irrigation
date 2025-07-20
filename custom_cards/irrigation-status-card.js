// Irrigation Status Card for Home Assistant Dashboard

class IrrigationStatusCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    setConfig(config) {
        if (!config.addon_url) {
            throw new Error('You need to define addon_url');
        }
        this.config = config;
        this.render();
    }

    set hass(hass) {
        this._hass = hass;
        this.updateCard();
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                .card {
                    padding: 16px;
                    background: var(--ha-card-background, var(--card-background-color, white));
                    border-radius: var(--ha-card-border-radius, 12px);
                    box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
                }
                .header {
                    display: flex;
                    align-items: center;
                    margin-bottom: 16px;
                }
                .header ha-icon {
                    margin-right: 8px;
                    color: var(--primary-color);
                }
                .title {
                    font-size: 1.2em;
                    font-weight: 500;
                    color: var(--primary-text-color);
                }
                .status-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                    gap: 12px;
                    margin-bottom: 16px;
                }
                .status-item {
                    text-align: center;
                    padding: 12px;
                    background: var(--secondary-background-color);
                    border-radius: 8px;
                }
                .status-value {
                    font-size: 1.5em;
                    font-weight: bold;
                    color: var(--primary-color);
                }
                .status-label {
                    font-size: 0.9em;
                    color: var(--secondary-text-color);
                    margin-top: 4px;
                }
                .active-zones {
                    margin-top: 16px;
                }
                .zone-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 8px 12px;
                    margin: 4px 0;
                    background: var(--primary-color);
                    color: white;
                    border-radius: 6px;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.7; }
                    100% { opacity: 1; }
                }
                .controls {
                    display: flex;
                    gap: 8px;
                    margin-top: 16px;
                }
                .btn {
                    flex: 1;
                    padding: 8px 16px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.9em;
                    transition: background-color 0.2s;
                }
                .btn-primary {
                    background: var(--primary-color);
                    color: white;
                }
                .btn-primary:hover {
                    background: var(--primary-color);
                    opacity: 0.8;
                }
                .btn-secondary {
                    background: var(--secondary-background-color);
                    color: var(--primary-text-color);
                }
                .error {
                    color: var(--error-color);
                    text-align: center;
                    padding: 16px;
                }
            </style>
            <div class="card">
                <div class="header">
                    <ha-icon icon="mdi:sprinkler"></ha-icon>
                    <div class="title">${this.config.title || 'Irrigation System'}</div>
                </div>
                <div id="content">
                    <div class="error">Loading...</div>
                </div>
            </div>
        `;
    }

    async updateCard() {
        if (!this.config.addon_url) return;

        try {
            const response = await fetch(`${this.config.addon_url}/api/status`);
            const status = await response.json();
            
            const content = this.shadowRoot.getElementById('content');
            content.innerHTML = `
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-value">${status.active_zones.length}</div>
                        <div class="status-label">Active Zones</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">${status.water_usage_today.toFixed(1)}L</div>
                        <div class="status-label">Water Today</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">${status.system_active ? 'ON' : 'OFF'}</div>
                        <div class="status-label">System Status</div>
                    </div>
                </div>
                
                ${status.active_zones.length > 0 ? `
                    <div class="active-zones">
                        <h4>Active Watering</h4>
                        ${status.active_zones.map(zone => `
                            <div class="zone-item">
                                <span>Zone ${zone}</span>
                                <span>Watering...</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                <div class="controls">
                    <button class="btn btn-primary" onclick="window.open('${this.config.addon_url}', '_blank')">
                        Open Controller
                    </button>
                    <button class="btn btn-secondary" onclick="this.refreshStatus()">
                        Refresh
                    </button>
                </div>
            `;
        } catch (error) {
            const content = this.shadowRoot.getElementById('content');
            content.innerHTML = `<div class="error">Error loading irrigation status</div>`;
        }
    }

    refreshStatus() {
        this.updateCard();
    }

    getCardSize() {
        return 3;
    }
}

customElements.define('irrigation-status-card', IrrigationStatusCard);

// Register the card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
    type: 'irrigation-status-card',
    name: 'Irrigation Status Card',
    description: 'Display irrigation system status and controls'
});