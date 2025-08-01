/**
 * Analytics Dashboard for BuyRoll
 * Advanced data visualization and insights
 */

class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.data = {};
        this.init();
    }

    init() {
        this.setupAnalyticsData();
        this.createAnalyticsDashboard();
        this.setupRealTimeMetrics();
        this.setupInteractiveCharts();
        this.setupDataExport();
    }

    setupAnalyticsData() {
        // Generate sample analytics data
        this.data = {
            overview: {
                totalViews: 12543,
                totalLikes: 2341,
                totalShares: 567,
                totalComments: 891,
                conversionRate: 3.2,
                avgSessionTime: '4:32'
            },
            traffic: this.generateTrafficData(),
            products: this.generateProductData(),
            users: this.generateUserData(),
            revenue: this.generateRevenueData(),
            engagement: this.generateEngagementData()
        };
    }

    generateTrafficData() {
        const days = 30;
        const data = [];
        for (let i = days; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            data.push({
                date: date.toISOString().split('T')[0],
                views: Math.floor(Math.random() * 1000) + 200,
                uniqueVisitors: Math.floor(Math.random() * 500) + 100,
                bounceRate: Math.random() * 0.4 + 0.2
            });
        }
        return data;
    }

    generateProductData() {
        return [
            { name: 'Wireless Headphones', views: 2341, likes: 456, shares: 89, revenue: 12450 },
            { name: 'Smart Watch', views: 1876, likes: 321, shares: 67, revenue: 9870 },
            { name: 'Laptop Stand', views: 1543, likes: 234, shares: 45, revenue: 5670 },
            { name: 'Coffee Maker', views: 1234, likes: 198, shares: 34, revenue: 4560 },
            { name: 'Phone Case', views: 987, likes: 156, shares: 23, revenue: 2340 }
        ];
    }

    generateUserData() {
        return {
            demographics: {
                age: [
                    { range: '18-24', percentage: 25 },
                    { range: '25-34', percentage: 35 },
                    { range: '35-44', percentage: 20 },
                    { range: '45-54', percentage: 15 },
                    { range: '55+', percentage: 5 }
                ],
                gender: [
                    { type: 'Female', percentage: 52 },
                    { type: 'Male', percentage: 45 },
                    { type: 'Other', percentage: 3 }
                ],
                location: [
                    { country: 'United States', percentage: 45 },
                    { country: 'Canada', percentage: 15 },
                    { country: 'United Kingdom', percentage: 12 },
                    { country: 'Germany', percentage: 8 },
                    { country: 'Other', percentage: 20 }
                ]
            }
        };
    }

    generateRevenueData() {
        const months = 12;
        const data = [];
        for (let i = months; i >= 0; i--) {
            const date = new Date();
            date.setMonth(date.getMonth() - i);
            data.push({
                month: date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
                revenue: Math.floor(Math.random() * 50000) + 10000,
                orders: Math.floor(Math.random() * 500) + 100,
                avgOrderValue: Math.floor(Math.random() * 100) + 50
            });
        }
        return data;
    }

    generateEngagementData() {
        return {
            hourly: Array.from({ length: 24 }, (_, i) => ({
                hour: i,
                engagement: Math.random() * 100
            })),
            weekly: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => ({
                day,
                engagement: Math.random() * 100
            }))
        };
    }

    createAnalyticsDashboard() {
        const dashboardContainer = document.createElement('div');
        dashboardContainer.className = 'analytics-dashboard';
        dashboardContainer.innerHTML = `
            <div class="analytics-header">
                <h2 class="analytics-title">Analytics Dashboard</h2>
                <div class="analytics-controls">
                    <select class="analytics-period">
                        <option value="7d">Last 7 days</option>
                        <option value="30d" selected>Last 30 days</option>
                        <option value="90d">Last 90 days</option>
                        <option value="1y">Last year</option>
                    </select>
                    <button class="btn btn-outline btn-sm export-data">
                        <i class="fas fa-download mr-2"></i>Export
                    </button>
                </div>
            </div>

            <div class="analytics-overview">
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-eye"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-value" data-count="${this.data.overview.totalViews}">0</div>
                        <div class="metric-label">Total Views</div>
                        <div class="metric-change positive">+12.5%</div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-heart"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-value" data-count="${this.data.overview.totalLikes}">0</div>
                        <div class="metric-label">Total Likes</div>
                        <div class="metric-change positive">+8.3%</div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-share"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-value" data-count="${this.data.overview.totalShares}">0</div>
                        <div class="metric-label">Total Shares</div>
                        <div class="metric-change positive">+15.7%</div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-percentage"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-value">${this.data.overview.conversionRate}%</div>
                        <div class="metric-label">Conversion Rate</div>
                        <div class="metric-change negative">-2.1%</div>
                    </div>
                </div>
            </div>

            <div class="analytics-charts">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3>Traffic Overview</h3>
                        <div class="chart-legend">
                            <span class="legend-item">
                                <span class="legend-color" style="background: #3b82f6;"></span>
                                Views
                            </span>
                            <span class="legend-item">
                                <span class="legend-color" style="background: #10b981;"></span>
                                Unique Visitors
                            </span>
                        </div>
                    </div>
                    <canvas id="trafficChart" width="400" height="200"></canvas>
                </div>

                <div class="chart-container">
                    <div class="chart-header">
                        <h3>Top Products</h3>
                    </div>
                    <div class="products-chart" id="productsChart">
                        <!-- Products will be populated here -->
                    </div>
                </div>

                <div class="chart-container">
                    <div class="chart-header">
                        <h3>User Demographics</h3>
                    </div>
                    <canvas id="demographicsChart" width="300" height="300"></canvas>
                </div>

                <div class="chart-container">
                    <div class="chart-header">
                        <h3>Revenue Trend</h3>
                    </div>
                    <canvas id="revenueChart" width="400" height="200"></canvas>
                </div>
            </div>

            <div class="analytics-insights">
                <div class="insight-card">
                    <div class="insight-icon">
                        <i class="fas fa-lightbulb"></i>
                    </div>
                    <div class="insight-content">
                        <h4>Key Insight</h4>
                        <p>Your engagement rate is 23% higher on weekends. Consider scheduling more content during these times.</p>
                    </div>
                </div>

                <div class="insight-card">
                    <div class="insight-icon">
                        <i class="fas fa-trending-up"></i>
                    </div>
                    <div class="insight-content">
                        <h4>Growth Opportunity</h4>
                        <p>Electronics category shows 45% higher conversion rates. Focus marketing efforts on similar products.</p>
                    </div>
                </div>

                <div class="insight-card">
                    <div class="insight-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="insight-content">
                        <h4>Action Required</h4>
                        <p>Bounce rate increased by 12% this week. Review page load times and content relevance.</p>
                    </div>
                </div>
            </div>
        `;

        // Add to dashboard if it exists, otherwise create a modal
        const dashboardContent = document.querySelector('.dashboard-content .container');
        if (dashboardContent) {
            dashboardContent.appendChild(dashboardContainer);
        } else {
            this.createAnalyticsModal(dashboardContainer);
        }

        this.setupAnalyticsEvents(dashboardContainer);
        this.renderCharts();
    }

    createAnalyticsModal(content) {
        const modal = document.createElement('div');
        modal.className = 'analytics-modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Analytics Dashboard</h3>
                    <button class="modal-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${content.innerHTML}
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Setup modal events
        const closeBtn = modal.querySelector('.modal-close');
        const backdrop = modal.querySelector('.modal-backdrop');
        [closeBtn, backdrop].forEach(el => {
            el.addEventListener('click', () => {
                modal.remove();
            });
        });

        // Add analytics button to navigation
        this.addAnalyticsButton(modal);
    }

    addAnalyticsButton(modal) {
        const navActions = document.querySelector('.nav .flex.items-center.space-x-4');
        if (navActions) {
            const analyticsBtn = document.createElement('button');
            analyticsBtn.className = 'p-2 text-gray-600 hover:text-primary-800 transition';
            analyticsBtn.setAttribute('data-tooltip', 'Analytics');
            analyticsBtn.innerHTML = '<i class="fas fa-chart-bar text-lg"></i>';
            
            analyticsBtn.addEventListener('click', () => {
                modal.classList.add('active');
                document.body.classList.add('modal-open');
            });

            navActions.insertBefore(analyticsBtn, navActions.firstChild);
        }
    }

    setupAnalyticsEvents(container) {
        // Period selector
        const periodSelect = container.querySelector('.analytics-period');
        periodSelect.addEventListener('change', (e) => {
            this.updateAnalyticsPeriod(e.target.value);
        });

        // Export button
        const exportBtn = container.querySelector('.export-data');
        exportBtn.addEventListener('click', () => {
            this.exportAnalyticsData();
        });

        // Animate counters
        this.animateCounters(container);
    }

    renderCharts() {
        this.renderTrafficChart();
        this.renderProductsChart();
        this.renderDemographicsChart();
        this.renderRevenueChart();
    }

    renderTrafficChart() {
        const canvas = document.getElementById('trafficChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.data.traffic.slice(-7); // Last 7 days

        this.drawLineChart(ctx, data, canvas.width, canvas.height, [
            { key: 'views', color: '#3b82f6', label: 'Views' },
            { key: 'uniqueVisitors', color: '#10b981', label: 'Unique Visitors' }
        ]);
    }

    renderProductsChart() {
        const container = document.getElementById('productsChart');
        if (!container) return;

        const maxValue = Math.max(...this.data.products.map(p => p.views));
        
        container.innerHTML = this.data.products.map(product => `
            <div class="product-bar">
                <div class="product-info">
                    <span class="product-name">${product.name}</span>
                    <span class="product-value">${product.views.toLocaleString()}</span>
                </div>
                <div class="product-bar-container">
                    <div class="product-bar-fill" style="width: ${(product.views / maxValue) * 100}%"></div>
                </div>
            </div>
        `).join('');
    }

    renderDemographicsChart() {
        const canvas = document.getElementById('demographicsChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.data.users.demographics.age;

        this.drawPieChart(ctx, data, canvas.width, canvas.height);
    }

    renderRevenueChart() {
        const canvas = document.getElementById('revenueChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.data.revenue.slice(-6); // Last 6 months

        this.drawLineChart(ctx, data, canvas.width, canvas.height, [
            { key: 'revenue', color: '#8b5cf6', label: 'Revenue' }
        ]);
    }

    drawLineChart(ctx, data, width, height, series) {
        const padding = 40;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        // Draw grid
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;

        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }

        // Draw data lines
        series.forEach(serie => {
            const values = data.map(d => d[serie.key]);
            const maxValue = Math.max(...values);
            const minValue = Math.min(...values);
            const range = maxValue - minValue || 1;

            ctx.strokeStyle = serie.color;
            ctx.lineWidth = 3;
            ctx.beginPath();

            values.forEach((value, i) => {
                const x = padding + (chartWidth / (values.length - 1)) * i;
                const y = padding + chartHeight - ((value - minValue) / range) * chartHeight;

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });

            ctx.stroke();

            // Draw points
            ctx.fillStyle = serie.color;
            values.forEach((value, i) => {
                const x = padding + (chartWidth / (values.length - 1)) * i;
                const y = padding + chartHeight - ((value - minValue) / range) * chartHeight;
                
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, 2 * Math.PI);
                ctx.fill();
            });
        });
    }

    drawPieChart(ctx, data, width, height) {
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 2 - 20;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        let currentAngle = -Math.PI / 2;
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

        data.forEach((item, index) => {
            const sliceAngle = (item.percentage / 100) * 2 * Math.PI;
            
            // Draw slice
            ctx.fillStyle = colors[index % colors.length];
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fill();

            // Draw label
            const labelAngle = currentAngle + sliceAngle / 2;
            const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
            const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);
            
            ctx.fillStyle = '#ffffff';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(`${item.percentage}%`, labelX, labelY);

            currentAngle += sliceAngle;
        });
    }

    animateCounters(container) {
        const counters = container.querySelectorAll('[data-count]');
        
        counters.forEach(counter => {
            const target = parseInt(counter.dataset.count);
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;
            
            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                counter.textContent = Math.floor(current).toLocaleString();
            }, 16);
        });
    }

    setupRealTimeMetrics() {
        // Update metrics every 30 seconds
        setInterval(() => {
            this.updateRealTimeMetrics();
        }, 30000);
    }

    updateRealTimeMetrics() {
        // Simulate real-time metric updates
        const metrics = document.querySelectorAll('.metric-value[data-count]');
        metrics.forEach(metric => {
            const currentValue = parseInt(metric.dataset.count);
            const change = Math.floor(Math.random() * 10) - 5; // Random change
            const newValue = Math.max(0, currentValue + change);
            
            metric.dataset.count = newValue;
            metric.textContent = newValue.toLocaleString();
            
            // Add update animation
            metric.classList.add('metric-updated');
            setTimeout(() => {
                metric.classList.remove('metric-updated');
            }, 1000);
        });
    }

    setupInteractiveCharts() {
        // Add hover effects and tooltips to charts
        const canvases = document.querySelectorAll('canvas');
        canvases.forEach(canvas => {
            canvas.addEventListener('mousemove', (e) => {
                this.handleChartHover(e, canvas);
            });
        });
    }

    handleChartHover(event, canvas) {
        // Add tooltip functionality for charts
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // Show tooltip with data point information
        this.showChartTooltip(x, y, canvas);
    }

    showChartTooltip(x, y, canvas) {
        // Implementation for chart tooltips
        // This would show detailed information about the data point
    }

    updateAnalyticsPeriod(period) {
        console.log(`Updating analytics for period: ${period}`);
        
        // Update data based on selected period
        switch (period) {
            case '7d':
                this.data.traffic = this.data.traffic.slice(-7);
                break;
            case '30d':
                this.data.traffic = this.data.traffic.slice(-30);
                break;
            case '90d':
                // Generate more data for 90 days
                break;
            case '1y':
                // Generate yearly data
                break;
        }
        
        // Re-render charts
        this.renderCharts();
        
        // Show update notification
        if (window.BuyRollApp) {
            const app = new window.BuyRollApp();
            app.showNotification(`Analytics updated for ${period}`, 'success');
        }
    }

    setupDataExport() {
        // Setup data export functionality
    }

    exportAnalyticsData() {
        const exportData = {
            overview: this.data.overview,
            traffic: this.data.traffic,
            products: this.data.products,
            users: this.data.users,
            revenue: this.data.revenue,
            exportDate: new Date().toISOString()
        };

        // Create and download JSON file
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `buyroll-analytics-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
        
        if (window.BuyRollApp) {
            const app = new window.BuyRollApp();
            app.showNotification('Analytics data exported successfully', 'success');
        }
    }
}

// Initialize analytics dashboard
document.addEventListener('DOMContentLoaded', () => {
    window.analyticsDashboard = new AnalyticsDashboard();
});

// Export for use in other modules
window.AnalyticsDashboard = AnalyticsDashboard;