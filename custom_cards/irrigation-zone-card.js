// Irrigation Zone Control Card for Home Assistant Dashboard

class IrrigationZoneCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    setConfig(config) {
        if (!config.addon_url) {
            throw new Error('You need to define addon_url');
        }
        if (!config.zone_id) {
            throw new Error('You need to define zone_id');
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
                    position: relative;
                    overflow: hidden;
                }
                .card.watering {
                    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                    color: white;
                }
                .card.watering::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                    animation: shimmer 2s infinite;
                }
                @keyframes shimmer {
                    0% { left: -100%; }
                    100% { left: 100%; }
                }
                .header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 16px;
                }
                .title-section {
                    display: flex;
                    align-items: center;
                }
                .title-section ha-icon {
                    margin-right: 8px;
                    color: var(--primary-color);
                }
                .card.watering .title-section ha-icon {
                    color: white;
                }
                .title {
                    font-size: 1.1em;
                    font-weight: 500;
                    color: var(--primary-text-color);
                }
                .card.watering .title {
                    color: white;
                }
                .status-badge {
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 0.8em;
                    font-weight: 500;
                }
                .status-active {
                    background: var(--success-color);
                    color: white;
                }
                .status-inactive {
                    background: var(--disabled-color);
                    color: var(--secondary-text-color);
                }
                .zone-info {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 12px;
                    margin-bottom: 16px;
                }
                .info-item {
                    text-align: center;
                }
                .info-value {
                    font-size: 1.2em;
                    font-weight: bold;
                    color: var(--primary-color);
                }
                .card.watering .info-value {
                    color: white;
                }
                .info-label {
                    font-size: 0.8em;
                    color: var(--secondary-text-color);
                    margin-top: 2px;
                }
                .card.watering .info-label {
                    color: rgba(255,255,255,0.8);
                }
                .controls {
                    display: flex;
                    gap: 8px;
                    align-items: center;
                }
                .duration-input {
                    flex: 1;
                    padding: 8px;
                    border: 1px solid var(--divider-color);
                    border-radius: 6px;
                    background: var(--secondary-background-color);
                    color: var(--primary-text-color);
                    font-size: 0.9em;
                }
                .card.watering .duration-input {
                    background: rgba(255,255,255,0.2);
                    border-color: rgba(255,255,255,0.3);
                    color: white;
                }
                .card.watering .duration-input::placeholder {
                    color: rgba(255,255,255,0.7);
                }
                .btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.9em;
                    font-weight: 500;
                    transition: all 0.2s;
                    display: flex;
                    align-items: center;
                    gap: 4px;
                }
                .btn-water {
                    background: var(--primary-color);
                    color: white;
                    flex: 2;
                }
                .btn-water:hover {
                    background: var(--primary-color);
                    opacity: 0.8;
                    transform: translateY(-1px);
                }
                .btn-stop {
                    background: var(--error-color);
                    color: white;
                    flex: 2;
                }
                .btn-stop:hover {
                    background: var(--error-color);
                    opacity: 0.8;
                }
                .btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                .watering-progress {
                    margin-top: 12px;
                    padding: 8px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 6px;
                    text-align: center;
                    font-size: 0.9em;
                }
                .error {
                    color: var(--error-color);
                    text-align: center;
                    padding: 8px;
                    font-size: 0.9em;
                }
            </style>
            <div class="card" id="main-card">
                <div class="header">
                    <div class="title-section">
                        <ha-icon icon="mdi:sprinkler-variant"></ha-icon>
                        <div class="title">${this.config.title || 'Irrigation Zone'}</div>
                    </div>
                    <div class="status-badge" id="status-badge">Loading...</div>
                </div>
                <div id="content">
                    <div class="error">Loading zone information...</div>
                </div>
            </div>
        `;
    }

    async updateCard() {
        if (!this.config.addon_url || !this.config.zone_id) return;

        try {
            // Get zone information
            const zonesResponse = await fetch(`${this.config.addon_url}/api/zones`);
            const zones = await zonesResponse.json();
            const zone = zones.find(z => z.id === this.config.zone_id);

            if (!zone) {
                throw new Error('Zone not found');
            }

            // Get system status
            const statusResponse = await fetch(`${this.config.addon_url}/api/status`);
            const status = await statusResponse.json();
            
            const isWatering = status.active_zones.includes(this.config.zone_id);
            
            this.updateDisplay(zone, isWatering);
            
        } catch (error) {
            console.error('Error updating irrigation zone card:', error);
            const content = this.shadowRoot.getElementById('content');
            content.innerHTML = `<div class="error">Error loading zone information</div>`;
        }
    }

    updateDisplay(zone, isWatering) {
        const card = this.shadowRoot.getElementById('main-card');
        const statusBadge = this.shadowRoot.getElementById('status-badge');
        const content = this.shadowRoot.getElementById('content');

        // Update card appearance
        if (isWatering) {
            card.classList.add('watering');
            statusBadge.textContent = 'WATERING';
            statusBadge.className = 'status-badge status-active';
        } else {
            card.classList.remove('watering');
            statusBadge.textContent = zone.active ? 'READY' : 'INACTIVE';
            statusBadge.className = `status-badge ${zone.active ? 'status-active' : 'status-inactive'}`;
        }

        // Update content
        content.innerHTML = `
            <div class="zone-info">
                <div class="info-item">
                    <div class="info-value">${zone.plant_count}</div>
                    <div class="info-label">Plants</div>
                </div>
                <div class="info-item">
                    <div class="info-value">${zone.flow_rate}L/h</div>
                    <div class="info-label">Flow Rate</div>
                </div>
            </div>
            
            ${isWatering ? `
                <div class="watering-progress">
                    <ha-icon icon="mdi:water"></ha-icon>
                    Currently watering...
                </div>
                <div class="controls">
                    <button class="btn btn-stop" onclick="this.stopWatering()">
                        <ha-icon icon="mdi:stop"></ha-icon>
                        Stop
                    </button>
                </div>
            ` : `
                <div class="controls">
                    <input type="number" class="duration-input" id="duration-input" 
                           value="${this.config.default_duration || 2}" 
                           min="1" max="60" placeholder="Minutes">
                    <button class="btn btn-water" onclick="this.startWatering()" 
                            ${!zone.active ? 'disabled' : ''}>
                        <ha-icon icon="mdi:play"></ha-icon>
                        Water
                    </button>
                </div>
            `}
        `;
    }

    async startWatering() {
        const durationInput = this.shadowRoot.getElementById('duration-input');
        const duration = parseInt(durationInput.value) || 2;

        try {
            const response = await fetch(`${this.config.addon_url}/api/manual-water`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    zone_id: this.config.zone_id,
                    duration: duration
                })
            });

            const result = await response.json();
            if (result.success) {
                // Update display immediately
                setTimeout(() => this.updateCard(), 500);
            } else {
                console.error('Failed to start watering:', result.error);
            }
        } catch (error) {
            console.error('Error starting watering:', error);
        }
    }

    async stopWatering() {
        // This would require an API endpoint to stop watering
        // For now, just refresh the card
        this.updateCard();
    }

    getCardSize() {
        return 2;
    }
}

customElements.define('irrigation-zone-card', IrrigationZoneCard);

// Register the card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
    type: 'irrigation-zone-card',
    name: 'Irrigation Zone Card',
    description: 'Control individual irrigation zones'
});